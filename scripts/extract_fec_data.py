import pandas as pd
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set up plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

class FECDataAnalyzer:
    def __init__(self, data_dir):
        """
        Initialize the FEC data analyzer
        
        Parameters:
        -----------
        data_dir : str
            Path to the directory containing FEC data folders
        """
        self.data_dir = Path(data_dir)
        self.header_dir = self.data_dir / 'fec_data_file_headers'
        
        # Load header files to understand data structure
        self.load_headers()
        
        # Storage for processed data
        self.pas2_data = []
        self.cn_data = []
        self.cm_data = []
    
    def load_headers(self):
        """Load FEC header files to understand column names"""
        try:
            # Load header files
            pas2_header_df = pd.read_csv(self.header_dir / 'pas2_header_file.csv')
            cn_header_df = pd.read_csv(self.header_dir / 'cn_header_file.csv')
            cm_header_df = pd.read_csv(self.header_dir / 'cm_header_file.csv')
            
            # Extract column names - header files contain column names as columns
            self.pas2_cols = list(pas2_header_df.columns)
            self.cn_cols = list(cn_header_df.columns)
            self.cm_cols = list(cm_header_df.columns)
            
            print("Header files loaded successfully!")
            print(f"\nPAS2 (IE) columns ({len(self.pas2_cols)}): {self.pas2_cols[:10]}... (showing first 10)")
            print(f"\nCandidate Master columns ({len(self.cn_cols)}): {self.cn_cols[:10]}... (showing first 10)")
            print(f"\nCommittee Master columns ({len(self.cm_cols)}): {self.cm_cols[:10]}... (showing first 10)")
            
        except Exception as e:
            print(f"Error loading headers: {e}")
            print("Using default column names based on FEC documentation...")
            self.setup_default_headers()
    
    def setup_default_headers(self):
        """Set up default column names based on FEC documentation"""
        self.pas2_cols = [
            'CMTE_ID', 'AMNDT_IND', 'RPT_TP', 'TRANSACTION_PGI', 'IMAGE_NUM',
            'TRANSACTION_TP', 'ENTITY_TP', 'NAME', 'CITY', 'STATE', 'ZIP_CODE',
            'EMPLOYER', 'OCCUPATION', 'TRANSACTION_DT', 'TRANSACTION_AMT',
            'OTHER_ID', 'CAND_ID', 'TRAN_ID', 'FILE_NUM', 'MEMO_CD', 'MEMO_TEXT',
            'SUB_ID'
        ]
        
        self.cn_cols = [
            'CAND_ID', 'CAND_NAME', 'CAND_PTY_AFFILIATION', 'CAND_ELECTION_YR',
            'CAND_OFFICE_ST', 'CAND_OFFICE', 'CAND_OFFICE_DISTRICT', 'CAND_ICI',
            'CAND_STATUS', 'CAND_PCC', 'CAND_ST1', 'CAND_ST2', 'CAND_CITY',
            'CAND_ST', 'CAND_ZIP'
        ]
        
        self.cm_cols = [
            'CMTE_ID', 'CMTE_NM', 'TRES_NM', 'CMTE_ST1', 'CMTE_ST2', 'CMTE_CITY',
            'CMTE_ST', 'CMTE_ZIP', 'CMTE_DSGN', 'CMTE_TP', 'CMTE_PTY_AFFILIATION',
            'CMTE_FILING_FREQ', 'ORG_TP', 'CONNECTED_ORG_NM', 'CAND_ID'
        ]
    
    def load_cycle_data(self, start_year, end_year):
        """Load data for a specific election cycle"""
        cycle_dir = self.data_dir / f'{start_year}_{end_year}'
        
        print(f"\nLoading data for {start_year}-{end_year} cycle...")
        
        # Load PAS2 (Independent Expenditures & Committee Contributions)
        pas2_dir = cycle_dir / f'pas2{str(end_year)[-2:]}'
        pas2_file = pas2_dir / 'itpas2.txt'
        
        if pas2_file.exists():
            try:
                df = pd.read_csv(pas2_file, sep='|', header=None, 
                                names=self.pas2_cols, low_memory=False,
                                encoding='latin-1', on_bad_lines='skip')
                df['CYCLE'] = f'{start_year}-{end_year}'
                df['CYCLE_END_YEAR'] = end_year
                self.pas2_data.append(df)
                print(f"  ✓ Loaded {len(df):,} PAS2 records")
            except Exception as e:
                print(f"  ❌ Error loading PAS2 data: {e}")
        
        # Load Candidate Master
        cn_dir = cycle_dir / f'cn{str(end_year)[-2:]}'
        cn_file = cn_dir / 'cn.txt'
        
        if cn_file.exists():
            try:
                df = pd.read_csv(cn_file, sep='|', header=None,
                                names=self.cn_cols, low_memory=False,
                                encoding='latin-1', on_bad_lines='skip')
                df['CYCLE'] = f'{start_year}-{end_year}'
                self.cn_data.append(df)
                print(f"  ✓ Loaded {len(df):,} candidate records")
            except Exception as e:
                print(f"  ❌ Error loading candidate data: {e}")
        
        # Load Committee Master
        cm_dir = cycle_dir / f'cm{str(end_year)[-2:]}'
        cm_file = cm_dir / 'cm.txt'
        
        if cm_file.exists():
            try:
                df = pd.read_csv(cm_file, sep='|', header=None,
                                names=self.cm_cols, low_memory=False,
                                encoding='latin-1', on_bad_lines='skip')
                df['CYCLE'] = f'{start_year}-{end_year}'
                self.cm_data.append(df)
                print(f"  ✓ Loaded {len(df):,} committee records")
            except Exception as e:
                print(f"  ❌ Error loading committee data: {e}")
    
    def load_all_cycles(self):
        """Load data for all cycles from 2002 to 2020"""
        cycles = [
            (2001, 2002), (2003, 2004), (2005, 2006), (2007, 2008),
            (2009, 2010), (2011, 2012), (2013, 2014), (2015, 2016),
            (2017, 2018), (2019, 2020)
        ]
        
        for start_year, end_year in cycles:
            self.load_cycle_data(start_year, end_year)
        
        # Combine all cycles
        print("\nCombining all cycles...")
        if self.pas2_data:
            self.pas2_combined = pd.concat(self.pas2_data, ignore_index=True)
            print(f"✓ Total PAS2 records: {len(self.pas2_combined):,}")
        else:
            print("⚠️  No PAS2 data loaded!")
            self.pas2_combined = pd.DataFrame()
        
        if self.cn_data:
            self.cn_combined = pd.concat(self.cn_data, ignore_index=True)
            print(f"✓ Total candidate records: {len(self.cn_combined):,}")
        else:
            print("⚠️  No candidate data loaded!")
            self.cn_combined = pd.DataFrame()
        
        if self.cm_data:
            self.cm_combined = pd.concat(self.cm_data, ignore_index=True)
            print(f"✓ Total committee records: {len(self.cm_combined):,}")
        else:
            print("⚠️  No committee data loaded!")
            self.cm_combined = pd.DataFrame()
    
    def identify_independent_expenditures(self):
        """Identify independent expenditures from the PAS2 data"""
        print("\nIdentifying independent expenditures...")
        
        if len(self.pas2_combined) == 0:
            print("❌ No PAS2 data available to analyze!")
            return pd.DataFrame()
        
        # Filter for independent expenditure transaction types ONLY
        ie_mask = self.pas2_combined['TRANSACTION_TP'].isin(['24E', '24A', '24N'])
        self.ie_data = self.pas2_combined[ie_mask].copy()
        
        print(f"✓ Found {len(self.ie_data):,} independent expenditure records")
        
        # Convert amount to numeric and FILTER OUT NEGATIVE VALUES
        self.ie_data['TRANSACTION_AMT'] = pd.to_numeric(
            self.ie_data['TRANSACTION_AMT'], errors='coerce'
        )
        
        # Check for negative values
        negative_count = (self.ie_data['TRANSACTION_AMT'] < 0).sum()
        if negative_count > 0:
            print(f"\n⚠️  Found {negative_count:,} negative transaction amounts - removing them")
            negative_total = self.ie_data[self.ie_data['TRANSACTION_AMT'] < 0]['TRANSACTION_AMT'].sum()
            print(f"    Total negative amount: ${negative_total:,.2f}")
            
            # Remove negative amounts
            self.ie_data = self.ie_data[self.ie_data['TRANSACTION_AMT'] >= 0].copy()
            print(f"    Remaining records after removing negatives: {len(self.ie_data):,}")
        
        # Create support/oppose indicator
        self.ie_data['IE_TYPE'] = self.ie_data['TRANSACTION_TP'].map({
            '24E': 'SUPPORT',
            '24A': 'OPPOSE',
            '24N': 'SUPPORT'
        })
        
        # Show breakdown
        print("\n  IE Type Breakdown:")
        ie_breakdown = self.ie_data.groupby('TRANSACTION_TP').agg({
            'TRANSACTION_AMT': ['count', 'sum']
        })
        for tp in ie_breakdown.index:
            count = ie_breakdown.loc[tp, ('TRANSACTION_AMT', 'count')]
            total = ie_breakdown.loc[tp, ('TRANSACTION_AMT', 'sum')]
            tp_name = {'24E': 'Supporting', '24A': 'Opposing', '24N': 'Supporting (24N)'}
            print(f"    {tp} ({tp_name.get(tp, 'Unknown')}): {count:,} transactions, ${total:,.2f}")
        
        return self.ie_data
    
    def merge_candidate_info(self):
        """Merge candidate information to identify party and office"""
        print("\nMerging candidate information...")
        
        if len(self.ie_data) == 0:
            print("❌ No IE data to merge!")
            return pd.DataFrame()
        
        if len(self.cn_combined) == 0:
            print("❌ No candidate data available!")
            return pd.DataFrame()
        
        # Get unique candidate info
        cn_unique = self.cn_combined.sort_values('CAND_ELECTION_YR', ascending=False)\
                                    .drop_duplicates(subset=['CAND_ID'], keep='first')
        
        # Merge with IE data
        self.ie_data = self.ie_data.merge(
            cn_unique[['CAND_ID', 'CAND_NAME', 'CAND_PTY_AFFILIATION', 
                      'CAND_OFFICE', 'CAND_OFFICE_ST']],
            on='CAND_ID',
            how='left'
        )
        
        # Map party codes to full names
        party_map = {
            'DEM': 'Democrat',
            'REP': 'Republican',
            'IND': 'Independent',
            'LIB': 'Libertarian',
            'GRE': 'Green',
            '': 'Unknown'
        }
        self.ie_data['CANDIDATE_PARTY'] = self.ie_data['CAND_PTY_AFFILIATION'].map(
            lambda x: party_map.get(x, 'Other')
        )
        
        # Calculate benefiting party
        print("\n🔧 Calculating benefiting party for each IE...")
        
        def calculate_benefiting_party(row):
            candidate_party = row['CANDIDATE_PARTY']
            ie_type = row['IE_TYPE']
            
            if ie_type == 'SUPPORT':
                return candidate_party
            elif ie_type == 'OPPOSE':
                if candidate_party == 'Democrat':
                    return 'Republican'
                elif candidate_party == 'Republican':
                    return 'Democrat'
                else:
                    return 'Unknown'
            else:
                return 'Unknown'
        
        self.ie_data['BENEFITING_PARTY'] = self.ie_data.apply(
            calculate_benefiting_party, axis=1
        )
        
        # Show the correction in action
        print("\n  IE Assignment Summary:")
        support_dem = len(self.ie_data[(self.ie_data['IE_TYPE'] == 'SUPPORT') & 
                                       (self.ie_data['CANDIDATE_PARTY'] == 'Democrat')])
        support_rep = len(self.ie_data[(self.ie_data['IE_TYPE'] == 'SUPPORT') & 
                                       (self.ie_data['CANDIDATE_PARTY'] == 'Republican')])
        oppose_dem = len(self.ie_data[(self.ie_data['IE_TYPE'] == 'OPPOSE') & 
                                      (self.ie_data['CANDIDATE_PARTY'] == 'Democrat')])
        oppose_rep = len(self.ie_data[(self.ie_data['IE_TYPE'] == 'OPPOSE') & 
                                      (self.ie_data['CANDIDATE_PARTY'] == 'Republican')])
        
        print(f"    Supporting Democrats: {support_dem:,} → Benefits Democrats")
        print(f"    Supporting Republicans: {support_rep:,} → Benefits Republicans")
        print(f"    Opposing Democrats: {oppose_dem:,} → Benefits Republicans ⚠️ FLIPPED")
        print(f"    Opposing Republicans: {oppose_rep:,} → Benefits Democrats ⚠️ FLIPPED")
        
        benefit_dem = len(self.ie_data[self.ie_data['BENEFITING_PARTY'] == 'Democrat'])
        benefit_rep = len(self.ie_data[self.ie_data['BENEFITING_PARTY'] == 'Republican'])
        print(f"\n  Net Benefiting Party:")
        print(f"    Democrats: {benefit_dem:,}")
        print(f"    Republicans: {benefit_rep:,}")
        
        # Filter for Senate and Presidential races
        self.ie_data_filtered = self.ie_data[
            self.ie_data['CAND_OFFICE'].isin(['S', 'P'])
        ].copy()
        
        print(f"\n✓ Records for Senate/Presidential races: {len(self.ie_data_filtered):,}")
        
        # Create separate datasets for Senate and Presidential
        self.ie_data_senate = self.ie_data[
            self.ie_data['CAND_OFFICE'] == 'S'
        ].copy()
        
        self.ie_data_presidential = self.ie_data[
            self.ie_data['CAND_OFFICE'] == 'P'
        ].copy()
        
        print(f"  - Senate only: {len(self.ie_data_senate):,}")
        print(f"  - Presidential only: {len(self.ie_data_presidential):,}")
        
        return self.ie_data_filtered
    
    def merge_committee_info(self):
        """Merge committee information to identify source of expenditures"""
        print("\nMerging committee information...")
        
        if len(self.cm_combined) == 0:
            print("❌ No committee data available!")
            return pd.DataFrame()
        
        # Get unique committee info
        cm_unique = self.cm_combined.drop_duplicates(subset=['CMTE_ID'], keep='last')
        
        # Categorize committee types function
        def categorize_committee(row):
            cmte_tp = row.get('CMTE_TP', '')
            cmte_dsgn = row.get('CMTE_DSGN', '')
            
            if cmte_tp == 'O':
                return 'Super PAC'
            elif cmte_tp in ['N', 'Q', 'V']:
                return 'Traditional PAC'
            elif cmte_tp == 'U':
                return 'Individual IE Committee'
            elif cmte_tp in ['X', 'Y', 'Z']:
                return 'Party Committee'
            elif cmte_tp in ['H', 'S', 'P']:
                return 'Candidate Committee'
            else:
                return 'Other/Unknown'
        
        # Merge for all three datasets
        for dataset_name, dataset in [
            ('ie_data_filtered', self.ie_data_filtered),
            ('ie_data_senate', self.ie_data_senate),
            ('ie_data_presidential', self.ie_data_presidential)
        ]:
            if len(dataset) == 0:
                continue
            
            merged = dataset.merge(
                cm_unique[['CMTE_ID', 'CMTE_NM', 'CMTE_TP', 'CMTE_DSGN', 
                          'ORG_TP', 'CONNECTED_ORG_NM']],
                on='CMTE_ID',
                how='left'
            )
            
            merged['COMMITTEE_CATEGORY'] = merged.apply(categorize_committee, axis=1)
            
            # Update the dataset
            if dataset_name == 'ie_data_filtered':
                self.ie_data_filtered = merged
            elif dataset_name == 'ie_data_senate':
                self.ie_data_senate = merged
            elif dataset_name == 'ie_data_presidential':
                self.ie_data_presidential = merged
        
        print("✓ Committee information merged for all datasets")
        
        # CRITICAL: Check for Super PACs in pre-2011 data
        print("\n🔍 Checking for Super PAC activity in pre-2011 cycles...")
        for dataset_name, dataset in [
            ('Aggregate', self.ie_data_filtered),
            ('Senate', self.ie_data_senate),
            ('Presidential', self.ie_data_presidential)
        ]:
            if len(dataset) == 0:
                continue
            
            pre_2011_superpac = dataset[
                (dataset['CYCLE_END_YEAR'] <= 2010) & 
                (dataset['COMMITTEE_CATEGORY'] == 'Super PAC')
            ]
            
            if len(pre_2011_superpac) > 0:
                total_amount = pre_2011_superpac['TRANSACTION_AMT'].sum()
                print(f"\n  {dataset_name}: Found {len(pre_2011_superpac):,} Super PAC IEs in pre-2011 cycles")
                print(f"    Total amount: ${total_amount:,.2f}")
                print(f"    ⚠️  These will be EXCLUDED from analysis")
        
        return self.ie_data_filtered
    
    def create_pre_post_comparison(self):
        """Create comparison of pre- and post-Citizens United periods"""
        print("\nCreating pre/post Citizens United comparison...")
        
        # Function to add period column and apply filters
        def add_period(df):
            if len(df) == 0:
                return df
            
            # CRITICAL FIX: Exclude Super PAC spending from cycles ending in 2010 or earlier
            print(f"\n  Filtering out pre-2011 Super PAC spending...")
            pre_filter_count = len(df)
            pre_filter_superpac = df[
                (df['CYCLE_END_YEAR'] <= 2010) & 
                (df['COMMITTEE_CATEGORY'] == 'Super PAC')
            ]
            
            if len(pre_filter_superpac) > 0:
                excluded_amount = pre_filter_superpac['TRANSACTION_AMT'].sum()
                print(f"    Excluding {len(pre_filter_superpac):,} Super PAC records from pre-2011")
                print(f"    Excluded amount: ${excluded_amount:,.2f}")
                
                # Filter them out
                df = df[~(
                    (df['CYCLE_END_YEAR'] <= 2010) & 
                    (df['COMMITTEE_CATEGORY'] == 'Super PAC')
                )].copy()
                
                print(f"    Records after filter: {len(df):,} (removed {pre_filter_count - len(df):,})")
            
            # Define periods
            df['PERIOD'] = df['CYCLE_END_YEAR'].apply(
                lambda x: 'Pre-Citizens United (2002-2010)' if x <= 2010 
                else 'Post-Citizens United (2011-2020)'
            )
            
            # Focus on Democrats and Republicans
            df = df[df['BENEFITING_PARTY'].isin(['Democrat', 'Republican'])].copy()
            
            return df
        
        # Apply to all three datasets
        self.ie_aggregate = add_period(self.ie_data_filtered)
        self.ie_senate = add_period(self.ie_data_senate)
        self.ie_presidential = add_period(self.ie_data_presidential)
        
        print(f"\n✓ Final counts after all filters:")
        print(f"  Aggregate: {len(self.ie_aggregate):,}")
        print(f"  Senate: {len(self.ie_senate):,}")
        print(f"  Presidential: {len(self.ie_presidential):,}")
        
        # Verify no Super PACs in pre period
        for name, df in [('Aggregate', self.ie_aggregate), 
                        ('Senate', self.ie_senate), 
                        ('Presidential', self.ie_presidential)]:
            pre_superpac = df[
                (df['PERIOD'] == 'Pre-Citizens United (2002-2010)') & 
                (df['COMMITTEE_CATEGORY'] == 'Super PAC')
            ]
            if len(pre_superpac) > 0:
                print(f"  ⚠️  WARNING: {name} still has {len(pre_superpac)} Super PAC records in pre-period!")
            else:
                print(f"  ✓ {name}: No Super PACs in pre-period (correct)")
        
        return self.ie_aggregate
    
    def analyze_dataset(self, data, dataset_name, output_dir):
        """Run complete analysis on a specific dataset"""
        if len(data) == 0:
            print(f"\n⚠️  No data available for {dataset_name} analysis!")
            return
        
        print("\n" + "="*80)
        print(f"{dataset_name.upper()} ANALYSIS")
        print("="*80)
        
        # Data validation
        self._validate_data(data, dataset_name)
        
        # Analysis by period, party, and source
        self._analyze_by_period_party_source(data, dataset_name)
        
        # Analysis of totals by period and party
        self._analyze_total_by_period_party(data, dataset_name)
        
        # Create visualizations
        self._create_visualizations(data, dataset_name, output_dir)
        
        # Export results
        self._export_results(data, dataset_name, output_dir)
    
    def _validate_data(self, data, dataset_name):
        """Validate data quality and print warnings"""
        print(f"\n📊 Data Validation for {dataset_name}:")
        
        # Check for negative amounts
        negative = data[data['TRANSACTION_AMT'] < 0]
        if len(negative) > 0:
            print(f"  ⚠️  WARNING: {len(negative)} negative amounts found!")
        else:
            print(f"  ✓ No negative amounts")
        
        # Check for Super PACs in pre-period
        pre_superpac = data[
            (data['PERIOD'] == 'Pre-Citizens United (2002-2010)') & 
            (data['COMMITTEE_CATEGORY'] == 'Super PAC')
        ]
        if len(pre_superpac) > 0:
            print(f"  ⚠️  WARNING: {len(pre_superpac)} Super PAC records in pre-period!")
        else:
            print(f"  ✓ No Super PACs in pre-period")
        
        # Check for missing benefiting party
        missing_party = data[data['BENEFITING_PARTY'].isna()]
        if len(missing_party) > 0:
            print(f"  ⚠️  WARNING: {len(missing_party)} missing benefiting party")
        else:
            print(f"  ✓ All records have benefiting party")
    
    def _analyze_by_period_party_source(self, data, dataset_name):
        """Analyze IEs by period, party, and committee source"""
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
        
        # Format currency for display
        display_summary = summary.copy()
        for col in ['Total_Amount', 'Mean_Amount', 'Median_Amount']:
            display_summary[col] = display_summary[col].apply(lambda x: f'${x:,.2f}')
        
        print("\n", display_summary[['PERIOD', 'BENEFITING_PARTY', 'COMMITTEE_CATEGORY', 
                                     'Total_Amount', 'Number_of_IEs', 
                                     'Unique_Committees']].to_string(index=False))
        
        return summary
    
    def _analyze_total_by_period_party(self, data, dataset_name):
        """Analyze total IEs by period and party"""
        print("\n" + "-"*80)
        print(f"{dataset_name}: Total IEs by Period and Party")
        print("-"*80)
        
        totals = data.groupby(['PERIOD', 'BENEFITING_PARTY']).agg({
            'TRANSACTION_AMT': ['sum', 'count'],
            'CMTE_ID': 'nunique'
        }).round(2)
        
        totals.columns = ['Total_Amount', 'Number_of_IEs', 'Unique_Committees']
        totals = totals.reset_index()
        
        # Calculate increases
        try:
            pre_dem = totals[(totals['PERIOD'] == 'Pre-Citizens United (2002-2010)') & 
                            (totals['BENEFITING_PARTY'] == 'Democrat')]['Total_Amount'].values[0]
            post_dem = totals[(totals['PERIOD'] == 'Post-Citizens United (2011-2020)') & 
                             (totals['BENEFITING_PARTY'] == 'Democrat')]['Total_Amount'].values[0]
            
            pre_rep = totals[(totals['PERIOD'] == 'Pre-Citizens United (2002-2010)') & 
                            (totals['BENEFITING_PARTY'] == 'Republican')]['Total_Amount'].values[0]
            post_rep = totals[(totals['PERIOD'] == 'Post-Citizens United (2011-2020)') & 
                             (totals['BENEFITING_PARTY'] == 'Republican')]['Total_Amount'].values[0]
            
            dem_increase = ((post_dem - pre_dem) / pre_dem * 100) if pre_dem > 0 else 0
            rep_increase = ((post_rep - pre_rep) / pre_rep * 100) if pre_rep > 0 else 0
            
            # Format for display
            display_totals = totals.copy()
            display_totals['Total_Amount'] = display_totals['Total_Amount'].apply(lambda x: f'${x:,.2f}')
            
            print("\n", display_totals.to_string(index=False))
            print(f"\n📊 Democrat increase: {dem_increase:.1f}% (${pre_dem:,.0f} → ${post_dem:,.0f})")
            print(f"📊 Republican increase: {rep_increase:.1f}% (${pre_rep:,.0f} → ${post_rep:,.0f})")
        except (IndexError, KeyError) as e:
            print("\n⚠️  Unable to calculate increases - insufficient data")
        
        return totals
    
    def _create_visualizations(self, data, dataset_name, output_dir):
        """Create visualizations for a specific dataset - NO TITLES
        Creates TWO versions of each graphic: with totals and without totals"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        print(f"\nCreating visualizations for {dataset_name}...")
        
        prefix = dataset_name.lower()
        
        # ========================================================================
        # 1. Total IEs by Period and Party
        # ========================================================================
        
        # Prepare base data
        period_party_totals_base = data.groupby(['PERIOD', 'BENEFITING_PARTY'])\
            ['TRANSACTION_AMT'].sum().reset_index()
        
        # VERSION WITH TOTAL
        fig, ax = plt.subplots(figsize=(12, 7))
        
        period_party_totals = period_party_totals_base.copy()
        period_totals = data.groupby('PERIOD')['TRANSACTION_AMT'].sum().reset_index()
        period_totals['BENEFITING_PARTY'] = 'Total'
        period_party_totals = pd.concat([period_party_totals, period_totals], ignore_index=True)
        
        period_party_totals_pivot = period_party_totals.pivot(
            index='PERIOD', columns='BENEFITING_PARTY', values='TRANSACTION_AMT'
        )
        cols_order = [c for c in ['Democrat', 'Republican', 'Total'] if c in period_party_totals_pivot.columns]
        period_party_totals_pivot = period_party_totals_pivot[cols_order]
        
        period_party_totals_pivot.plot(kind='bar', ax=ax, color=['blue', 'red', 'gray'])
        ax.set_xlabel('Period', fontsize=12)
        ax.set_ylabel('Total Amount ($)', fontsize=12)
        ax.legend(title='Benefiting Party', fontsize=10)
        ax.tick_params(axis='x', rotation=0)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M'))
        
        plt.tight_layout()
        plt.savefig(output_path / f'{prefix}_total_ie_by_period_party.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {prefix}_total_ie_by_period_party.png (with total)")
        plt.close()
        
        # VERSION WITHOUT TOTAL
        fig, ax = plt.subplots(figsize=(12, 7))
        
        period_party_pivot_no_total = period_party_totals_base.pivot(
            index='PERIOD', columns='BENEFITING_PARTY', values='TRANSACTION_AMT'
        )
        cols_order = [c for c in ['Democrat', 'Republican'] if c in period_party_pivot_no_total.columns]
        period_party_pivot_no_total = period_party_pivot_no_total[cols_order]
        
        period_party_pivot_no_total.plot(kind='bar', ax=ax, color=['blue', 'red'])
        ax.set_xlabel('Period', fontsize=12)
        ax.set_ylabel('Total Amount ($)', fontsize=12)
        ax.legend(title='Benefiting Party', fontsize=10)
        ax.tick_params(axis='x', rotation=0)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M'))
        
        plt.tight_layout()
        plt.savefig(output_path / f'{prefix}_total_ie_by_period_party_no_total.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {prefix}_total_ie_by_period_party_no_total.png (without total)")
        plt.close()
        
        # ========================================================================
        # 2. IEs by Committee Source
        # ========================================================================
        
        # VERSION WITH TOTAL
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        
        for idx, period in enumerate(['Pre-Citizens United (2002-2010)', 
                                     'Post-Citizens United (2011-2020)']):
            period_data = data[data['PERIOD'] == period]
            
            source_party = period_data.groupby(['COMMITTEE_CATEGORY', 'BENEFITING_PARTY'])\
                ['TRANSACTION_AMT'].sum().reset_index()
            
            source_totals = period_data.groupby('COMMITTEE_CATEGORY')['TRANSACTION_AMT'].sum().reset_index()
            source_totals['BENEFITING_PARTY'] = 'Total'
            source_party = pd.concat([source_party, source_totals], ignore_index=True)
            
            source_party_pivot = source_party.pivot(
                index='COMMITTEE_CATEGORY', columns='BENEFITING_PARTY', values='TRANSACTION_AMT'
            ).fillna(0)
            
            cols_order = [c for c in ['Democrat', 'Republican', 'Total'] if c in source_party_pivot.columns]
            source_party_pivot = source_party_pivot[cols_order]
            
            source_party_pivot.plot(kind='barh', ax=axes[idx], color=['blue', 'red', 'gray'])
            
            # Add panel title
            if idx == 0:
                axes[idx].set_title('Pre-Citizens United (2002-2010)', fontsize=12, fontweight='bold')
            else:
                axes[idx].set_title('Post-Citizens United (2011-2020)', fontsize=12, fontweight='bold')
            
            axes[idx].set_xlabel('Total Amount ($)', fontsize=11)
            axes[idx].set_ylabel('Committee Type', fontsize=11)
            axes[idx].legend(title='Benefiting Party', fontsize=9)
            axes[idx].xaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M')
            )
        
        plt.tight_layout()
        plt.savefig(output_path / f'{prefix}_ie_by_source_comparison.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {prefix}_ie_by_source_comparison.png (with total)")
        plt.close()
        
        # VERSION WITHOUT TOTAL
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        
        for idx, period in enumerate(['Pre-Citizens United (2002-2010)', 
                                     'Post-Citizens United (2011-2020)']):
            period_data = data[data['PERIOD'] == period]
            
            source_party = period_data.groupby(['COMMITTEE_CATEGORY', 'BENEFITING_PARTY'])\
                ['TRANSACTION_AMT'].sum().reset_index()
            
            source_party_pivot = source_party.pivot(
                index='COMMITTEE_CATEGORY', columns='BENEFITING_PARTY', values='TRANSACTION_AMT'
            ).fillna(0)
            
            cols_order = [c for c in ['Democrat', 'Republican'] if c in source_party_pivot.columns]
            source_party_pivot = source_party_pivot[cols_order]
            
            source_party_pivot.plot(kind='barh', ax=axes[idx], color=['blue', 'red'])
            
            # Add panel title
            if idx == 0:
                axes[idx].set_title('Pre-Citizens United (2002-2010)', fontsize=12, fontweight='bold')
            else:
                axes[idx].set_title('Post-Citizens United (2011-2020)', fontsize=12, fontweight='bold')
            
            axes[idx].set_xlabel('Total Amount ($)', fontsize=11)
            axes[idx].set_ylabel('Committee Type', fontsize=11)
            axes[idx].legend(title='Benefiting Party', fontsize=9)
            axes[idx].xaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M')
            )
        
        plt.tight_layout()
        plt.savefig(output_path / f'{prefix}_ie_by_source_comparison_no_total.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {prefix}_ie_by_source_comparison_no_total.png (without total)")
        plt.close()
        
        # ========================================================================
        # 3. Time series by cycle
        # ========================================================================
        
        # Prepare base data
        cycle_party_base = data.groupby(['CYCLE_END_YEAR', 'BENEFITING_PARTY'])\
            ['TRANSACTION_AMT'].sum().reset_index()
        
        # VERSION WITH TOTAL
        fig, ax = plt.subplots(figsize=(14, 7))
        
        cycle_party = cycle_party_base.copy()
        cycle_totals = data.groupby('CYCLE_END_YEAR')['TRANSACTION_AMT'].sum().reset_index()
        cycle_totals['BENEFITING_PARTY'] = 'Total'
        cycle_party = pd.concat([cycle_party, cycle_totals], ignore_index=True)
        
        for party, color in [('Democrat', 'blue'), ('Republican', 'red'), ('Total', 'gray')]:
            party_data = cycle_party[cycle_party['BENEFITING_PARTY'] == party]
            linestyle = '--' if party == 'Total' else '-'
            linewidth = 3 if party == 'Total' else 2.5
            ax.plot(party_data['CYCLE_END_YEAR'], party_data['TRANSACTION_AMT'],
                   marker='o', linewidth=linewidth, markersize=8, label=party, 
                   color=color, linestyle=linestyle)
        
        ax.axvline(x=2010.5, color='black', linestyle=':', linewidth=2, 
                  label='Citizens United (Jan 2010)', alpha=0.7)
        
        ax.set_xlabel('Election Cycle End Year', fontsize=12)
        ax.set_ylabel('Total Amount ($)', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M'))
        
        plt.tight_layout()
        plt.savefig(output_path / f'{prefix}_ie_time_series.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {prefix}_ie_time_series.png (with total)")
        plt.close()
        
        # VERSION WITHOUT TOTAL
        fig, ax = plt.subplots(figsize=(14, 7))
        
        for party, color in [('Democrat', 'blue'), ('Republican', 'red')]:
            party_data = cycle_party_base[cycle_party_base['BENEFITING_PARTY'] == party]
            ax.plot(party_data['CYCLE_END_YEAR'], party_data['TRANSACTION_AMT'],
                   marker='o', linewidth=2.5, markersize=8, label=party, color=color)
        
        ax.axvline(x=2010.5, color='black', linestyle=':', linewidth=2, 
                  label='Citizens United (Jan 2010)', alpha=0.7)
        
        ax.set_xlabel('Election Cycle End Year', fontsize=12)
        ax.set_ylabel('Total Amount ($)', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M'))
        
        plt.tight_layout()
        plt.savefig(output_path / f'{prefix}_ie_time_series_no_total.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {prefix}_ie_time_series_no_total.png (without total)")
        plt.close()
        
        # ========================================================================
        # 4. Committee source breakdown by party
        # ========================================================================
        
        # VERSION WITH TOTAL (3 panels)
        fig, axes = plt.subplots(1, 3, figsize=(20, 8))
        
        for idx, party in enumerate(['Democrat', 'Republican', 'Total']):
            if party == 'Total':
                party_data = data
            else:
                party_data = data[data['BENEFITING_PARTY'] == party]
            
            source_period = party_data.groupby(['PERIOD', 'COMMITTEE_CATEGORY'])\
                ['TRANSACTION_AMT'].sum().reset_index()
            
            source_period_pivot = source_period.pivot(
                index='COMMITTEE_CATEGORY', columns='PERIOD', values='TRANSACTION_AMT'
            ).fillna(0)
            
            color = 'gray' if party == 'Total' else (['#ff7f0e', '#2ca02c'])
            source_period_pivot.plot(kind='barh', ax=axes[idx], color=color)
            
            # Add panel title
            if party == 'Total':
                axes[idx].set_title('Total (Both Parties)', fontsize=12, fontweight='bold')
            else:
                axes[idx].set_title(f'{party}', fontsize=12, fontweight='bold')
            
            axes[idx].set_xlabel('Total Amount ($)', fontsize=11)
            axes[idx].set_ylabel('Committee Type', fontsize=11)
            axes[idx].legend(title='Period', fontsize=9, loc='best')
            axes[idx].xaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M')
            )
        
        plt.tight_layout()
        plt.savefig(output_path / f'{prefix}_ie_source_by_party.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {prefix}_ie_source_by_party.png (with total)")
        plt.close()
        
        # VERSION WITHOUT TOTAL (2 panels)
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        
        for idx, party in enumerate(['Democrat', 'Republican']):
            party_data = data[data['BENEFITING_PARTY'] == party]
            
            source_period = party_data.groupby(['PERIOD', 'COMMITTEE_CATEGORY'])\
                ['TRANSACTION_AMT'].sum().reset_index()
            
            source_period_pivot = source_period.pivot(
                index='COMMITTEE_CATEGORY', columns='PERIOD', values='TRANSACTION_AMT'
            ).fillna(0)
            
            source_period_pivot.plot(kind='barh', ax=axes[idx], color=['#ff7f0e', '#2ca02c'])
            
            # Add panel title
            axes[idx].set_title(f'{party}', fontsize=12, fontweight='bold')
            
            axes[idx].set_xlabel('Total Amount ($)', fontsize=11)
            axes[idx].set_ylabel('Committee Type', fontsize=11)
            axes[idx].legend(title='Period', fontsize=9, loc='best')
            axes[idx].xaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: f'${x/1e6:.0f}M')
            )
        
        plt.tight_layout()
        plt.savefig(output_path / f'{prefix}_ie_source_by_party_no_total.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {prefix}_ie_source_by_party_no_total.png (without total)")
        plt.close()
        
        print(f"✅ All visualizations (8 files per dataset) saved to: {output_path}")
    
    def _export_results(self, data, dataset_name, output_dir):
        """Export detailed results to CSV with header comments and percent change"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        print(f"\nExporting results for {dataset_name}...")
        
        prefix = dataset_name.lower()
        
        # 1. Full IE dataset
        full_data_file = output_path / f'{prefix}_independent_expenditures_full.csv'
        
        # Add header comment
        with open(full_data_file, 'w') as f:
            f.write(f"# Full independent expenditure data for {dataset_name}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# Used in graphics: None (raw data file)\n")
            f.write("#\n")
        
        data.to_csv(full_data_file, mode='a', index=False)
        print(f"  ✓ Saved: {prefix}_independent_expenditures_full.csv ({len(data):,} records)")
        
        # 2. Summary by period, party, and source (WITH PERCENT CHANGE)
        summary = data.groupby(['PERIOD', 'BENEFITING_PARTY', 'COMMITTEE_CATEGORY']).agg({
            'TRANSACTION_AMT': ['sum', 'count', 'mean', 'median'],
            'CMTE_ID': 'nunique'
        }).round(2)
        summary.columns = ['Total_Amount', 'Num_Transactions', 'Mean_Amount', 
                          'Median_Amount', 'Unique_Committees']
        summary = summary.reset_index()
        
        # Add total row for each period
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
                        'Total_Amount': period_cmte_data['TRANSACTION_AMT'].sum(),
                        'Num_Transactions': len(period_cmte_data),
                        'Mean_Amount': period_cmte_data['TRANSACTION_AMT'].mean(),
                        'Median_Amount': period_cmte_data['TRANSACTION_AMT'].median(),
                        'Unique_Committees': period_cmte_data['CMTE_ID'].nunique()
                    }
                    summary = pd.concat([summary, pd.DataFrame([total_row])], ignore_index=True)
        
        # Calculate percent change
        summary['Percent_Change'] = None
        for party in summary['BENEFITING_PARTY'].unique():
            for committee in summary['COMMITTEE_CATEGORY'].unique():
                pre_data = summary[
                    (summary['PERIOD'] == 'Pre-Citizens United (2002-2010)') &
                    (summary['BENEFITING_PARTY'] == party) &
                    (summary['COMMITTEE_CATEGORY'] == committee)
                ]
                post_data = summary[
                    (summary['PERIOD'] == 'Post-Citizens United (2011-2020)') &
                    (summary['BENEFITING_PARTY'] == party) &
                    (summary['COMMITTEE_CATEGORY'] == committee)
                ]
                
                if len(pre_data) > 0 and len(post_data) > 0:
                    pre_amount = pre_data['Total_Amount'].values[0]
                    post_amount = post_data['Total_Amount'].values[0]
                    
                    if pre_amount > 0:
                        pct_change = ((post_amount - pre_amount) / pre_amount) * 100
                        # Update post period row with percent change
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
            f.write(f"# Used in graphics: {prefix}_ie_by_source_comparison.png, {prefix}_ie_source_by_party.png\n")
            f.write("# Percent_Change shows the percentage change from pre to post Citizens United period\n")
            f.write("#\n")
        
        summary.to_csv(summary_file, mode='a', index=False)
        print(f"  ✓ Saved: {prefix}_ie_summary_by_period_party_source.csv")
        
        # 3. Cycle-by-cycle totals (WITH PERCENT CHANGE)
        cycle_summary = data.groupby(['CYCLE', 'CYCLE_END_YEAR', 'BENEFITING_PARTY']).agg({
            'TRANSACTION_AMT': ['sum', 'count'],
            'CMTE_ID': 'nunique'
        }).round(2)
        cycle_summary.columns = ['Total_Amount', 'Num_Transactions', 'Unique_Committees']
        cycle_summary = cycle_summary.reset_index()
        
        # Add total for each cycle
        for cycle in cycle_summary[['CYCLE', 'CYCLE_END_YEAR']].drop_duplicates().values:
            cycle_name, cycle_year = cycle
            cycle_data = data[data['CYCLE'] == cycle_name]
            if len(cycle_data) > 0:
                total_row = {
                    'CYCLE': cycle_name,
                    'CYCLE_END_YEAR': cycle_year,
                    'BENEFITING_PARTY': 'Total',
                    'Total_Amount': cycle_data['TRANSACTION_AMT'].sum(),
                    'Num_Transactions': len(cycle_data),
                    'Unique_Committees': cycle_data['CMTE_ID'].nunique()
                }
                cycle_summary = pd.concat([cycle_summary, pd.DataFrame([total_row])], ignore_index=True)
        
        # Calculate percent change from previous cycle
        cycle_summary = cycle_summary.sort_values(['BENEFITING_PARTY', 'CYCLE_END_YEAR'])
        cycle_summary['Percent_Change_From_Previous'] = None
        
        for party in cycle_summary['BENEFITING_PARTY'].unique():
            party_data = cycle_summary[cycle_summary['BENEFITING_PARTY'] == party].copy()
            party_data['Percent_Change_From_Previous'] = party_data['Total_Amount'].pct_change() * 100
            cycle_summary.loc[cycle_summary['BENEFITING_PARTY'] == party, 'Percent_Change_From_Previous'] = \
                party_data['Percent_Change_From_Previous'].values
        
        # Convert to numeric and round (handles None/NaN properly)
        cycle_summary['Percent_Change_From_Previous'] = pd.to_numeric(
            cycle_summary['Percent_Change_From_Previous'], errors='coerce'
        ).round(2)
        
        # ADD PERIOD TOTALS to cycle summary
        period_totals_rows = []
        
        for party in ['Democrat', 'Republican', 'Total']:
            if party == 'Total':
                pre_data = data[data['PERIOD'] == 'Pre-Citizens United (2002-2010)']
                post_data = data[data['PERIOD'] == 'Post-Citizens United (2011-2020)']
                all_data = data
            else:
                pre_data = data[(data['PERIOD'] == 'Pre-Citizens United (2002-2010)') & 
                               (data['BENEFITING_PARTY'] == party)]
                post_data = data[(data['PERIOD'] == 'Post-Citizens United (2011-2020)') & 
                                (data['BENEFITING_PARTY'] == party)]
                all_data = data[data['BENEFITING_PARTY'] == party]
            
            # Pre period total (2002-2010)
            period_totals_rows.append({
                'CYCLE': '2002-2010 TOTAL',
                'CYCLE_END_YEAR': None,
                'BENEFITING_PARTY': party,
                'Total_Amount': pre_data['TRANSACTION_AMT'].sum(),
                'Num_Transactions': len(pre_data),
                'Unique_Committees': pre_data['CMTE_ID'].nunique(),
                'Percent_Change_From_Previous': None
            })
            
            # Post period total (2011-2020)
            period_totals_rows.append({
                'CYCLE': '2011-2020 TOTAL',
                'CYCLE_END_YEAR': None,
                'BENEFITING_PARTY': party,
                'Total_Amount': post_data['TRANSACTION_AMT'].sum(),
                'Num_Transactions': len(post_data),
                'Unique_Committees': post_data['CMTE_ID'].nunique(),
                'Percent_Change_From_Previous': None
            })
            
            # Overall total (2002-2020)
            period_totals_rows.append({
                'CYCLE': '2002-2020 TOTAL',
                'CYCLE_END_YEAR': None,
                'BENEFITING_PARTY': party,
                'Total_Amount': all_data['TRANSACTION_AMT'].sum(),
                'Num_Transactions': len(all_data),
                'Unique_Committees': all_data['CMTE_ID'].nunique(),
                'Percent_Change_From_Previous': None
            })
        
        # Append period totals to cycle summary
        period_totals_df = pd.DataFrame(period_totals_rows)
        cycle_summary = pd.concat([cycle_summary, period_totals_df], ignore_index=True)
        
        cycle_file = output_path / f'{prefix}_ie_summary_by_cycle.csv'
        with open(cycle_file, 'w') as f:
            f.write(f"# Cycle-by-cycle summary of independent expenditures for {dataset_name}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Used in graphics: {prefix}_ie_time_series.png, {prefix}_total_ie_by_period_party.png\n")
            f.write("# Percent_Change_From_Previous shows the percentage change from the previous election cycle\n")
            f.write("# Includes period totals at the end: 2002-2010 TOTAL, 2011-2020 TOTAL, 2002-2020 TOTAL\n")
            f.write("#\n")
        
        cycle_summary.to_csv(cycle_file, mode='a', index=False)
        print(f"  ✓ Saved: {prefix}_ie_summary_by_cycle.csv")
        
        # 4. Support vs Oppose breakdown
        support_oppose = data.groupby(['PERIOD', 'BENEFITING_PARTY', 'IE_TYPE']).agg({
            'TRANSACTION_AMT': ['sum', 'count']
        }).round(2)
        support_oppose.columns = ['Total_Amount', 'Num_Transactions']
        support_oppose = support_oppose.reset_index()
        
        # Add total for each period/party
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
                        'Total_Amount': period_party_data['TRANSACTION_AMT'].sum(),
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
        print(f"  ✓ Saved: {prefix}_ie_support_vs_oppose_breakdown.csv")
        
        # 5. NEW: Period totals summary with change calculations
        period_totals_summary = []
        
        # Calculate totals for each party and overall
        for party in ['Democrat', 'Republican', 'Total']:
            if party == 'Total':
                pre_data = data[data['PERIOD'] == 'Pre-Citizens United (2002-2010)']
                post_data = data[data['PERIOD'] == 'Post-Citizens United (2011-2020)']
                all_data = data
            else:
                pre_data = data[(data['PERIOD'] == 'Pre-Citizens United (2002-2010)') & 
                               (data['BENEFITING_PARTY'] == party)]
                post_data = data[(data['PERIOD'] == 'Post-Citizens United (2011-2020)') & 
                                (data['BENEFITING_PARTY'] == party)]
                all_data = data[data['BENEFITING_PARTY'] == party]
            
            # Pre period (2002-2010)
            pre_total = pre_data['TRANSACTION_AMT'].sum()
            pre_count = len(pre_data)
            pre_committees = pre_data['CMTE_ID'].nunique()
            
            # Post period (2011-2020)
            post_total = post_data['TRANSACTION_AMT'].sum()
            post_count = len(post_data)
            post_committees = post_data['CMTE_ID'].nunique()
            
            # Overall period (2002-2020)
            overall_total = all_data['TRANSACTION_AMT'].sum()
            overall_count = len(all_data)
            overall_committees = all_data['CMTE_ID'].nunique()
            
            # Calculate changes
            absolute_change = post_total - pre_total
            percent_change = ((post_total - pre_total) / pre_total * 100) if pre_total > 0 else None
            
            # Add rows
            period_totals_summary.append({
                'Party': party,
                'Period': '2002-2010 (Pre-Citizens United)',
                'Total_Amount': pre_total,
                'Num_Transactions': pre_count,
                'Unique_Committees': pre_committees,
                'Mean_Amount': pre_data['TRANSACTION_AMT'].mean() if len(pre_data) > 0 else 0,
                'Median_Amount': pre_data['TRANSACTION_AMT'].median() if len(pre_data) > 0 else 0
            })
            
            period_totals_summary.append({
                'Party': party,
                'Period': '2011-2020 (Post-Citizens United)',
                'Total_Amount': post_total,
                'Num_Transactions': post_count,
                'Unique_Committees': post_committees,
                'Mean_Amount': post_data['TRANSACTION_AMT'].mean() if len(post_data) > 0 else 0,
                'Median_Amount': post_data['TRANSACTION_AMT'].median() if len(post_data) > 0 else 0
            })
            
            period_totals_summary.append({
                'Party': party,
                'Period': '2002-2020 (Overall)',
                'Total_Amount': overall_total,
                'Num_Transactions': overall_count,
                'Unique_Committees': overall_committees,
                'Mean_Amount': all_data['TRANSACTION_AMT'].mean() if len(all_data) > 0 else 0,
                'Median_Amount': all_data['TRANSACTION_AMT'].median() if len(all_data) > 0 else 0
            })
            
            period_totals_summary.append({
                'Party': party,
                'Period': 'Change (2002-2010 to 2011-2020)',
                'Total_Amount': absolute_change,
                'Num_Transactions': post_count - pre_count,
                'Unique_Committees': post_committees - pre_committees,
                'Mean_Amount': (post_data['TRANSACTION_AMT'].mean() - pre_data['TRANSACTION_AMT'].mean()) if len(pre_data) > 0 and len(post_data) > 0 else 0,
                'Median_Amount': (post_data['TRANSACTION_AMT'].median() - pre_data['TRANSACTION_AMT'].median()) if len(pre_data) > 0 and len(post_data) > 0 else 0
            })
            
            period_totals_summary.append({
                'Party': party,
                'Period': 'Percent Change (2002-2010 to 2011-2020)',
                'Total_Amount': percent_change,
                'Num_Transactions': ((post_count - pre_count) / pre_count * 100) if pre_count > 0 else None,
                'Unique_Committees': ((post_committees - pre_committees) / pre_committees * 100) if pre_committees > 0 else None,
                'Mean_Amount': ((post_data['TRANSACTION_AMT'].mean() - pre_data['TRANSACTION_AMT'].mean()) / pre_data['TRANSACTION_AMT'].mean() * 100) if len(pre_data) > 0 and pre_data['TRANSACTION_AMT'].mean() > 0 and len(post_data) > 0 else None,
                'Median_Amount': ((post_data['TRANSACTION_AMT'].median() - pre_data['TRANSACTION_AMT'].median()) / pre_data['TRANSACTION_AMT'].median() * 100) if len(pre_data) > 0 and pre_data['TRANSACTION_AMT'].median() > 0 and len(post_data) > 0 else None
            })
        
        period_totals_df = pd.DataFrame(period_totals_summary)
        period_totals_df = period_totals_df.round(2)
        
        totals_file = output_path / f'{prefix}_period_totals_summary.csv'
        with open(totals_file, 'w') as f:
            f.write(f"# Period totals summary for {dataset_name}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# Shows totals for Pre-CU (2002-2010), Post-CU (2011-2020), Overall (2002-2020),\n")
            f.write("# absolute change, and percent change for each party and overall total\n")
            f.write("# Used in graphics: Can be referenced in all graphics for overall context\n")
            f.write("#\n")
        
        period_totals_df.to_csv(totals_file, mode='a', index=False)
        print(f"  ✓ Saved: {prefix}_period_totals_summary.csv")
        
        print(f"✅ All results exported to: {output_path}")


