import hashlib
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PKG = REPO / "dataverse_package"
CYCLES = [(2001, 2002), (2003, 2004), (2005, 2006), (2007, 2008), (2009, 2010),
          (2011, 2012), (2013, 2014), (2015, 2016), (2017, 2018), (2019, 2020)]


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> None:
    if PKG.exists():
        try:
            shutil.rmtree(PKG)
        except PermissionError:
            print("Could not delete the existing package folder; files will be overwritten in place.")
    PKG.mkdir(exist_ok=True)

    # 1. code
    for p in sorted((REPO / "scripts").glob("*.py")):
        copy(p, PKG / "code" / p.name)
    copy(REPO / "requirements.txt", PKG / "code" / "requirements.txt")
    for p in ["README.md", "guides/OUTPUTS.md", "guides/PROJECT_TREE.md", "guides/REFERENCE_GUIDE.md"]:
        if (REPO / p).exists():
            copy(REPO / p, PKG / "code" / Path(p).name if p == "README.md" else PKG / "code" / "guides" / Path(p).name)

    # 2. FEC header files + raw-data manifest
    for p in sorted((REPO / "data" / "fec_data_file_headers").glob("*.csv")):
        copy(p, PKG / "data" / "fec_data_file_headers" / p.name)
    lines = ["file,cycle,fec_download_url,md5,bytes"]
    for s, e in CYCLES:
        yy = str(e)[-2:]
        for sub, fname, kind in [(f"pas2{yy}", "itpas2.txt", "pas2"), (f"cn{yy}", "cn.txt", "cn"), (f"cm{yy}", "cm.txt", "cm")]:
            local = REPO / "data" / f"{s}_{e}" / sub / fname
            url = f"https://www.fec.gov/files/bulk-downloads/{e}/{kind}{yy}.zip"
            if local.exists():
                lines.append(f"{s}_{e}/{sub}/{fname},{s}-{e},{url},{md5(local)},{local.stat().st_size}")
            else:
                lines.append(f"{s}_{e}/{sub}/{fname},{s}-{e},{url},MISSING,")
    (PKG / "data" / "RAW_DATA_MANIFEST.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 3. outputs (everything except pickles)
    n_out = 0
    for p in sorted((REPO / "outputs").rglob("*")):
        if p.is_file() and p.suffix.lower() in {".csv", ".md", ".png", ".txt"}:
            copy(p, PKG / "outputs" / p.relative_to(REPO / "outputs"))
            n_out += 1

    # 4. deposit README with codebook
    readme = f"""# Replication data and code for: Shifts in Independent Expenditures by Party and Committee Type After *Citizens United*

Author: Shriyan Yamali. Mentor: Bradley A. Smith, Capital University Law School.

This package contains the code, derived data, regression output, and figures for a study of
independent expenditures (IEs) benefiting Democratic and Republican candidates in U.S. Senate and
presidential elections, 2001-2020, before and after *Citizens United v. FEC* (2010).

## Contents

- `code/` - all Python scripts, `requirements.txt`, and the repository README and guides.
  Run order: `fec_data_loader.py` -> `fec_data_visualizer.py` -> `fec_regression_analysis.py` ->
  `fec_regression_graphs.py` -> `fec_regression_tables.py` -> `diagnose.py`;
  robustness check: `fec_data_loader_corrected.py` then `fec_regression_analysis.py --data-dir outputs/robustness_check`;
  verification: `check_paper_numbers.py` compares every number stated in the research report with the outputs.
- `data/fec_data_file_headers/` - the three FEC header files used to read the bulk files.
- `data/RAW_DATA_MANIFEST.csv` - the thirty raw FEC bulk files used (one `itpas2.txt`, `cn.txt`, and `cm.txt`
  per two-year cycle), with the FEC download URL, MD5 checksum, and size of each file as used in this study.
  The raw files (about 1.8 GB) are public domain and are not duplicated here; download them from the listed URLs,
  unzip, and place them as `data/<start>_<end>/<pas2|cn|cm><yy>/<file>` (see `code/guides/PROJECT_TREE.md`).
- `outputs/aggregate/`, `outputs/senate/`, `outputs/presidential/` - transaction-level and summary CSV files for
  Senate + presidential races combined, Senate only, and presidential only. The two report figures are in
  `outputs/aggregate/`.
- `outputs/regressions/` - regression coefficients (with HC1 robust standard errors and bootstrap 95% confidence
  intervals), model summaries, the balanced panels the models were estimated on, `regression_results.md`,
  the coefficient figure, and CSV/Markdown tables.
- `outputs/robustness_check/regressions/` - the same regression outputs under the alternative committee
  classification described in the report (same-cycle committee types, hybrid PACs as their own category,
  transaction types 24A/24E only).
- `outputs/other_IEs_breakdown.csv` - composition of the Other/Unknown committee category by FEC type code.

## Codebook: `<dataset>_independent_expenditures_full.csv`

One row per independent-expenditure transaction retained in the analysis. Columns from the FEC bulk files keep
their FEC names (see https://www.fec.gov/campaign-finance-data/contributions-committees-candidates-file-description/,
candidate master and committee master file descriptions). Columns added by the study:

| Column | Meaning |
|---|---|
| CYCLE, CYCLE_END_YEAR | Two-year election cycle of the FEC file the record came from (e.g. 2011-2012, 2012). |
| IE_TYPE | SUPPORT (transaction type 24E or 24N) or OPPOSE (24A). |
| CANDIDATE_PARTY | Party of the candidate named in the expenditure, from the candidate master file. |
| BENEFITING_PARTY | Democrat if the IE supported a Democrat or opposed a Republican; Republican if it supported a Republican or opposed a Democrat. Only these two values are retained. |
| CAND_OFFICE | S (Senate) or P (presidential), from the candidate ID. |
| COMMITTEE_CATEGORY | Study category from the committee's FEC type code: Super PAC (O); Traditional PAC (N, Q, V); Party Committee (X, Y, Z); Individual IE Committee (U); Other/Unknown (all others). |
| PERIOD | Pre-Citizens United (2001-2010) or Post-Citizens United (2011-2020). |

Exclusions applied by `fec_data_loader.py`: negative amounts (refunds/corrections); records for offices other than
Senate and president; records benefiting third-party or unidentifiable candidates; records attributed to candidate
committees; and pre-2011 records of committees classified as Super PACs. All amounts are nominal U.S. dollars.

## Software

Python 3.10+, pandas, NumPy, Matplotlib, seaborn, Pillow (versions in `code/requirements.txt`). Results in the report
were generated with pandas 2.3.3 and NumPy 2.2.6. Figures use Times New Roman when available and Liberation Serif
otherwise.

## Source

Federal Election Commission, bulk data (https://www.fec.gov/data/browse-data/?tab=bulk-data): "Contributions from
committees to candidates & independent expenditures", "Candidate master", and "Committee master" files for the
2001-2002 through 2019-2020 cycles.
"""
    (PKG / "README.md").write_text(readme, encoding="utf-8")

    # 5. file list with checksums for the deposit
    rows = ["path,bytes,md5"]
    total = 0
    for p in sorted(PKG.rglob("*")):
        if p.is_file() and p.name != "FILE_LIST.csv":
            rows.append(f"{p.relative_to(PKG).as_posix()},{p.stat().st_size},{md5(p)}")
            total += p.stat().st_size
    (PKG / "FILE_LIST.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Package written to {PKG}: {len(rows) - 1} files, {total / 1e6:.1f} MB ({n_out} output files)")


if __name__ == "__main__":
    main()
