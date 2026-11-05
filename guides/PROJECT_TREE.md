# Project Tree

> Do not change the location of any files or directories as that breaks the analysis pipeline. If you change the location of any files or directories, make sure to reflect the changes in the `fec_data_loader.py` script.

```
.
├── requirements.txt│
├── scripts/
│   ├── fec_data_loader.py
│   ├── fec_data_loader_corrected.py   (robustness check: alternative committee classification)
│   ├── fec_data_visualizer.py
│   ├── fec_regression_analysis.py
│   ├── fec_regression_graphs.py
│   ├── fec_regression_tables.py
│   ├── diagnose.py
│   ├── check_paper_numbers.py
│   └── verify_setup.py
│
├── data/
│   ├── fec_data_file_headers/
│   │   ├── pas2_header_file.csv
│   │   ├── cn_header_file.csv
│   │   └── cm_header_file.csv
│   │
│   ├── 2001_2002/
│   │   ├── pas202/
│   │   │   └── itpas2.txt
│   │   ├── cn02/
│   │   │   └── cn.txt
│   │   └── cm02/
│   │       └── cm.txt
│   │
│   ├── 2003_2004/
│   │   ├── pas204/
│   │   │   └── itpas2.txt
│   │   ├── cn04/
│   │   │   └── cn.txt
│   │   └── cm04/
│   │       └── cm.txt
│   │
│   ├── 2005_2006/
│   │   ├── pas206/
│   │   │   └── itpas2.txt
│   │   ├── cn06/
│   │   │   └── cn.txt
│   │   └── cm06/
│   │       └── cm.txt
│   │
│   ├── 2007_2008/
│   │   ├── pas208/
│   │   │   └── itpas2.txt
│   │   ├── cn08/
│   │   │   └── cn.txt
│   │   └── cm08/
│   │       └── cm.txt
│   │
│   ├── 2009_2010/
│   │   ├── pas210/
│   │   │   └── itpas2.txt
│   │   ├── cn10/
│   │   │   └── cn.txt
│   │   └── cm10/
│   │       └── cm.txt
│   │
│   ├── 2011_2012/
│   │   ├── pas212/
│   │   │   └── itpas2.txt
│   │   ├── cn12/
│   │   │   └── cn.txt
│   │   └── cm12/
│   │       └── cm.txt
│   │
│   ├── 2013_2014/
│   │   ├── pas214/
│   │   │   └── itpas2.txt
│   │   ├── cn14/
│   │   │   └── cn.txt
│   │   └── cm14/
│   │       └── cm.txt
│   │
│   ├── 2015_2016/
│   │   ├── pas216/
│   │   │   └── itpas2.txt
│   │   ├── cn16/
│   │   │   └── cn.txt
│   │   └── cm16/
│   │       └── cm.txt
│   │
│   ├── 2017_2018/
│   │   ├── pas218/
│   │   │   └── itpas2.txt
│   │   ├── cn18/
│   │   │   └── cn.txt
│   │   └── cm18/
│   │       └── cm.txt
│   │
│   └── 2019_2020/
│       ├── pas220/
│       │   └── itpas2.txt
│       ├── cn20/
│       │   └── cn.txt
│       └── cm20/
│           └── cm.txt
│
└── outputs/
    ├── aggregate/
    │   ├── aggregate_ie_time_series_no_total.png*            (report Figure 1)
    │   ├── aggregate_ie_by_source_comparison_no_total.png*   (report Figure 3)
    │   ├── aggregate_independent_expenditures_full.csv*
    │   ├── aggregate_ie_summary_by_period_party_source.csv*
    │   ├── aggregate_ie_summary_by_cycle.csv*
    │   ├── aggregate_ie_support_vs_oppose_breakdown.csv*
    │   └── aggregate_period_totals_summary.csv*
    │
    ├── senate/
    │   ├── senate_independent_expenditures_full.csv*
    │   ├── senate_ie_summary_by_period_party_source.csv*
    │   ├── senate_ie_summary_by_cycle.csv*
    │   ├── senate_ie_support_vs_oppose_breakdown.csv*
    │   └── senate_period_totals_summary.csv*
    │
    ├── presidential/
    │   └── (same five files as senate/)
    │
    ├── regressions/
    │   ├── regression_coefficients.csv*
    │   ├── regression_model_summaries.csv*
    │   ├── regression_results.md*
    │   ├── <dataset>_party_office_panel.csv*  and  <dataset>_source_panel.csv*
    │   ├── figures/figure_1_source_share_aggregate.png*      (report Figure 2)
    │   └── tables/table_1 … table_4 (.csv and .md)*
    │
    ├── robustness_check/
    │   ├── <dataset>_processed.pkl*
    │   └── regressions/ (same layout as outputs/regressions/)*
    │
    ├── other_IEs_breakdown.csv*
    └── <dataset>_processed.pkl*
```

## File Markers

`*` File will be created during execution

Download data files from https://www.fec.gov/data/browse-data/?tab=bulk-data
