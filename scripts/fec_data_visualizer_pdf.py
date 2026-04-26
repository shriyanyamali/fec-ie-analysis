import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from datetime import datetime
import pickle

sns.set_style("white")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.major.size'] = 4
plt.rcParams['ytick.major.size'] = 4
plt.rcParams['xtick.major.width'] = 0.8
plt.rcParams['ytick.major.width'] = 0.8

BAR_DEM   = '#222222'
BAR_REP   = '#888888'
BAR_TOTAL = '#CCCCCC'
BAR_EDGE  = 'black'

BAR_PRE  = '#CCCCCC'    # light grey  (pre-CU period)
BAR_POST = '#444444'    # dark grey   (post-CU period)

LINE_STYLES = {
    'Democrat':   dict(color='black',   linestyle='-',  marker='o', markersize=6, linewidth=2),
    'Republican': dict(color='#666666', linestyle='--', marker='s', markersize=6, linewidth=2),
    'Total':      dict(color='#AAAAAA', linestyle=':',  marker='^', markersize=6, linewidth=1.6),
}


def _style_ax(ax, horizontal_grid=True):
    """Apply consistent publication styling to an Axes object."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    if horizontal_grid:
        ax.yaxis.grid(True, color='#DDDDDD', linewidth=0.7, linestyle='-')
        ax.xaxis.grid(False)
    ax.set_axisbelow(True)


class FECDataVisualizer:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)

    def load_processed_data(self):
        print("Loading processed datasets...")

        datasets = {}
        for name in ['aggregate', 'senate', 'presidential']:
            filepath = self.data_dir / f'{name}_processed.pkl'
            with open(filepath, 'rb') as f:
                datasets[name] = pickle.load(f)
            print(f"  Loaded {name} dataset: {len(datasets[name]):,} records")

        self.ie_aggregate    = datasets['aggregate']
        self.ie_senate       = datasets['senate']
        self.ie_presidential = datasets['presidential']

        print("\nAll datasets loaded successfully")

    def analyze_dataset(self, data, dataset_name, output_dir):
        if len(data) == 0:
            print(f"\nNo data available for {dataset_name} analysis!")
            return

        print("\n" + "="*80)
        print(f"{dataset_name.upper()} ANALYSIS")
        print("="*80)

        self._validate_data(data, dataset_name)
        self._analyze_by_period_party_source(data, dataset_name)
        self._analyze_total_by_period_party(data, dataset_name)
        self._create_visualizations(data, dataset_name, output_dir)
        self._export_results(data, dataset_name, output_dir)

    def _validate_data(self, data, dataset_name):
        print(f"\nData Validation for {dataset_name}:")

        negative = data[data['TRANSACTION_AMT'] < 0]
        if len(negative) > 0:
            print(f"  WARNING: {len(negative)} negative amounts found!")
        else:
            print(f"  No negative amounts")

        pre_superpac = data[
            (data['PERIOD'] == 'Pre-Citizens United (2001-2010)') &
            (data['COMMITTEE_CATEGORY'] == 'Super PAC')
        ]
        if len(pre_superpac) > 0:
            print(f"  WARNING: {len(pre_superpac)} Super PAC records in pre-period!")
        else:
            print(f"  No Super PACs in pre-period")

        missing_party = data[data['BENEFITING_PARTY'].isna()]
        if len(missing_party) > 0:
            print(f"  WARNING: {len(missing_party)} missing benefiting party")
        else:
            print(f"  All records have benefiting party")

    def _analyze_by_period_party_source(self, data, dataset_name):
        print("\n" + "-"*80)
        print(f"{dataset_name}: IEs by Period, Party, and Source")
        print("-"*80)

        summary = data.groupby(
            ['PERIOD', 'BENEFITING_PARTY', 'COMMITTEE_CATEGORY']
        ).agg({
            'TRANSACTION_AMT': ['sum', 'count', 'mean', 'median'],
            'CMTE_ID': 'nunique'
        }).round(2)

        summary.columns = ['Total_Amount', 'Number_of_IEs', 'Mean_Amount',
                           'Median_Amount', 'Unique_Committees']
        summary = summary.reset_index()

        display_summary = summary.copy()
        for col in ['Total_Amount', 'Mean_Amount', 'Median_Amount']:
            display_summary[col] = display_summary[col].apply(lambda x: f'${x:,.2f}')

        print("\n", display_summary[['PERIOD', 'BENEFITING_PARTY', 'COMMITTEE_CATEGORY',
                                     'Total_Amount', 'Number_of_IEs',
                                     'Unique_Committees']].to_string(index=False))
        return summary

    def _analyze_total_by_period_party(self, data, dataset_name):
        print("\n" + "-"*80)
        print(f"{dataset_name}: Total IEs by Period and Party")
        print("-"*80)

        totals = data.groupby(['PERIOD', 'BENEFITING_PARTY']).agg({
            'TRANSACTION_AMT': ['sum', 'count'],
            'CMTE_ID': 'nunique'
        }).round(2)

        totals.columns = ['Total_Amount', 'Number_of_IEs', 'Unique_Committees']
        totals = totals.reset_index()

        try:
            pre_dem  = totals[(totals['PERIOD'] == 'Pre-Citizens United (2001-2010)') &
                              (totals['BENEFITING_PARTY'] == 'Democrat')]['Total_Amount'].values[0]
            post_dem = totals[(totals['PERIOD'] == 'Post-Citizens United (2011-2020)') &
                              (totals['BENEFITING_PARTY'] == 'Democrat')]['Total_Amount'].values[0]
            pre_rep  = totals[(totals['PERIOD'] == 'Pre-Citizens United (2001-2010)') &
                              (totals['BENEFITING_PARTY'] == 'Republican')]['Total_Amount'].values[0]
            post_rep = totals[(totals['PERIOD'] == 'Post-Citizens United (2011-2020)') &
                              (totals['BENEFITING_PARTY'] == 'Republican')]['Total_Amount'].values[0]

            dem_increase = ((post_dem - pre_dem) / pre_dem * 100) if pre_dem > 0 else 0
            rep_increase = ((post_rep - pre_rep) / pre_rep * 100) if pre_rep > 0 else 0

            display_totals = totals.copy()
            display_totals['Total_Amount'] = display_totals['Total_Amount'].apply(lambda x: f'${x:,.2f}')

            print("\n", display_totals.to_string(index=False))
            print(f"\nDemocrat increase:   {dem_increase:.1f}% (${pre_dem:,.0f} to ${post_dem:,.0f})")
            print(f"Republican increase: {rep_increase:.1f}% (${pre_rep:,.0f} to ${post_rep:,.0f})")
        except (IndexError, KeyError) as e:
            print("\nUnable to calculate increases - insufficient data")

        return totals

    def _create_visualizations(self, data, dataset_name, output_dir):
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        print(f"\nCreating visualizations for {dataset_name}...")
        prefix = dataset_name.lower()

        period_party_totals_base = (
            data.groupby(['PERIOD', 'BENEFITING_PARTY'])['TRANSACTION_AMT']
                .sum().reset_index()
        )

        for include_total, suffix in [(True, ''), (False, '_no_total')]:
            fig, ax = plt.subplots(figsize=(12, 7))

            ppt = period_party_totals_base.copy()
            if include_total:
                pt = data.groupby('PERIOD')['TRANSACTION_AMT'].sum().reset_index()
                pt['BENEFITING_PARTY'] = 'Total'
                ppt = pd.concat([ppt, pt], ignore_index=True)

            parties = ([c for c in ['Democrat', 'Republican', 'Total']
                        if c in ppt['BENEFITING_PARTY'].unique()]
                       if include_total else
                       [c for c in ['Democrat', 'Republican']
                        if c in ppt['BENEFITING_PARTY'].unique()])
            bar_colors = {'Democrat': BAR_DEM, 'Republican': BAR_REP, 'Total': BAR_TOTAL}

            pivot = ppt[ppt['BENEFITING_PARTY'].isin(parties)].pivot(
                index='PERIOD', columns='BENEFITING_PARTY', values='TRANSACTION_AMT'
            )[parties]

            pivot.plot(
                kind='bar', ax=ax, 
                color=[bar_colors[p] for p in parties],
                edgecolor=BAR_EDGE, linewidth=0.6, width=0.6
            )

            ax.set_xlabel('Period', fontsize=12)
            ax.set_ylabel('Total Amount ($)', fontsize=12)
            ax.legend(title='Benefiting Party', fontsize=10,
                      frameon=True, framealpha=1, edgecolor='#CCCCCC')
            ax.tick_params(axis='x', rotation=0)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M'))
            _style_ax(ax)

            plt.tight_layout()
            fname = f'{prefix}_total_ie_by_period_party{suffix}.pdf'
            plt.savefig(output_path / fname, bbox_inches='tight')
            print(f"  Saved: {fname}")
            plt.close()

        for include_total, suffix in [(True, ''), (False, '_no_total')]:
            fig, axes = plt.subplots(1, 2, figsize=(16, 7))

            for idx, period in enumerate(['Pre-Citizens United (2001-2010)',
                                          'Post-Citizens United (2011-2020)']):
                period_data = data[data['PERIOD'] == period]

                sp = (period_data.groupby(['COMMITTEE_CATEGORY', 'BENEFITING_PARTY'])
                                 ['TRANSACTION_AMT'].sum().reset_index())

                if include_total:
                    st = (period_data.groupby('COMMITTEE_CATEGORY')['TRANSACTION_AMT']
                                     .sum().reset_index())
                    st['BENEFITING_PARTY'] = 'Total'
                    sp = pd.concat([sp, st], ignore_index=True)

                parties = ([c for c in ['Democrat', 'Republican', 'Total']
                            if c in sp['BENEFITING_PARTY'].unique()]
                           if include_total else
                           [c for c in ['Democrat', 'Republican']
                            if c in sp['BENEFITING_PARTY'].unique()])
                bar_colors = {'Democrat': BAR_DEM, 'Republican': BAR_REP, 'Total': BAR_TOTAL}

                pivot = sp[sp['BENEFITING_PARTY'].isin(parties)].pivot(
                    index='COMMITTEE_CATEGORY', columns='BENEFITING_PARTY',
                    values='TRANSACTION_AMT'
                ).fillna(0)[parties]

                pivot.plot(
                    kind='barh', ax=axes[idx],
                    color=[bar_colors[p] for p in parties],
                    edgecolor=BAR_EDGE, linewidth=0.6, width=0.6
                )

                titles = {0: 'Pre-Citizens United (2001-2010)',
                          1: 'Post-Citizens United (2011-2020)'}
                axes[idx].set_title(titles[idx], fontsize=12, fontweight='bold', pad=10)
                axes[idx].set_xlabel('Total Amount ($)', fontsize=11)
                axes[idx].set_ylabel('Committee Type', fontsize=11)
                axes[idx].legend(title='Benefiting Party', fontsize=9,
                                 frameon=True, framealpha=1, edgecolor='#CCCCCC')
                axes[idx].xaxis.set_major_formatter(
                    plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M')
                )
                _style_ax(axes[idx], horizontal_grid=False)
                axes[idx].xaxis.grid(True, color='#DDDDDD', linewidth=0.7)
                axes[idx].yaxis.grid(False)

            plt.tight_layout()
            fname = f'{prefix}_ie_by_source_comparison{suffix}.pdf'
            plt.savefig(output_path / fname, bbox_inches='tight')
            print(f"  Saved: {fname}")
            plt.close()

        cycle_party_base = (
            data.groupby(['CYCLE_END_YEAR', 'BENEFITING_PARTY'])['TRANSACTION_AMT']
                .sum().reset_index()
        )
        cycle_years = sorted(data['CYCLE_END_YEAR'].dropna().unique().astype(int))

        for include_total, suffix in [(True, ''), (False, '_no_total')]:
            fig, ax = plt.subplots(figsize=(14, 7))

            cp = cycle_party_base.copy()
            if include_total:
                ct = data.groupby('CYCLE_END_YEAR')['TRANSACTION_AMT'].sum().reset_index()
                ct['BENEFITING_PARTY'] = 'Total'
                cp = pd.concat([cp, ct], ignore_index=True)

            parties = (['Democrat', 'Republican', 'Total'] if include_total
                       else ['Democrat', 'Republican'])

            for party in parties:
                pd_data = cp[cp['BENEFITING_PARTY'] == party]
                ax.plot(pd_data['CYCLE_END_YEAR'], pd_data['TRANSACTION_AMT'],
                        label=party, **LINE_STYLES[party])

            ax.axvline(x=2010.5, color='black', linestyle=':', linewidth=1.4,
                       label='Citizens United (Jan 2010)', alpha=0.6)

            ax.set_xlabel('Election Cycle End Year', fontsize=12)
            ax.set_ylabel('Total Amount ($)', fontsize=12)
            ax.legend(fontsize=11, frameon=True, framealpha=1, edgecolor='#CCCCCC')
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M'))
            ax.set_xticks(cycle_years)
            ax.set_xticklabels([str(y) for y in cycle_years])
            _style_ax(ax)

            plt.tight_layout()
            fname = f'{prefix}_ie_time_series{suffix}.pdf'
            plt.savefig(output_path / fname, bbox_inches='tight')
            print(f"  Saved: {fname}")
            plt.close()

        for include_total, suffix in [(True, ''), (False, '_no_total')]:
            ncols = 3 if include_total else 2
            fig, axes = plt.subplots(1, ncols, figsize=(7 * ncols, 8))

            party_list = (['Democrat', 'Republican', 'Total'] if include_total
                          else ['Democrat', 'Republican'])

            for idx, party in enumerate(party_list):
                pd_data = data if party == 'Total' else data[data['BENEFITING_PARTY'] == party]

                sp = (pd_data.groupby(['PERIOD', 'COMMITTEE_CATEGORY'])['TRANSACTION_AMT']
                              .sum().reset_index())

                pivot = sp.pivot(
                    index='COMMITTEE_CATEGORY', columns='PERIOD', values='TRANSACTION_AMT'
                ).fillna(0)

                col_order = [c for c in ['Pre-Citizens United (2001-2010)',
                                          'Post-Citizens United (2011-2020)']
                             if c in pivot.columns]
                pivot = pivot[col_order]

                pivot.plot(
                    kind='barh', ax=axes[idx],
                    color=[BAR_PRE, BAR_POST],
                    edgecolor=BAR_EDGE, linewidth=0.6, width=0.6
                )

                title = 'Total (Both Parties)' if party == 'Total' else party
                axes[idx].set_title(title, fontsize=12, fontweight='bold', pad=10)
                axes[idx].set_xlabel('Total Amount ($)', fontsize=11)
                axes[idx].set_ylabel('Committee Type', fontsize=11)

                handles, labels = axes[idx].get_legend_handles_labels()
                short_labels = ['Pre-CU (2001-2010)', 'Post-CU (2011-2020)']
                axes[idx].legend(handles, short_labels[:len(handles)],
                                 title='Period', fontsize=9,
                                 frameon=True, framealpha=1, edgecolor='#CCCCCC',
                                 loc='best')

                axes[idx].xaxis.set_major_formatter(
                    plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M')
                )
                _style_ax(axes[idx], horizontal_grid=False)
                axes[idx].xaxis.grid(True, color='#DDDDDD', linewidth=0.7)
                axes[idx].yaxis.grid(False)

            plt.tight_layout()
            fname = f'{prefix}_ie_source_by_party{suffix}.pdf'
            plt.savefig(output_path / fname, bbox_inches='tight')
            print(f"  Saved: {fname}")
            plt.close()

        print(f"All visualizations (8 files per dataset) saved to: {output_path}")

    def _export_results(self, data, dataset_name, output_dir):
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        print(f"\nExporting results for {dataset_name}...")
        prefix = dataset_name.lower()

        full_data_file = output_path / f'{prefix}_independent_expenditures_full.csv'
        with open(full_data_file, 'w') as f:
            f.write(f"# Full independent expenditure data for {dataset_name}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# Used in graphics: None (raw data file)\n")
            f.write("#\n")
        data.to_csv(full_data_file, mode='a', index=False)
        print(f"  Saved: {prefix}_independent_expenditures_full.csv ({len(data):,} records)")

        summary = data.groupby(['PERIOD', 'BENEFITING_PARTY', 'COMMITTEE_CATEGORY']).agg({
            'TRANSACTION_AMT': ['sum', 'count', 'mean', 'median'],
            'CMTE_ID': 'nunique'
        }).round(2)
        summary.columns = ['Total_Amount', 'Num_Transactions', 'Mean_Amount',
                           'Median_Amount', 'Unique_Committees']
        summary = summary.reset_index()

        for period in summary['PERIOD'].unique():
            for committee in summary['COMMITTEE_CATEGORY'].unique():
                period_cmte_data = data[
                    (data['PERIOD'] == period) &
                    (data['COMMITTEE_CATEGORY'] == committee)
                ]
                if len(period_cmte_data) > 0:
                    total_row = {
                        'PERIOD': period,
                        'BENEFITING_PARTY': 'Total',
                        'COMMITTEE_CATEGORY': committee,
                        'Total_Amount':      period_cmte_data['TRANSACTION_AMT'].sum(),
                        'Num_Transactions':  len(period_cmte_data),
                        'Mean_Amount':       period_cmte_data['TRANSACTION_AMT'].mean(),
                        'Median_Amount':     period_cmte_data['TRANSACTION_AMT'].median(),
                        'Unique_Committees': period_cmte_data['CMTE_ID'].nunique()
                    }
                    summary = pd.concat([summary, pd.DataFrame([total_row])], ignore_index=True)

        summary['Percent_Change'] = None
        for party in summary['BENEFITING_PARTY'].unique():
            for committee in summary['COMMITTEE_CATEGORY'].unique():
                pre_data = summary[
                    (summary['PERIOD'] == 'Pre-Citizens United (2001-2010)') &
                    (summary['BENEFITING_PARTY'] == party) &
                    (summary['COMMITTEE_CATEGORY'] == committee)
                ]
                post_data = summary[
                    (summary['PERIOD'] == 'Post-Citizens United (2011-2020)') &
                    (summary['BENEFITING_PARTY'] == party) &
                    (summary['COMMITTEE_CATEGORY'] == committee)
                ]
                if len(pre_data) > 0 and len(post_data) > 0:
                    pre_amount  = pre_data['Total_Amount'].values[0]
                    post_amount = post_data['Total_Amount'].values[0]
                    if pre_amount > 0:
                        pct_change = ((post_amount - pre_amount) / pre_amount) * 100
                        mask = (
                            (summary['PERIOD'] == 'Post-Citizens United (2011-2020)') &
                            (summary['BENEFITING_PARTY'] == party) &
                            (summary['COMMITTEE_CATEGORY'] == committee)
                        )
                        summary.loc[mask, 'Percent_Change'] = round(pct_change, 2)

        summary_file = output_path / f'{prefix}_ie_summary_by_period_party_source.csv'
        with open(summary_file, 'w') as f:
            f.write(f"# Summary of independent expenditures by period, party, and committee source for {dataset_name}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Used in graphics: {prefix}_ie_by_source_comparison.pdf, {prefix}_ie_source_by_party.pdf\n")
            f.write("# Percent_Change shows the percentage change from pre to post Citizens United period\n")
            f.write("#\n")
        summary.to_csv(summary_file, mode='a', index=False)
        print(f"  Saved: {prefix}_ie_summary_by_period_party_source.csv")

        cycle_summary = data.groupby(['CYCLE', 'CYCLE_END_YEAR', 'BENEFITING_PARTY']).agg({
            'TRANSACTION_AMT': ['sum', 'count'],
            'CMTE_ID': 'nunique'
        }).round(2)
        cycle_summary.columns = ['Total_Amount', 'Num_Transactions', 'Unique_Committees']
        cycle_summary = cycle_summary.reset_index()

        for cycle in cycle_summary[['CYCLE', 'CYCLE_END_YEAR']].drop_duplicates().values:
            cycle_name, cycle_year = cycle
            cycle_data = data[data['CYCLE'] == cycle_name]
            if len(cycle_data) > 0:
                total_row = {
                    'CYCLE': cycle_name,
                    'CYCLE_END_YEAR': cycle_year,
                    'BENEFITING_PARTY': 'Total',
                    'Total_Amount':      cycle_data['TRANSACTION_AMT'].sum(),
                    'Num_Transactions':  len(cycle_data),
                    'Unique_Committees': cycle_data['CMTE_ID'].nunique()
                }
                cycle_summary = pd.concat([cycle_summary, pd.DataFrame([total_row])], ignore_index=True)

        cycle_summary = cycle_summary.sort_values(['BENEFITING_PARTY', 'CYCLE_END_YEAR'])
        cycle_summary['Percent_Change_From_Previous'] = None

        for party in cycle_summary['BENEFITING_PARTY'].unique():
            party_data = cycle_summary[cycle_summary['BENEFITING_PARTY'] == party].copy()
            party_data['Percent_Change_From_Previous'] = party_data['Total_Amount'].pct_change() * 100
            cycle_summary.loc[cycle_summary['BENEFITING_PARTY'] == party, 'Percent_Change_From_Previous'] = \
                party_data['Percent_Change_From_Previous'].values

        cycle_summary['Percent_Change_From_Previous'] = pd.to_numeric(
            cycle_summary['Percent_Change_From_Previous'], errors='coerce'
        ).round(2)

        period_totals_rows = []
        for party in ['Democrat', 'Republican', 'Total']:
            if party == 'Total':
                pre_data  = data[data['PERIOD'] == 'Pre-Citizens United (2001-2010)']
                post_data = data[data['PERIOD'] == 'Post-Citizens United (2011-2020)']
                all_data  = data
            else:
                pre_data  = data[(data['PERIOD'] == 'Pre-Citizens United (2001-2010)') &
                                 (data['BENEFITING_PARTY'] == party)]
                post_data = data[(data['PERIOD'] == 'Post-Citizens United (2011-2020)') &
                                 (data['BENEFITING_PARTY'] == party)]
                all_data  = data[data['BENEFITING_PARTY'] == party]

            for label, d in [('2001-2010 TOTAL', pre_data),
                              ('2011-2020 TOTAL', post_data),
                              ('2001-2020 TOTAL', all_data)]:
                period_totals_rows.append({
                    'CYCLE': label, 'CYCLE_END_YEAR': None,
                    'BENEFITING_PARTY': party,
                    'Total_Amount':      d['TRANSACTION_AMT'].sum(),
                    'Num_Transactions':  len(d),
                    'Unique_Committees': d['CMTE_ID'].nunique(),
                    'Percent_Change_From_Previous': None
                })

        period_totals_df = pd.DataFrame(period_totals_rows)
        cycle_summary = pd.concat([cycle_summary, period_totals_df], ignore_index=True)

        cycle_file = output_path / f'{prefix}_ie_summary_by_cycle.csv'
        with open(cycle_file, 'w') as f:
            f.write(f"# Cycle-by-cycle summary of independent expenditures for {dataset_name}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Used in graphics: {prefix}_ie_time_series.pdf, {prefix}_total_ie_by_period_party.pdf\n")
            f.write("# Percent_Change_From_Previous shows the percentage change from the previous election cycle\n")
            f.write("# Includes period totals at the end: 2001-2010 TOTAL, 2011-2020 TOTAL, 2001-2020 TOTAL\n")
            f.write("#\n")
        cycle_summary.to_csv(cycle_file, mode='a', index=False)
        print(f"  Saved: {prefix}_ie_summary_by_cycle.csv")

        support_oppose = data.groupby(['PERIOD', 'BENEFITING_PARTY', 'IE_TYPE']).agg({
            'TRANSACTION_AMT': ['sum', 'count']
        }).round(2)
        support_oppose.columns = ['Total_Amount', 'Num_Transactions']
        support_oppose = support_oppose.reset_index()

        for period in support_oppose['PERIOD'].unique():
            for party in support_oppose['BENEFITING_PARTY'].unique():
                period_party_data = data[
                    (data['PERIOD'] == period) &
                    (data['BENEFITING_PARTY'] == party)
                ]
                if len(period_party_data) > 0:
                    total_row = {
                        'PERIOD': period,
                        'BENEFITING_PARTY': party,
                        'IE_TYPE': 'Total',
                        'Total_Amount':     period_party_data['TRANSACTION_AMT'].sum(),
                        'Num_Transactions': len(period_party_data)
                    }
                    support_oppose = pd.concat([support_oppose, pd.DataFrame([total_row])], ignore_index=True)

        support_file = output_path / f'{prefix}_ie_support_vs_oppose_breakdown.csv'
        with open(support_file, 'w') as f:
            f.write(f"# Breakdown of supporting vs opposing independent expenditures for {dataset_name}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# Used in graphics: None (supplementary analysis file)\n")
            f.write("#\n")
        support_oppose.to_csv(support_file, mode='a', index=False)
        print(f"  Saved: {prefix}_ie_support_vs_oppose_breakdown.csv")

        period_totals_summary = []
        for party in ['Democrat', 'Republican', 'Total']:
            if party == 'Total':
                pre_data  = data[data['PERIOD'] == 'Pre-Citizens United (2001-2010)']
                post_data = data[data['PERIOD'] == 'Post-Citizens United (2011-2020)']
                all_data  = data
            else:
                pre_data  = data[(data['PERIOD'] == 'Pre-Citizens United (2001-2010)') &
                                 (data['BENEFITING_PARTY'] == party)]
                post_data = data[(data['PERIOD'] == 'Post-Citizens United (2011-2020)') &
                                 (data['BENEFITING_PARTY'] == party)]
                all_data  = data[data['BENEFITING_PARTY'] == party]

            pre_total  = pre_data['TRANSACTION_AMT'].sum()
            pre_count  = len(pre_data)
            pre_cmte   = pre_data['CMTE_ID'].nunique()
            post_total = post_data['TRANSACTION_AMT'].sum()
            post_count = len(post_data)
            post_cmte  = post_data['CMTE_ID'].nunique()
            overall_total = all_data['TRANSACTION_AMT'].sum()
            overall_count = len(all_data)
            overall_cmte  = all_data['CMTE_ID'].nunique()
            absolute_change = post_total - pre_total
            percent_change  = ((post_total - pre_total) / pre_total * 100) if pre_total > 0 else None

            period_totals_summary.append({
                'Party': party, 'Period': '2001-2010 (Pre-Citizens United)',
                'Total_Amount':      pre_total,
                'Num_Transactions':  pre_count,
                'Unique_Committees': pre_cmte,
                'Mean_Amount':   pre_data['TRANSACTION_AMT'].mean()   if len(pre_data) > 0 else 0,
                'Median_Amount': pre_data['TRANSACTION_AMT'].median() if len(pre_data) > 0 else 0
            })
            period_totals_summary.append({
                'Party': party, 'Period': '2011-2020 (Post-Citizens United)',
                'Total_Amount':      post_total,
                'Num_Transactions':  post_count,
                'Unique_Committees': post_cmte,
                'Mean_Amount':   post_data['TRANSACTION_AMT'].mean()   if len(post_data) > 0 else 0,
                'Median_Amount': post_data['TRANSACTION_AMT'].median() if len(post_data) > 0 else 0
            })
            period_totals_summary.append({
                'Party': party, 'Period': '2001-2020 (Overall)',
                'Total_Amount':      overall_total,
                'Num_Transactions':  overall_count,
                'Unique_Committees': overall_cmte,
                'Mean_Amount':   all_data['TRANSACTION_AMT'].mean()   if len(all_data) > 0 else 0,
                'Median_Amount': all_data['TRANSACTION_AMT'].median() if len(all_data) > 0 else 0
            })
            period_totals_summary.append({
                'Party': party, 'Period': 'Change (2001-2010 to 2011-2020)',
                'Total_Amount':      absolute_change,
                'Num_Transactions':  post_count - pre_count,
                'Unique_Committees': post_cmte - pre_cmte,
                'Mean_Amount':   (post_data['TRANSACTION_AMT'].mean() - pre_data['TRANSACTION_AMT'].mean())
                                 if len(pre_data) > 0 and len(post_data) > 0 else 0,
                'Median_Amount': (post_data['TRANSACTION_AMT'].median() - pre_data['TRANSACTION_AMT'].median())
                                 if len(pre_data) > 0 and len(post_data) > 0 else 0
            })
            period_totals_summary.append({
                'Party': party, 'Period': 'Percent Change (2001-2010 to 2011-2020)',
                'Total_Amount':      percent_change,
                'Num_Transactions':  ((post_count - pre_count) / pre_count * 100) if pre_count > 0 else None,
                'Unique_Committees': ((post_cmte - pre_cmte) / pre_cmte * 100) if pre_cmte > 0 else None,
                'Mean_Amount':   ((post_data['TRANSACTION_AMT'].mean() - pre_data['TRANSACTION_AMT'].mean()) /
                                   pre_data['TRANSACTION_AMT'].mean() * 100)
                                 if len(pre_data) > 0 and pre_data['TRANSACTION_AMT'].mean() > 0
                                    and len(post_data) > 0 else None,
                'Median_Amount': ((post_data['TRANSACTION_AMT'].median() - pre_data['TRANSACTION_AMT'].median()) /
                                   pre_data['TRANSACTION_AMT'].median() * 100)
                                 if len(pre_data) > 0 and pre_data['TRANSACTION_AMT'].median() > 0
                                    and len(post_data) > 0 else None
            })

        period_totals_df = pd.DataFrame(period_totals_summary).round(2)

        totals_file = output_path / f'{prefix}_period_totals_summary.csv'
        with open(totals_file, 'w') as f:
            f.write(f"# Period totals summary for {dataset_name}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# Shows totals for Pre-CU (2001-2010), Post-CU (2011-2020), Overall (2001-2020),\n")
            f.write("# absolute change, and percent change for each party and overall total\n")
            f.write("# Used in graphics: Can be referenced in all graphics for overall context\n")
            f.write("#\n")
        period_totals_df.to_csv(totals_file, mode='a', index=False)
        print(f"  Saved: {prefix}_period_totals_summary.csv")
        print(f"All results exported to: {output_path}")


def main():
    print("="*80)
    print("FEC Independent Expenditure Data Visualizer")
    print("="*80)

    data_dir = 'C:/Users/sruja/Downloads/Code/FEC IE Analysis/outputs'
    visualizer = FECDataVisualizer(data_dir)
    visualizer.load_processed_data()

    print("\n" + "="*80)
    print("RUNNING SEPARATE ANALYSES")
    print("="*80)

    print("\nAGGREGATE ANALYSIS (Senate + Presidential)")
    visualizer.analyze_dataset(visualizer.ie_aggregate, 'Aggregate',
                               Path(data_dir) / 'aggregate')

    print("\nSENATE ANALYSIS")
    visualizer.analyze_dataset(visualizer.ie_senate, 'Senate',
                               Path(data_dir) / 'senate')

    print("\nPRESIDENTIAL ANALYSIS")
    visualizer.analyze_dataset(visualizer.ie_presidential, 'Presidential',
                               Path(data_dir) / 'presidential')

    print("\n" + "="*80)
    print("ALL ANALYSES COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()