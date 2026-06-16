from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DPI = 300
DATASETS = ["Aggregate", "Senate", "Presidential"]


def pt_to_px(pt: float) -> int:
    return int(pt * DPI / 72)


def load_font(pt: float = 12, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\timesbd.ttf" if bold else r"C:\Windows\Fonts\times.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), pt_to_px(pt))
    return ImageFont.load_default()


FONT = load_font(12)
FONT_BOLD = load_font(12, bold=True)
FONT_SMALL = load_font(10)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def fnum(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else float("nan")


def stars(p_value: float) -> str:
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def fmt_num(value: float, digits: int = 3) -> str:
    out = f"{value:.{digits}f}"
    if out.startswith("-0."):
        out = "-." + out.split(".", 1)[1]
    elif out.startswith("0."):
        out = "." + out.split(".", 1)[1]
    return out


def coeff_cell(row: dict[str, str] | None) -> str:
    if row is None:
        return ""
    coef = fnum(row, "coefficient")
    se = fnum(row, "robust_se")
    p_value = fnum(row, "p_value")
    return f"{fmt_num(coef)}{stars(p_value)}\n({fmt_num(se)})"


def find_row(rows: list[dict[str, str]], dataset: str, model: str, term: str) -> dict[str, str] | None:
    for row in rows:
        if row["dataset"] == dataset and row["model"] == model and row["term"] == term:
            return row
    return None


def find_summary(rows: list[dict[str, str]], dataset: str, model: str) -> dict[str, str] | None:
    for row in rows:
        if row["dataset"] == dataset and row["model"] == model:
            return row
    return None


def build_table(coeffs: list[dict[str, str]], summaries: list[dict[str, str]], title: str, model: str, variables: list[tuple[str, str]], note: str) -> tuple[list[list[str]], str, str]:
    table = [["", "Model 1", "Model 2", "Model 3"], ["", "Aggregate", "Senate", "Presidential"]]
    for term, label in variables:
        row = [label]
        for dataset in DATASETS:
            row.append(coeff_cell(find_row(coeffs, dataset, model, term)))
        table.append(row)

    n_row = ["N"]
    r2_row = ["Adj. R-squared"]
    for dataset in DATASETS:
        summary = find_summary(summaries, dataset, model)
        n_row.append(str(int(float(summary["n"]))) if summary else "")
        r2_row.append(fmt_num(float(summary["adj_r2"])) if summary else "")
    table.append(n_row)
    table.append(r2_row)
    return table, title, note


def write_markdown(table: list[list[str]], title: str, note: str, path: Path) -> None:
    lines = [f"# {title}", ""]
    header = table[0]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for row in table[1:]:
        cleaned = [cell.replace("\n", "<br>") for cell in row]
        lines.append("| " + " | ".join(cleaned) + " |")
    lines.extend(["", f"Note: {note}"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv_table(table: list[list[str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(table)


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, font: ImageFont.ImageFont, anchor: str = "lm") -> None:
    draw.text(xy, text, font=font, fill="#111111", anchor=anchor)


def draw_table_png(table: list[list[str]], title: str, note: str, path: Path) -> None:
    width = int(7.2 * DPI)
    row_h = 132
    title_h = 120
    note_h = 260
    height = title_h + row_h * len(table) + note_h
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    left = 70
    col_w = [670, 450, 450, 450]
    x_positions = [left]
    for w in col_w[:-1]:
        x_positions.append(x_positions[-1] + w)

    y = 60
    draw_text(draw, (left, y), title, FONT_BOLD)
    y += 70
    draw.line((left, y, width - left, y), fill="#111111", width=3)

    for r, row in enumerate(table):
        y_mid = y + row_h / 2
        for c, cell in enumerate(row):
            x = x_positions[c]
            if c == 0:
                draw_text(draw, (x, y_mid), cell, FONT_BOLD if r < 2 else FONT)
            else:
                lines = cell.split("\n")
                if len(lines) == 1:
                    draw_text(draw, (x + col_w[c] / 2, y_mid), lines[0], FONT_BOLD if r < 2 else FONT, anchor="mm")
                else:
                    draw_text(draw, (x + col_w[c] / 2, y_mid - 24), lines[0], FONT, anchor="mm")
                    draw_text(draw, (x + col_w[c] / 2, y_mid + 35), lines[1], FONT_SMALL, anchor="mm")
        if r in [1, len(table) - 3]:
            draw.line((left, y + row_h, width - left, y + row_h), fill="#111111", width=2)
        y += row_h

    draw.line((left, y, width - left, y), fill="#111111", width=3)
    note_lines = wrap_note(note, 105)
    y += 35
    for line in note_lines:
        draw_text(draw, (left, y), line, FONT_SMALL)
        y += 38

    image.save(path, "PNG", dpi=(DPI, DPI))


def wrap_note(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if len(trial) > width and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def save_outputs(table: list[list[str]], title: str, note: str, basename: str, output_dir: Path) -> None:
    write_csv_table(table, output_dir / f"{basename}.csv")
    write_markdown(table, title, note, output_dir / f"{basename}.md")
    draw_table_png(table, title, note, output_dir / f"{basename}.png")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create journal-style regression tables.")
    parser.add_argument("--coefficients", type=Path, default=Path("outputs/regressions/regression_coefficients.csv"))
    parser.add_argument("--summaries", type=Path, default=Path("outputs/regressions/regression_model_summaries.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/regressions/tables"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    coeffs = read_csv(args.coefficients)
    summaries = read_csv(args.summaries)

    party_table = build_table(
        coeffs,
        summaries,
        "Table 1. OLS Models of Party-Benefiting Independent Expenditures",
        "party_growth_baseline",
        [
            ("post_cu", "Post-Citizens United"),
            ("republican", "Republican"),
            ("post_x_republican", "Post-CU x Republican"),
            ("presidential_office", "Presidential office"),
            ("presidential_cycle", "Presidential cycle"),
            ("const", "Constant"),
        ],
        "Robust standard errors in parentheses. Dependent variable is log(1 + total independent expenditure dollars). *p < .10, **p < .05, ***p < .01.",
    )
    save_outputs(*party_table, "table_1_party_growth", args.output_dir)

    source_table = build_table(
        coeffs,
        summaries,
        "Table 2. OLS Models of Independent Expenditure Source Share",
        "source_share_shift_category_specific_post_base_party_committee",
        [
            ("post_x_super_pac", "Post-CU x Super PAC"),
            ("post_x_party_committee", "Post-CU x Party committee"),
            ("post_x_traditional_pac", "Post-CU x Traditional PAC"),
            ("post_x_other_unknown", "Post-CU x Other/Unknown"),
            ("post_x_individual_ie_committee", "Post-CU x Individual IE"),
            ("const", "Constant"),
        ],
        "Robust standard errors in parentheses. Dependent variable is committee-category share of cycle-party-office independent expenditure dollars. Coefficients are proportions, so .591 equals 59.1 percentage points. *p < .10, **p < .05, ***p < .01.",
    )
    save_outputs(*source_table, "table_2_source_share", args.output_dir)

    superpac_share_table = build_table(
        coeffs,
        summaries,
        "Table 3. Weighted OLS Models of Super PAC Independent Expenditure Source Share",
        "weighted_superpac_source_share_partisan_shift",
        [
            ("post_cu", "Post-Citizens United"),
            ("republican", "Republican"),
            ("post_x_republican", "Post-CU x Republican"),
            ("presidential_office", "Presidential office"),
            ("presidential_cycle", "Presidential cycle"),
            ("const", "Constant"),
        ],
        "Robust standard errors in parentheses. The dependent variable is Super PAC share of cycle-party-office independent expenditure dollars. Models are weighted by total independent expenditure dollars in each cycle-party-office cell, so the estimates reflect where independent expenditure dollars flowed. Coefficients are proportions, so .131 equals 13.1 percentage points. Significance tests are two-tailed. *p < .10, **p < .05, ***p < .01.",
    )
    save_outputs(*superpac_share_table, "table_3_superpac_source_share", args.output_dir)

    superpac_table = build_table(
        coeffs,
        summaries,
        "Table 4. Post-Citizens United Super PAC Models",
        "post_cu_superpac_partisan_advantage",
        [
            ("republican", "Republican"),
            ("presidential_office", "Presidential office"),
            ("presidential_cycle", "Presidential cycle"),
            ("cycle_index", "Election-cycle trend"),
            ("const", "Constant"),
        ],
        "Robust standard errors in parentheses. Dependent variable is log(1 + Super PAC independent expenditure dollars) in post-Citizens United cycles only. *p < .10, **p < .05, ***p < .01.",
    )
    save_outputs(*superpac_table, "table_4_superpac_partisan", args.output_dir)

    print("Regression tables saved to:")
    print(f"  {args.output_dir}")


if __name__ == "__main__":
    main()
