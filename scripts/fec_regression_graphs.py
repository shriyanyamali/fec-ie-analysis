from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DPI = 300
FONT_PT = 12
BLACK = "#111111"
DARK = "#444444"
MID = "#777777"
LIGHT = "#d9d9d9"
WHITE = "white"

DATASETS = ["Aggregate", "Senate", "Presidential"]
SOURCE_TERMS = [
    ("post_x_super_pac", "Super PAC"),
    ("post_x_party_committee", "Party committee"),
    ("post_x_traditional_pac", "Traditional PAC"),
    ("post_x_other_unknown", "Other/Unknown"),
    ("post_x_individual_ie_committee", "Individual IE"),
]
CORE_SOURCE_TERMS = SOURCE_TERMS[:3]
PARTY_TERMS = [
    ("post_cu", "Post-CU"),
    ("post_x_republican", "Post-CU x Republican"),
]


def inches(width: float, height: float) -> tuple[int, int]:
    return int(width * DPI), int(height * DPI)


def pt_to_px(pt: float) -> int:
    return int(pt * DPI / 72)


def load_font(pt: float = FONT_PT, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\timesbd.ttf" if bold else r"C:\Windows\Fonts\times.ttf",
        r"C:\Windows\Fonts\timesbi.ttf" if bold else r"C:\Windows\Fonts\timesi.ttf",
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


def read_coefficients(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def fnum(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else float("nan")


def p_label(p_value: float) -> str:
    if not math.isfinite(p_value):
        return ""
    if p_value < 0.001:
        return "p < .001"
    return f"p = {p_value:.3f}".replace("0.", ".")


def find_row(rows: list[dict[str, str]], dataset: str, model: str, term: str) -> dict[str, str] | None:
    for row in rows:
        if row["dataset"] == dataset and row["model"] == model and row["term"] == term:
            return row
    return None


def coefficient_entry(row: dict[str, str], *, share: bool) -> dict[str, float]:
    if share:
        coef = fnum(row, "share_model_percentage_points")
        low = fnum(row, "bootstrap_ci_low") * 100
        high = fnum(row, "bootstrap_ci_high") * 100
    else:
        coef = fnum(row, "log_model_percent_change")
        low = (math.exp(fnum(row, "bootstrap_ci_low")) - 1) * 100
        high = (math.exp(fnum(row, "bootstrap_ci_high")) - 1) * 100
    return {"coef": coef, "low": low, "high": high, "p": fnum(row, "p_value")}


def draw_centered_text(draw: ImageDraw.ImageDraw, x: float, y: float, text: str, font: ImageFont.ImageFont, fill: str = BLACK) -> None:
    draw.text((x, y), text, font=font, fill=fill, anchor="mm")


def draw_right_text(draw: ImageDraw.ImageDraw, x: float, y: float, text: str, font: ImageFont.ImageFont, fill: str = BLACK) -> None:
    draw.text((x, y), text, font=font, fill=fill, anchor="rm")


def draw_left_text(draw: ImageDraw.ImageDraw, x: float, y: float, text: str, font: ImageFont.ImageFont, fill: str = BLACK) -> None:
    draw.text((x, y), text, font=font, fill=fill, anchor="lm")


def draw_dot_ci(
    draw: ImageDraw.ImageDraw,
    y: float,
    coef: float,
    low: float,
    high: float,
    p_value: float,
    *,
    x_min: float,
    x_max: float,
    left: float,
    plot_w: float,
) -> None:
    def xpos(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_w

    x1 = max(left, min(left + plot_w, xpos(low)))
    x2 = max(left, min(left + plot_w, xpos(high)))
    xd = max(left, min(left + plot_w, xpos(coef)))
    color = BLACK if p_value < 0.05 else MID
    draw.line((x1, y, x2, y), fill=DARK, width=4)
    radius = 8
    draw.ellipse((xd - radius, y - radius, xd + radius, y + radius), fill=color, outline=BLACK, width=2)


def source_share_aggregate(rows: list[dict[str, str]], out_path: Path) -> None:
    width, height = inches(6.5, 3.6)
    image = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(image)

    left = 620
    right = 1600
    plot_w = right - left
    x_min, x_max = -80, 80
    y0 = 250
    row_gap = 120

    draw_left_text(draw, 75, 70, "Figure 1. Source-share shifts after Citizens United", FONT_BOLD)
    draw_left_text(draw, 75, 125, "Aggregate model; dots are coefficient estimates and bars are bootstrap 95% CIs.", FONT)

    def xpos(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_w

    axis_y = height - 160
    for tick in [-80, -40, 0, 40, 80]:
        x = xpos(tick)
        draw.line((x, y0 - 60, x, axis_y), fill=LIGHT, width=2)
        draw_centered_text(draw, x, axis_y + 55, str(tick), FONT_SMALL, fill=DARK)
    draw.line((xpos(0), y0 - 75, xpos(0), axis_y), fill=BLACK, width=3)
    draw.line((left, axis_y, right, axis_y), fill=BLACK, width=3)

    for i, (term, label) in enumerate(SOURCE_TERMS):
        row = find_row(rows, "Aggregate", "source_share_shift_category_specific_post_base_party_committee", term)
        if not row:
            continue
        entry = coefficient_entry(row, share=True)
        y = y0 + i * row_gap
        draw_right_text(draw, left - 45, y, label, FONT)
        draw_dot_ci(draw, y, entry["coef"], entry["low"], entry["high"], entry["p"], x_min=x_min, x_max=x_max, left=left, plot_w=plot_w)
        draw_left_text(draw, right + 45, y, f"{entry['coef']:+.1f} ({p_label(entry['p'])})", FONT_SMALL, fill=DARK)

    draw_centered_text(draw, (left + right) / 2, height - 55, "Change in source share, percentage points", FONT)
    image.save(out_path, "PNG", dpi=(DPI, DPI))


def source_share_by_office(rows: list[dict[str, str]], out_path: Path) -> None:
    width, height = inches(6.5, 4.0)
    image = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(image)

    left = 620
    right = 1600
    plot_w = right - left
    x_min, x_max = -80, 80
    y0 = 260
    row_gap = 88
    panel_gap = 92

    draw_left_text(draw, 75, 70, "Figure 2. Core source shifts by election type", FONT_BOLD)
    draw_left_text(draw, 75, 125, "Only the three largest source changes are shown for compactness.", FONT)

    def xpos(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_w

    axis_y = height - 155
    for tick in [-80, -40, 0, 40, 80]:
        x = xpos(tick)
        draw.line((x, y0 - 70, x, axis_y), fill=LIGHT, width=2)
        draw_centered_text(draw, x, axis_y + 55, str(tick), FONT_SMALL, fill=DARK)
    draw.line((xpos(0), y0 - 80, xpos(0), axis_y), fill=BLACK, width=3)
    draw.line((left, axis_y, right, axis_y), fill=BLACK, width=3)

    y = y0
    for dataset in DATASETS:
        draw_left_text(draw, 75, y, dataset, FONT_BOLD)
        for term, label in CORE_SOURCE_TERMS:
            row = find_row(rows, dataset, "source_share_shift_category_specific_post_base_party_committee", term)
            if not row:
                continue
            entry = coefficient_entry(row, share=True)
            draw_right_text(draw, left - 45, y, label, FONT)
            draw_dot_ci(draw, y, entry["coef"], entry["low"], entry["high"], entry["p"], x_min=x_min, x_max=x_max, left=left, plot_w=plot_w)
            draw_left_text(draw, right + 45, y, f"{entry['coef']:+.1f}", FONT_SMALL, fill=DARK)
            y += row_gap
        y += panel_gap

    draw_centered_text(draw, (left + right) / 2, height - 55, "Change in source share, percentage points", FONT)
    image.save(out_path, "PNG", dpi=(DPI, DPI))


def party_growth_effects(rows: list[dict[str, str]], out_path: Path) -> None:
    width, height = inches(6.5, 3.4)
    image = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(image)

    left = 620
    right = 1600
    plot_w = right - left
    x_min, x_max = -100, 1200
    y0 = 250
    row_gap = 82
    panel_gap = 76

    draw_left_text(draw, 75, 70, "Figure 3. Party-growth regression effects", FONT_BOLD)
    draw_left_text(draw, 75, 125, "Estimates are percent changes from log-dollar coefficients.", FONT)

    def xpos(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_w

    axis_y = height - 150
    for tick in [0, 300, 600, 900, 1200]:
        x = xpos(tick)
        draw.line((x, y0 - 70, x, axis_y), fill=LIGHT, width=2)
        draw_centered_text(draw, x, axis_y + 55, str(tick), FONT_SMALL, fill=DARK)
    draw.line((xpos(0), y0 - 80, xpos(0), axis_y), fill=BLACK, width=3)
    draw.line((left, axis_y, right, axis_y), fill=BLACK, width=3)

    y = y0
    for dataset in DATASETS:
        draw_left_text(draw, 75, y, dataset, FONT_BOLD)
        for term, label in PARTY_TERMS:
            row = find_row(rows, dataset, "party_growth_baseline", term)
            if not row:
                continue
            entry = coefficient_entry(row, share=False)
            draw_right_text(draw, left - 45, y, label, FONT)
            draw_dot_ci(draw, y, entry["coef"], entry["low"], entry["high"], entry["p"], x_min=x_min, x_max=x_max, left=left, plot_w=plot_w)
            draw_left_text(draw, right + 45, y, f"{entry['coef']:+.1f} ({p_label(entry['p'])})", FONT_SMALL, fill=DARK)
            y += row_gap
        y += panel_gap

    draw_centered_text(draw, (left + right) / 2, height - 55, "Estimated percent change in IE dollars", FONT)
    image.save(out_path, "PNG", dpi=(DPI, DPI))


def main() -> None:
    parser = argparse.ArgumentParser(description="Create compact PNG figures from FEC regression results.")
    parser.add_argument(
        "--coefficients",
        type=Path,
        default=Path("outputs/regressions/regression_coefficients.csv"),
        help="Path to regression_coefficients.csv.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/regressions/figures"),
        help="Directory for PNG graph output.",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = read_coefficients(args.coefficients)
    source_share_aggregate(rows, args.output_dir / "figure_1_source_share_aggregate.png")
    source_share_by_office(rows, args.output_dir / "figure_2_source_shift_by_office.png")
    party_growth_effects(rows, args.output_dir / "figure_3_party_growth_effects.png")

    print("Regression PNG figures saved to:")
    print(f"  {args.output_dir / 'figure_1_source_share_aggregate.png'}")
    print(f"  {args.output_dir / 'figure_2_source_shift_by_office.png'}")
    print(f"  {args.output_dir / 'figure_3_party_growth_effects.png'}")


if __name__ == "__main__":
    main()
