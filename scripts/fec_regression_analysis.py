from __future__ import annotations

import argparse
import math
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


PARTIES = ["Democrat", "Republican"]
EXPECTED_CATEGORIES = [
    "Individual IE Committee",
    "Party Committee",
    "Super PAC",
    "Traditional PAC",
    "Other/Unknown",
]
PRE_LABEL = "Pre-Citizens United (2001-2010)"
POST_LABEL = "Post-Citizens United (2011-2020)"


def slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", str(value).strip().lower()).strip("_")
    return cleaned or "value"


def two_sided_normal_p(z_value: float) -> float:
    if not np.isfinite(z_value):
        return np.nan
    return math.erfc(abs(float(z_value)) / math.sqrt(2.0))


def format_p_value(p_value: float) -> str:
    if not np.isfinite(p_value):
        return ""
    if p_value < 0.001:
        return "<0.001"
    return f"{p_value:.3f}"


def significance_stars(p_value: float) -> str:
    if not np.isfinite(p_value):
        return ""
    if p_value < 0.001:
        return "***"
    if p_value < 0.01:
        return "**"
    if p_value < 0.05:
        return "*"
    if p_value < 0.10:
        return "+"
    return ""


@dataclass
class ModelResult:
    coefficients: pd.DataFrame
    summary: dict


def fit_ols(
    frame: pd.DataFrame,
    outcome: str,
    predictors: Iterable[str],
    *,
    model_name: str,
    dataset_name: str,
    outcome_label: str,
    bootstrap_reps: int = 2000,
    seed: int = 2026,
) -> ModelResult:
    """Fit OLS with HC1 robust standard errors and optional bootstrap CIs."""

    predictors = list(predictors)
    model_frame = frame[[outcome] + predictors].replace([np.inf, -np.inf], np.nan).dropna()

    kept_predictors = []
    for col in predictors:
        if model_frame[col].nunique(dropna=True) > 1:
            kept_predictors.append(col)

    y = model_frame[outcome].astype(float).to_numpy()
    x = model_frame[kept_predictors].astype(float).copy()
    x.insert(0, "const", 1.0)
    x_names = list(x.columns)
    x_mat = x.to_numpy(dtype=float)

    n_obs = len(y)
    n_params = x_mat.shape[1]
    if n_obs == 0:
        raise ValueError(f"No usable observations for {dataset_name} / {model_name}")

    xtx_inv = np.linalg.pinv(x_mat.T @ x_mat)
    beta = xtx_inv @ x_mat.T @ y
    fitted = x_mat @ beta
    residuals = y - fitted

    sse = float(np.sum(residuals ** 2))
    tss = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - sse / tss if tss > 0 else np.nan
    adj_r2 = (
        1.0 - (1.0 - r2) * (n_obs - 1) / (n_obs - n_params)
        if np.isfinite(r2) and n_obs > n_params
        else np.nan
    )

    meat = x_mat.T @ ((residuals[:, None] ** 2) * x_mat)
    hc1_scale = n_obs / (n_obs - n_params) if n_obs > n_params else np.nan
    robust_cov = hc1_scale * (xtx_inv @ meat @ xtx_inv) if np.isfinite(hc1_scale) else np.full((n_params, n_params), np.nan)
    robust_se = np.sqrt(np.maximum(np.diag(robust_cov), 0))

    bootstrap_low = np.full(n_params, np.nan)
    bootstrap_high = np.full(n_params, np.nan)
    if bootstrap_reps > 0 and n_obs > n_params:
        rng = np.random.default_rng(seed)
        draws = np.full((bootstrap_reps, n_params), np.nan)
        for i in range(bootstrap_reps):
            idx = rng.integers(0, n_obs, n_obs)
            xb = x_mat[idx, :]
            yb = y[idx]
            draws[i, :] = np.linalg.pinv(xb.T @ xb) @ xb.T @ yb
        bootstrap_low = np.nanpercentile(draws, 2.5, axis=0)
        bootstrap_high = np.nanpercentile(draws, 97.5, axis=0)

    rows = []
    for idx, term in enumerate(x_names):
        coef = float(beta[idx])
        se = float(robust_se[idx]) if np.isfinite(robust_se[idx]) else np.nan
        z_value = coef / se if se and np.isfinite(se) else np.nan
        p_value = two_sided_normal_p(z_value)
        rows.append(
            {
                "dataset": dataset_name,
                "model": model_name,
                "outcome": outcome_label,
                "term": term,
                "coefficient": coef,
                "robust_se": se,
                "z_value": z_value,
                "p_value": p_value,
                "stars": significance_stars(p_value),
                "bootstrap_ci_low": float(bootstrap_low[idx]) if np.isfinite(bootstrap_low[idx]) else np.nan,
                "bootstrap_ci_high": float(bootstrap_high[idx]) if np.isfinite(bootstrap_high[idx]) else np.nan,
                "n": n_obs,
                "r2": r2,
                "adj_r2": adj_r2,
                "dropped_constant_predictors": "; ".join(sorted(set(predictors) - set(kept_predictors))),
            }
        )

    return ModelResult(
        coefficients=pd.DataFrame(rows),
        summary={
            "dataset": dataset_name,
            "model": model_name,
            "outcome": outcome_label,
            "n": n_obs,
            "parameters": n_params,
            "r2": r2,
            "adj_r2": adj_r2,
            "predictors": "; ".join(kept_predictors),
            "dropped_constant_predictors": "; ".join(sorted(set(predictors) - set(kept_predictors))),
        },
    )


