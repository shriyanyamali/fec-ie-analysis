[![DOI](https://img.shields.io/badge/DOI-10.7910/DVN/FYTRLU-blue)](https://doi.org/10.7910/DVN/FYTRLU)

# FEC Independent Expenditure Analysis

## What This Program Does

1. **Loads and combines data** from all election cycles (2001-2020)

2. **Identifies independent expenditures** by filtering for transaction types 24E, 24A, 24N

3. **Links to candidate data** to determine:
   - Party affiliation (Democrat vs Republican)
   - Office sought (Senate vs Presidential)

4. **Links to committee data** to categorize sources:
   - Super PACs (post-Citizens United phenomenon)
   - Traditional PACs
   - Party committees
   - Individual IE committees
   - Other sources

5. **Compares two periods:**
   - **Pre-Citizens United:** 2001-2010
   - **Post-Citizens United:** 2011-2020

6. **Analyzes:**
   - Total dollar amounts by party and period
   - Source of expenditures (which types of committees)
   - Percentage increase for each party
   - Number of unique committees participating
   - Trends over time

## Required Files

### 1. Header Files

- `pas2_header_file.csv` - Independent expenditure file headers
- `cn_header_file.csv` - Candidate master file headers
- `cm_header_file.csv` - Committee master file headers

### 2. Data Files

For each biennial election cycle, download a file from the following categories for that cycle. Extract all the downloaded zip files before organizing your data into folders.
> You should have 3 x # of cycles + 3 data files. For example, if you are analyzing 10 cycles, then you should have 3 x 10 + 3 = 33 data files.

- Contributions from committees to candidates & independent expenditures
- Candidate master
- Committee master

See [PROJECT_TREE.md](guides/PROJECT_TREE.md) for how the file structure should be.

Your data directory must follow this structure:

```
data/
├── fec_data_file_headers/
│   ├── pas2_header_file.csv
│   ├── cn_header_file.csv
│   └── cm_header_file.csv
├── 2001_2002/
│   ├── pas202/
│   │   └── itpas2.txt
│   ├── cn02/
│   │   └── cn.txt
│   └── cm02/
│       └── cm.txt
├── 2003_2004/
│   └── [same structure as above]
├── ... (through 2019_2020)
```

## Key FEC File Types

For the full key and codes, see [REFERENCE_GUIDE.md](guides/REFERENCE_GUIDE.md)

### PAS2 Files (itpas2.txt)

- **Contains:** Contributions from committees to candidates AND independent expenditures
- **Key Transaction Types:**
  - `24E` = Independent expenditure advocating election of candidate
  - `24A` = Independent expenditure opposing election of candidate
  - `24N` = Independent expenditure (generic)

### Candidate Master (cn.txt)

- **Contains:** Candidate information including party affiliation and office sought
- **Used to:** Identify Democrat vs Republican candidates and filter for Senate/Presidential races

### Committee Master (cm.txt)

- **Contains:** Committee information including committee type
- **Key Committee Types:**
  - `O` = Super PAC (independent expenditure-only committee)
  - `N`, `Q`, `V` = Traditional PACs
  - `U` = Individual independent expenditure committee
  - `X`, `Y`, `Z` = Party committees

## How to Run

### Requirements

**Python Version:** Python 3.7 or higher

**Required Packages:**
Install dependencies:

```bash
pip install -r requirements.txt
```

---

1. **Ensure your data is organized** as shown above. Paths are resolved relative to the repository, so nothing needs to be edited. Optionally check the setup first:

   ```bash
   python scripts/verify_setup.py
   ```

2. **Load and classify the data** (reads the ten cycles, keeps independent expenditures, links candidates and committees, writes `outputs/*_processed.pkl`):

   ```bash
   python scripts/fec_data_loader.py
   ```

3. **Create the summary tables and the two report figures:**

   ```bash
   python scripts/fec_data_visualizer.py
   ```

   Writes the CSV summaries for the aggregate, Senate, and presidential datasets to `outputs/<dataset>/` and the figures `aggregate_ie_time_series_no_total.png` and `aggregate_ie_by_source_comparison_no_total.png` to `outputs/aggregate/`.

4. **Run the regression analysis:**

   ```bash
   python scripts/fec_regression_analysis.py
   ```

   Writes coefficients, model summaries, balanced panels, and `regression_results.md` to `outputs/regressions/`.

5. **Create the regression figure and tables:**

   ```bash
   python scripts/fec_regression_graphs.py
   python scripts/fec_regression_tables.py
   ```

   Writes `outputs/regressions/figures/figure_1_source_share_aggregate.png` and CSV/Markdown tables to `outputs/regressions/tables/`.

6. **Break down the Other/Unknown category** by FEC committee type code:

   ```bash
   python scripts/diagnose.py
   ```

   Writes `outputs/other_IEs_breakdown.csv`.

7. **Robustness check** (alternative committee classification: same-cycle committee types, hybrid PACs as their own category, transaction types 24A/24E only):

   ```bash
   python scripts/fec_data_loader_corrected.py
   python scripts/fec_regression_analysis.py --data-dir outputs/robustness_check
   ```

8. **Verify the research report against the outputs** (every number stated in the report is checked):

   ```bash
   python scripts/check_paper_numbers.py
   ```

9. **Find your results** in the output directory:

   ```
   outputs/
   ├── aggregate/          (5 CSV files, 2 PNG figures)
   ├── senate/             (5 CSV files)
   ├── presidential/       (5 CSV files)
   ├── regressions/        (9 files; tables/ and figures/ subfolders)
   ├── robustness_check/   (processed data and regressions/ for the alternative classification)
   └── other_IEs_breakdown.csv
   ```

   For the full output structure, see [OUTPUTS.md](guides/OUTPUTS.md)
