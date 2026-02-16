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

### Data Structure Required

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

---

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

   For the full output structure, see [OUTPUTS.md](guides/OUTPUTS.md)

--