def load_processed_dataset(data_dir: Path, dataset_name: str) -> pd.DataFrame:
    path = data_dir / f"{dataset_name.lower()}_processed.pkl"
    if not path.exists():
        raise FileNotFoundError(f"Missing processed dataset: {path}")

    with open(path, "rb") as f:
        data = pickle.load(f)

    data = data.copy()
    data["TRANSACTION_AMT"] = pd.to_numeric(data["TRANSACTION_AMT"], errors="coerce").fillna(0)
    data = data[data["BENEFITING_PARTY"].isin(PARTIES)].copy()

    if "CAND_OFFICE" not in data.columns:
        if dataset_name.lower() == "senate":
            data["CAND_OFFICE"] = "S"
        elif dataset_name.lower() == "presidential":
            data["CAND_OFFICE"] = "P"
        else:
            data["CAND_OFFICE"] = "Unknown"

    if "COMMITTEE_CATEGORY" not in data.columns:
        data["COMMITTEE_CATEGORY"] = "Other/Unknown"

    # Keep the regression scope aligned with the paper's source categories.
    # Candidate committees are not treated as independent-expenditure sources.
    data = data[data["COMMITTEE_CATEGORY"] != "Candidate Committee"].copy()

    return data


def add_common_design_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["post_cu"] = (out["CYCLE_END_YEAR"].astype(int) > 2010).astype(int)
    out["republican"] = (out["BENEFITING_PARTY"] == "Republican").astype(int)
    out["presidential_office"] = (out["CAND_OFFICE"] == "P").astype(int)
    out["presidential_cycle"] = (out["CYCLE_END_YEAR"].astype(int) % 4 == 0).astype(int)
    out["cycle_index"] = (out["CYCLE_END_YEAR"].astype(int) - int(out["CYCLE_END_YEAR"].astype(int).min())) / 2.0
    return out


def make_party_office_panel(data: pd.DataFrame) -> pd.DataFrame:
    cycles = sorted(data["CYCLE_END_YEAR"].dropna().astype(int).unique())
    offices = sorted(data["CAND_OFFICE"].dropna().unique())
    index = pd.MultiIndex.from_product(
        [cycles, PARTIES, offices],
        names=["CYCLE_END_YEAR", "BENEFITING_PARTY", "CAND_OFFICE"],
    )

    grouped = (
        data.groupby(["CYCLE_END_YEAR", "BENEFITING_PARTY", "CAND_OFFICE"])
        .agg(
            total_amount=("TRANSACTION_AMT", "sum"),
            num_transactions=("TRANSACTION_AMT", "size"),
            unique_committees=("CMTE_ID", "nunique"),
        )
        .reindex(index)
        .fillna(0)
        .reset_index()
    )
    grouped["log_total_ie"] = np.log1p(grouped["total_amount"])
    grouped["log_num_transactions"] = np.log1p(grouped["num_transactions"])
    grouped = add_common_design_columns(grouped)
    grouped["post_x_republican"] = grouped["post_cu"] * grouped["republican"]
    return grouped


