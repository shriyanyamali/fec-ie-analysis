# FEC Independent Expenditure Analysis

## What This Program Does

1. **Loads and combines data** from all election cycles (2002-2020)

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
   - **Pre-Citizens United:** 2002-2010
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
The script expects your data to be organized as shown in your file tree:

```
data/
├── 2001_2002/
│   ├── pas202/
│   │   └── itpas2.txt
│   ├── cn02/
│   │   └── cn.txt
│   └── cm02/
│       └── cm.txt
├── 2003_2004/
│   ├── pas204/
│   │   └── itpas2.txt
│   ├── cn04/
│   │   └── cn.txt
│   └── cm04/
│       └── cm.txt
... (and so on through 2019_2020)
```

## Key FEC File Types

For the full key and codes, see [REFERENCE_GUIDE.md](REFERENCE_GUIDE.md)

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
Install dependencies using the provided requirements.txt file:

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```txt
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.3.0
seaborn>=0.11.0
```

---

### Data Structure Required

See [PROJECT_TREE.md](PROJECT_TREE.md) for how the file structure should be.

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

---

### Option 1: Run on Your Local Machine (Recommended)

1. **Ensure your data is organized** as shown above

2. **Update the data path** in `analyze_fec_data.py`:
   - Open the script in a text editor
   - Find the `main()` function (near the bottom)
   - Change the `data_dir` path to match your local path:
   
   ```python
   # Line 1215
   data_dir = 'C:/Users/sruja/Downloads/Data Collection/data'  # Change this path
   base_output_dir = 'C:/Users/sruja/Downloads/Data Collection/outputs'  # And this path
   ```

3. **Run the script:**
   ```bash
   python analyze_fec_data.py
   ```

4. **Find your results** in the output directory:
   ```
   outputs/
   ├── aggregate/ (13 files)
   ├── senate/ (13 files)
   └── presidential/ (13 files)
   ```

---

### Option 2: Upload Data to Cloud Environment

If running in a cloud environment (like this one):

1. **Upload the header files** to `/mnt/user-data/uploads/fec_data_file_headers/`:
   - pas2_header_file.csv
   - cn_header_file.csv
   - cm_header_file.csv

2. **Upload your data folder structure** to `/mnt/user-data/uploads/data/`
   - All cycle folders (2001_2002 through 2019_2020)
   - Each with pas2XX, cnXX, and cmXX subdirectories

3. **Update paths in the script:**
   ```python
   data_dir = '/mnt/user-data/uploads/data'
   base_output_dir = '/mnt/user-data/outputs'
   ```

4. **Run the analysis:**
   ```bash
   python analyze_fec_data_FINAL_VERSION.py
   ```

---

## Expected Outputs


### 1. Visualizations (8 PNG files)

All graphics have **no overall titles** (for flexibility in your paper) but multi-panel graphics have **panel titles** to identify what each panel shows.

#### Period Comparison Graphics (2 files)

**`aggregate_total_ie_by_period_party.png`** (with total)
- Bar chart comparing Democrat, Republican, and Total IEs for pre vs post Citizens United periods
- 3 bars per period: Democrat (blue) | Republican (red) | Total (gray)
- X-axis: Pre-CU (2002-2010), Post-CU (2011-2020)
- Y-axis: Total spending amount ($)

**`aggregate_total_ie_by_period_party_no_total.png`** (without total)
- Same as above but only 2 bars per period: Democrat (blue) | Republican (red)
- Cleaner visualization for partisan comparison

#### Time Series Graphics (2 files)

**`aggregate_ie_time_series.png`** (with total)
- Line chart showing IE trends from 2002-2020
- 3 lines: Democrat (blue solid), Republican (red solid), Total (gray dashed)
- Vertical line marks Citizens United decision (January 2010)
- X-axis: Election cycle end years (2002, 2004... 2020)
- Y-axis: Total spending amount ($)

**`aggregate_ie_time_series_no_total.png`** (without total)
- Same as above but only 2 lines: Democrat and Republican
- Focuses on partisan differences over time

#### Source Comparison Graphics (2 files)

**`aggregate_ie_by_source_comparison.png`** (with total)
- Side-by-side comparison of committee sources pre vs post Citizens United
- 2 panels with titles: "Pre-Citizens United (2002-2010)" | "Post-Citizens United (2011-2020)"
- Each panel shows horizontal bars for committee types: Super PAC, Traditional PAC, Party Committee, etc.
- 3 bars per committee type: Democrat (blue) | Republican (red) | Total (gray)
- Shows emergence of Super PACs post-2010

**`aggregate_ie_by_source_comparison_no_total.png`** (without total)
- Same layout but only 2 bars per committee type: Democrat and Republican

#### Source by Party Graphics (2 files)

**`aggregate_ie_source_by_party.png`** (with total)
- 3 panels with titles: "Democrat" | "Republican" | "Total (Both Parties)"
- Each panel shows committee sources comparing pre vs post periods
- Horizontal bars with 2 colors: Pre-CU (orange) | Post-CU (green)
- Shows how each party's funding sources shifted

