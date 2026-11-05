## Expected Outputs

### 1. Visualizations (2 PNG files, aggregate dataset only)

Only the two figures used in the research report are produced. Neither includes a "Total" series.

**`aggregate_ie_time_series_no_total.png`** (report Figure 1)
- Line chart of total IEs benefiting Democratic and Republican candidates by election cycle, 2002–2020
- Vertical dotted line marks *Citizens United* (January 2010)

**`aggregate_ie_by_source_comparison_no_total.png`** (report Figure 3)
- Two panels, "Pre-Citizens United (2001-2010)" and "Post-Citizens United (2011-2020)"
- Horizontal bars by committee category, one bar per benefiting party

The regression coefficient plot (report Figure 2) is produced separately by `fec_regression_graphs.py` as `outputs/regressions/figures/figure_1_source_share_aggregate.png`.

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
- Header comment: "Used in graphics: aggregate_ie_by_source_comparison_no_total.png (aggregate only)"

#### Cycle-by-Cycle Summary

**`aggregate_ie_summary_by_cycle.csv`**
- Individual election cycle totals (2002, 2004, 2006... 2020)
- Shows total amount, transaction count, unique committees
- **Includes Percent_Change_From_Previous column** showing % change from prior cycle
- **Period total rows at end:**
  - 2001-2010 TOTAL (Pre-Citizens United sum)
  - 2011-2020 TOTAL (Post-Citizens United sum)
  - 2001-2020 TOTAL (Overall sum)
- ~39 rows (30 individual cycles + 9 period totals)
- Used for: Time series analysis, trend identification
- Header comment: "Used in graphics: aggregate_ie_time_series_no_total.png (aggregate only)"

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
  1. **2001-2010 (Pre-Citizens United)** - Pre-period totals
  2. **2011-2020 (Post-Citizens United)** - Post-period totals
  3. **2001-2020 (Overall)** - Entire timeframe totals
  4. **Change (2001-2010 to 2011-2020)** - Absolute dollar/count changes
  5. **Percent Change (2001-2010 to 2011-2020)** - Percentage increases
- Columns: Total_Amount, Num_Transactions, Unique_Committees, Mean_Amount, Median_Amount
- 15 rows (5 rows × 3 parties)
- Used for: Quick reference, paper tables, summary statistics
- Header comment: "Used in graphics: Can be referenced in all graphics for overall context"