def make_source_panel(data: pd.DataFrame) -> pd.DataFrame:
    cycles = sorted(data["CYCLE_END_YEAR"].dropna().astype(int).unique())
    offices = sorted(data["CAND_OFFICE"].dropna().unique())
    observed_categories = sorted(data["COMMITTEE_CATEGORY"].dropna().unique())
    categories = [c for c in EXPECTED_CATEGORIES if c in set(EXPECTED_CATEGORIES + observed_categories)]
    for c in observed_categories:
        if c not in categories:
            categories.append(c)

    index = pd.MultiIndex.from_product(
        [cycles, PARTIES, offices, categories],
        names=["CYCLE_END_YEAR", "BENEFITING_PARTY", "CAND_OFFICE", "COMMITTEE_CATEGORY"],
    )

    grouped = (
        data.groupby(["CYCLE_END_YEAR", "BENEFITING_PARTY", "CAND_OFFICE", "COMMITTEE_CATEGORY"])
        .agg(
            total_amount=("TRANSACTION_AMT", "sum"),
            num_transactions=("TRANSACTION_AMT", "size"),
            unique_committees=("CMTE_ID", "nunique"),
        )
        .reindex(index)
        .fillna(0)
        .reset_index()
    )

    totals = (
        grouped.groupby(["CYCLE_END_YEAR", "BENEFITING_PARTY", "CAND_OFFICE"])["total_amount"]
        .sum()
        .rename("party_office_cycle_total")
        .reset_index()
    )
    grouped = grouped.merge(totals, on=["CYCLE_END_YEAR", "BENEFITING_PARTY", "CAND_OFFICE"], how="left")
    grouped["source_share"] = np.where(
        grouped["party_office_cycle_total"] > 0,
        grouped["total_amount"] / grouped["party_office_cycle_total"],
        0.0,
    )
    grouped["log_total_ie"] = np.log1p(grouped["total_amount"])
    grouped = add_common_design_columns(grouped)
    grouped["super_pac"] = (grouped["COMMITTEE_CATEGORY"] == "Super PAC").astype(int)

    base_category = "Party Committee" if "Party Committee" in categories else categories[0]
    category_terms = []
    interaction_terms = []
    for category in categories:
        interaction_col = f"post_x_{slug(category)}"
        category_indicator = (grouped["COMMITTEE_CATEGORY"] == category).astype(int)
        grouped[interaction_col] = grouped["post_cu"] * category_indicator
        interaction_terms.append(interaction_col)

        if category == base_category:
            continue
        category_col = f"category_{slug(category)}"
        grouped[category_col] = category_indicator
        category_terms.append(category_col)

    grouped.attrs["base_category"] = base_category
    grouped.attrs["category_terms"] = category_terms
    grouped.attrs["interaction_terms"] = interaction_terms
    return grouped