def main():
    """Main execution function"""
    print("="*80)
    print("FEC Independent Expenditure Analysis")
    print("Impact of Citizens United v. FEC (2010)")
    print("FINAL VERSION")
    print("="*80)
    print("\nFeatures:")
    print("  ✓ Percent change columns in CSV files")
    print("  ✓ Total lines/bars in all graphics")
    print("  ✓ No titles on graphics (for paper flexibility)")
    print("  ✓ CSV header comments showing which graphics use each file")
    print("  ✓ Excludes Super PAC spending from pre-2011")
    print("  ✓ Filters negative transaction amounts")
    print("="*80)
    
    # Initialize analyzer
    data_dir = 'C:/Users/sruja/Downloads/Data Collection/data'
    base_output_dir = 'C:/Users/sruja/Downloads/Data Collection/outputs'
    
    analyzer = FECDataAnalyzer(data_dir)
    
    # Load all cycles
    analyzer.load_all_cycles()
    
    # Identify independent expenditures
    analyzer.identify_independent_expenditures()
    
    # Merge candidate information
    analyzer.merge_candidate_info()
    
    # Merge committee information
    analyzer.merge_committee_info()
    
    # Create pre/post comparison
    analyzer.create_pre_post_comparison()
    
    # Run analyses for each dataset
    print("\n" + "="*80)
    print("RUNNING SEPARATE ANALYSES")
    print("="*80)
    
    # 1. Aggregate Analysis
    print("\n🔹 AGGREGATE ANALYSIS (Senate + Presidential)")
    aggregate_output = Path(base_output_dir) / 'aggregate'
    analyzer.analyze_dataset(analyzer.ie_aggregate, 'Aggregate', aggregate_output)
    
    # 2. Senate Analysis
    print("\n🔹 SENATE ANALYSIS")
    senate_output = Path(base_output_dir) / 'senate'
    analyzer.analyze_dataset(analyzer.ie_senate, 'Senate', senate_output)
    
    # 3. Presidential Analysis
    print("\n🔹 PRESIDENTIAL ANALYSIS")
    presidential_output = Path(base_output_dir) / 'presidential'
    analyzer.analyze_dataset(analyzer.ie_presidential, 'Presidential', presidential_output)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\n📁 Output structure:")
    print(f"{base_output_dir}/")
    print("  ├── aggregate/")
    print("  │   ├── Graphics (8 PNG files):")
    print("  │   │   ├── aggregate_total_ie_by_period_party.png (with total)")
    print("  │   │   ├── aggregate_total_ie_by_period_party_no_total.png")
    print("  │   │   ├── aggregate_ie_by_source_comparison.png (with total)")
    print("  │   │   ├── aggregate_ie_by_source_comparison_no_total.png")
    print("  │   │   ├── aggregate_ie_time_series.png (with total)")
    print("  │   │   ├── aggregate_ie_time_series_no_total.png")
    print("  │   │   ├── aggregate_ie_source_by_party.png (with total)")
    print("  │   │   └── aggregate_ie_source_by_party_no_total.png")
    print("  │   └── Data Files (5 CSV files):")
    print("  │       ├── aggregate_independent_expenditures_full.csv")
    print("  │       ├── aggregate_ie_summary_by_period_party_source.csv")
    print("  │       ├── aggregate_ie_summary_by_cycle.csv")
    print("  │       ├── aggregate_ie_support_vs_oppose_breakdown.csv")
    print("  │       └── aggregate_period_totals_summary.csv (NEW!)")
    print("  ├── senate/ (same 13 files)")
    print("  └── presidential/ (same 13 files)")

if __name__ == '__main__':
    main()