**`aggregate_ie_source_by_party_no_total.png`** (without total)
- 2 panels with titles: "Democrat" | "Republican"
- Same structure but no "Total" panel

---

### 2. Data Files (5 CSV files)

All CSV files include header comments showing which graphics use their data.

#### Full Transaction Data

**`aggregate_independent_expenditures_full.csv`**
- Complete dataset of every IE transaction analyzed
- Columns include: CMTE_ID, TRANSACTION_AMT, CAND_ID, BENEFITING_PARTY, COMMITTEE_CATEGORY, PERIOD, CYCLE, IE_TYPE, etc.
- ~510,000 rows for aggregate dataset
- Used for: Custom analyses, verification
- Header comment: "Used in graphics: None (raw data file)"

#### Period/Party/Source Summary

**`aggregate_ie_summary_by_period_party_source.csv`**
- Aggregated totals by period, benefiting party, and committee source
- Shows total amount, transaction count, mean/median amounts, unique committees
- Includes "Total" rows for each period/committee combination
- **Includes Percent_Change column** showing % increase from pre to post
- ~40-60 rows
- Used for: Source comparison analyses, committee type breakdowns
- Header comment: "Used in graphics: aggregate_ie_by_source_comparison.png, aggregate_ie_source_by_party.png"

#### Cycle-by-Cycle Summary

**`aggregate_ie_summary_by_cycle.csv`**
- Individual election cycle totals (2002, 2004, 2006... 2020)
- Shows total amount, transaction count, unique committees
- **Includes Percent_Change_From_Previous column** showing % change from prior cycle
- **NEW: Period total rows at end:**
  - 2002-2010 TOTAL (Pre-Citizens United sum)
  - 2011-2020 TOTAL (Post-Citizens United sum)
  - 2002-2020 TOTAL (Overall sum)
- ~39 rows (30 individual cycles + 9 period totals)
- Used for: Time series analysis, trend identification
- Header comment: "Used in graphics: aggregate_ie_time_series.png, aggregate_total_ie_by_period_party.png"

#### Support vs Oppose Breakdown

**`aggregate_ie_support_vs_oppose_breakdown.csv`**
- Breakdown of supporting (24E, 24N) vs opposing (24A) expenditures
- Shows how much spending supported candidates vs opposed opponents
- Grouped by period, benefiting party, and IE type
- Includes "Total" rows for each period/party combination
- ~15-20 rows
- Used for: Understanding negative vs positive campaigning patterns
- Header comment: "Used in graphics: None (supplementary analysis file)"

#### Period Totals Summary

**`aggregate_period_totals_summary.csv`**
- Comprehensive summary with all key statistics in one place
- For each party (Democrat, Republican, Total), provides:
  1. **2002-2010 (Pre-Citizens United)** - Pre-period totals
  2. **2011-2020 (Post-Citizens United)** - Post-period totals
  3. **2002-2020 (Overall)** - Entire timeframe totals
  4. **Change (2002-2010 to 2011-2020)** - Absolute dollar/count changes
  5. **Percent Change (2002-2010 to 2011-2020)** - Percentage increases
- Columns: Total_Amount, Num_Transactions, Unique_Committees, Mean_Amount, Median_Amount
- 15 rows (5 rows × 3 parties)
- Used for: Quick reference, paper tables, summary statistics
- Header comment: "Used in graphics: Can be referenced in all graphics for overall context"

---

### 3. Complete Output Structure

```
outputs/
├── aggregate/
│   ├── Graphics (8 PNG files):
│   │   ├── aggregate_total_ie_by_period_party.png (with total)
│   │   ├── aggregate_total_ie_by_period_party_no_total.png
│   │   ├── aggregate_ie_by_source_comparison.png (with total)
│   │   ├── aggregate_ie_by_source_comparison_no_total.png
│   │   ├── aggregate_ie_time_series.png (with total)
│   │   ├── aggregate_ie_time_series_no_total.png
│   │   ├── aggregate_ie_source_by_party.png (with total)
│   │   └── aggregate_ie_source_by_party_no_total.png
│   └── Data Files (5 CSV files):
│       ├── aggregate_independent_expenditures_full.csv
│       ├── aggregate_ie_summary_by_period_party_source.csv
│       ├── aggregate_ie_summary_by_cycle.csv
│       ├── aggregate_ie_support_vs_oppose_breakdown.csv
│       └── aggregate_period_totals_summary.csv
│
├── senate/ (same 13 files with 'senate_' prefix)
└── presidential/ (same 13 files with 'presidential_' prefix)
```

**Total files generated: 39 (13 files × 3 datasets)**

---

### 4. Console Output
The script will print:
- Data loading progress for each cycle
- Summary statistics showing:
  - Total IEs by period and party
  - IEs by committee source (Super PACs, traditional PACs, etc.)
  - Percentage increase from pre- to post-Citizens United
  - Number of unique committees contributing