def run_models_for_dataset(
    data: pd.DataFrame,
    dataset_name: str,
    *,
    bootstrap_reps: int,
) -> tuple[list[pd.DataFrame], list[dict], dict[str, pd.DataFrame]]:
    coefficient_tables: list[pd.DataFrame] = []
    summaries: list[dict] = []
    panels: dict[str, pd.DataFrame] = {}

    party_panel = make_party_office_panel(data)
    source_panel = make_source_panel(data)
    panels["party_office_panel"] = party_panel
    panels["source_panel"] = source_panel

    party_predictors = [
        "post_cu",
        "republican",
        "post_x_republican",
        "presidential_office",
        "presidential_cycle",
    ]
    party_result = fit_ols(
        party_panel,
        "log_total_ie",
        party_predictors,
        model_name="party_growth_baseline",
        dataset_name=dataset_name,
        outcome_label="log(1 + total IE dollars), cycle-party-office panel",
        bootstrap_reps=bootstrap_reps,
    )
    coefficient_tables.append(party_result.coefficients)
    summaries.append(party_result.summary)

    trend_result = fit_ols(
        party_panel,
        "log_total_ie",
        party_predictors + ["cycle_index"],
        model_name="party_growth_with_linear_trend",
        dataset_name=dataset_name,
        outcome_label="log(1 + total IE dollars), cycle-party-office panel",
        bootstrap_reps=bootstrap_reps,
    )
    coefficient_tables.append(trend_result.coefficients)
    summaries.append(trend_result.summary)

    source_predictors = (
        ["republican", "presidential_office", "presidential_cycle"]
        + source_panel.attrs["category_terms"]
        + source_panel.attrs["interaction_terms"]
    )
    source_result = fit_ols(
        source_panel,
        "source_share",
        source_predictors,
        model_name=f"source_share_shift_category_specific_post_base_{slug(source_panel.attrs['base_category'])}",
        dataset_name=dataset_name,
        outcome_label="committee category share of cycle-party-office IE dollars",
        bootstrap_reps=bootstrap_reps,
    )
    coefficient_tables.append(source_result.coefficients)
    summaries.append(source_result.summary)

    post_superpac = source_panel[
        (source_panel["post_cu"] == 1) & (source_panel["COMMITTEE_CATEGORY"] == "Super PAC")
    ].copy()
    if len(post_superpac) > 0 and post_superpac["total_amount"].sum() > 0:
        superpac_result = fit_ols(
            post_superpac,
            "log_total_ie",
            ["republican", "presidential_office", "presidential_cycle", "cycle_index"],
            model_name="post_cu_superpac_partisan_advantage",
            dataset_name=dataset_name,
            outcome_label="log(1 + Super PAC IE dollars), post-CU cycle-party-office panel",
            bootstrap_reps=bootstrap_reps,
        )
        coefficient_tables.append(superpac_result.coefficients)
        summaries.append(superpac_result.summary)

    return coefficient_tables, summaries, panels


def add_interpretation_columns(coefficients: pd.DataFrame) -> pd.DataFrame:
    out = coefficients.copy()
    out["log_model_percent_change"] = np.where(
        out["outcome"].str.startswith("log("),
        (np.exp(out["coefficient"]) - 1.0) * 100.0,
        np.nan,
    )
    out["share_model_percentage_points"] = np.where(
        out["outcome"].str.contains("share", case=False, regex=False),
        out["coefficient"] * 100.0,
        np.nan,
    )
    return out


def key_term_label(term: str) -> str:
    labels = {
        "post_cu": "Post-Citizens United change",
        "republican": "Republican vs. Democratic baseline",
        "post_x_republican": "Republican differential post-CU change",
        "post_x_party_committee": "Party committee post-CU source-share shift",
        "post_x_super_pac": "Super PAC post-CU source-share shift",
        "post_x_traditional_pac": "Traditional PAC post-CU source-share shift",
        "post_x_other_unknown": "Other/Unknown post-CU source-share shift",
        "post_x_individual_ie_committee": "Individual IE committee post-CU source-share shift",
        "cycle_index": "Linear election-cycle trend",
    }
    return labels.get(term, term.replace("_", " "))


def model_label(model: str) -> str:
    labels = {
        "party_growth_baseline": "Party Growth Model",
        "party_growth_with_linear_trend": "Party Growth Model With Linear Trend",
        "source_share_shift_category_specific_post_base_party_committee": "Source-Share Shift Model",
        "post_cu_superpac_partisan_advantage": "Post-CU Super PAC Partisan Model",
    }
    return labels.get(model, model.replace("_", " ").title())


def make_markdown_report(coefficients: pd.DataFrame, summaries: pd.DataFrame) -> str:
    key_terms = {
        "party_growth_baseline": ["post_cu", "post_x_republican"],
        "party_growth_with_linear_trend": ["post_cu", "post_x_republican", "cycle_index"],
        "source_share_shift_category_specific_post_base_party_committee": [
            "post_x_party_committee",
            "post_x_super_pac",
            "post_x_traditional_pac",
            "post_x_other_unknown",
            "post_x_individual_ie_committee",
        ],
        "post_cu_superpac_partisan_advantage": ["republican"],
    }

    lines = [
        "# Regression Results",
        "",
        "Generated from balanced cycle-party-office panels. Monetary outcomes use log(1 + dollars), so coefficients can be translated as exp(beta) - 1. Source-share outcomes are in proportions, so multiply coefficients by 100 for percentage points.",
        "",
        "Significance markers: + p < .10, * p < .05, ** p < .01, *** p < .001. Bootstrap confidence intervals are percentile intervals from row resampling.",
        "",
    ]

    for dataset in sorted(coefficients["dataset"].unique()):
        lines.append(f"## {dataset}")
        dataset_coeffs = coefficients[coefficients["dataset"] == dataset]
        for model in dataset_coeffs["model"].drop_duplicates():
            model_coeffs = dataset_coeffs[dataset_coeffs["model"] == model]
            terms = key_terms.get(model, [])
            visible = model_coeffs[model_coeffs["term"].isin(terms)].copy()
            if visible.empty:
                continue
            order = {term: i for i, term in enumerate(terms)}
            visible["display_order"] = visible["term"].map(order)
            visible = visible.sort_values("display_order")

            summary_row = summaries[(summaries["dataset"] == dataset) & (summaries["model"] == model)].iloc[0]
            lines.append("")
            lines.append(f"### {model_label(model)}")
            lines.append(f"N = {int(summary_row['n'])}; adjusted R2 = {summary_row['adj_r2']:.3f}" if np.isfinite(summary_row["adj_r2"]) else f"N = {int(summary_row['n'])}")
            lines.append("")
            lines.append("| Term | Coef. | Robust SE | Bootstrap 95% CI | p | Interpretation |")
            lines.append("|---|---:|---:|---:|---:|---|")

            for _, row in visible.iterrows():
                ci = ""
                if np.isfinite(row["bootstrap_ci_low"]) and np.isfinite(row["bootstrap_ci_high"]):
                    ci = f"[{row['bootstrap_ci_low']:.3f}, {row['bootstrap_ci_high']:.3f}]"
                if np.isfinite(row["log_model_percent_change"]):
                    interp = f"{row['log_model_percent_change']:.1f}%"
                elif np.isfinite(row["share_model_percentage_points"]):
                    interp = f"{row['share_model_percentage_points']:.1f} percentage points"
                else:
                    interp = ""
                lines.append(
                    "| {term} | {coef:.3f}{stars} | {se:.3f} | {ci} | {p} | {interp} |".format(
                        term=key_term_label(row["term"]),
                        coef=row["coefficient"],
                        stars=row["stars"],
                        se=row["robust_se"] if np.isfinite(row["robust_se"]) else float("nan"),
                        ci=ci,
                        p=format_p_value(row["p_value"]),
                        interp=interp,
                    )
                )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run regression analyses for FEC independent expenditure data.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("C:/Users/sruja/Downloads/Code/FEC IE Analysis/outputs"),
        help="Directory containing aggregate_processed.pkl, senate_processed.pkl, and presidential_processed.pkl.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for regression outputs. Defaults to <data-dir>/regressions.",
    )
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=2000,
        help="Bootstrap repetitions for confidence intervals. Use 0 to skip.",
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    output_dir = args.output_dir or (data_dir / "regressions")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_coefficients: list[pd.DataFrame] = []
    all_summaries: list[dict] = []

    print("=" * 80)
    print("FEC Independent Expenditure Regression Analysis")
    print("=" * 80)

    for dataset_name in ["Aggregate", "Senate", "Presidential"]:
        print(f"\nRunning models for {dataset_name}...")
        data = load_processed_dataset(data_dir, dataset_name)
        coefficient_tables, summaries, panels = run_models_for_dataset(
            data,
            dataset_name,
            bootstrap_reps=args.bootstrap,
        )
        all_coefficients.extend(coefficient_tables)
        all_summaries.extend(summaries)

        for panel_name, panel in panels.items():
            panel_path = output_dir / f"{dataset_name.lower()}_{panel_name}.csv"
            panel.to_csv(panel_path, index=False)
            print(f"  Saved panel: {panel_path.name}")

    coefficients = add_interpretation_columns(pd.concat(all_coefficients, ignore_index=True))
    summaries = pd.DataFrame(all_summaries)

    coefficients_path = output_dir / "regression_coefficients.csv"
    summaries_path = output_dir / "regression_model_summaries.csv"
    markdown_path = output_dir / "regression_results.md"

    coefficients.to_csv(coefficients_path, index=False)
    summaries.to_csv(summaries_path, index=False)
    markdown_path.write_text(make_markdown_report(coefficients, summaries), encoding="utf-8")

    print("\nRegression outputs saved:")
    print(f"  {coefficients_path}")
    print(f"  {summaries_path}")
    print(f"  {markdown_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()
