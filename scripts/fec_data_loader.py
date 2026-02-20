import pandas as pd
import numpy as np
from pathlib import Path
import pickle

class FECDataLoader:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.header_dir = self.data_dir / 'fec_data_file_headers'
        
        self.load_headers()
        
        self.pas2_data = []
        self.cn_data = []
        self.cm_data = []
    
    def load_headers(self):
        try:
            pas2_header_df = pd.read_csv(self.header_dir / 'pas2_header_file.csv')
            cn_header_df = pd.read_csv(self.header_dir / 'cn_header_file.csv')
            cm_header_df = pd.read_csv(self.header_dir / 'cm_header_file.csv')
            
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
        cycle_dir = self.data_dir / f'{start_year}_{end_year}'
        
        print(f"\nLoading data for {start_year}-{end_year} cycle...")
        
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
                print(f"  Loaded {len(df):,} PAS2 records")
            except Exception as e:
                print(f"  Error loading PAS2 data: {e}")
        
        cn_dir = cycle_dir / f'cn{str(end_year)[-2:]}'
        cn_file = cn_dir / 'cn.txt'
        
        if cn_file.exists():
            try:
                df = pd.read_csv(cn_file, sep='|', header=None,
                                names=self.cn_cols, low_memory=False,
                                encoding='latin-1', on_bad_lines='skip')
                df['CYCLE'] = f'{start_year}-{end_year}'
                self.cn_data.append(df)
                print(f"  Loaded {len(df):,} candidate records")
            except Exception as e:
                print(f"  Error loading candidate data: {e}")
        
        cm_dir = cycle_dir / f'cm{str(end_year)[-2:]}'
        cm_file = cm_dir / 'cm.txt'
        
        if cm_file.exists():
            try:
                df = pd.read_csv(cm_file, sep='|', header=None,
                                names=self.cm_cols, low_memory=False,
                                encoding='latin-1', on_bad_lines='skip')
                df['CYCLE'] = f'{start_year}-{end_year}'
                self.cm_data.append(df)
                print(f"  Loaded {len(df):,} committee records")
            except Exception as e:
                print(f"  Error loading committee data: {e}")
    
    def load_all_cycles(self):
        cycles = [
            (2001, 2002), (2003, 2004), (2005, 2006), (2007, 2008),
            (2009, 2010), (2011, 2012), (2013, 2014), (2015, 2016),
            (2017, 2018), (2019, 2020)
        ]
        
        for start_year, end_year in cycles:
            self.load_cycle_data(start_year, end_year)
        
        print("\nCombining all cycles...")
        if self.pas2_data:
            self.pas2_combined = pd.concat(self.pas2_data, ignore_index=True)
            print(f"Total PAS2 records: {len(self.pas2_combined):,}")
        else:
            print("No PAS2 data loaded!")
            self.pas2_combined = pd.DataFrame()
        
        if self.cn_data:
            self.cn_combined = pd.concat(self.cn_data, ignore_index=True)
            print(f"Total candidate records: {len(self.cn_combined):,}")
        else:
            print("No candidate data loaded!")
            self.cn_combined = pd.DataFrame()
        
        if self.cm_data:
            self.cm_combined = pd.concat(self.cm_data, ignore_index=True)
            print(f"Total committee records: {len(self.cm_combined):,}")
        else:
            print("No committee data loaded!")
            self.cm_combined = pd.DataFrame()
    
    def identify_independent_expenditures(self):
        print("\nIdentifying independent expenditures...")
        
        if len(self.pas2_combined) == 0:
            print("No PAS2 data available to analyze!")
            return pd.DataFrame()
        
        ie_mask = self.pas2_combined['TRANSACTION_TP'].isin(['24E', '24A', '24N'])
        self.ie_data = self.pas2_combined[ie_mask].copy()
        
        print(f"Found {len(self.ie_data):,} independent expenditure records")
        
        self.ie_data['TRANSACTION_AMT'] = pd.to_numeric(
            self.ie_data['TRANSACTION_AMT'], errors='coerce'
        )
        
        negative_count = (self.ie_data['TRANSACTION_AMT'] < 0).sum()
        if negative_count > 0:
            print(f"\nFound {negative_count:,} negative transaction amounts - removing them")
            negative_total = self.ie_data[self.ie_data['TRANSACTION_AMT'] < 0]['TRANSACTION_AMT'].sum()
            print(f"    Total negative amount: ${negative_total:,.2f}")
            
            self.ie_data = self.ie_data[self.ie_data['TRANSACTION_AMT'] >= 0].copy()
            print(f"    Remaining records after removing negatives: {len(self.ie_data):,}")
        
        self.ie_data['IE_TYPE'] = self.ie_data['TRANSACTION_TP'].map({
            '24E': 'SUPPORT',
            '24A': 'OPPOSE',
            '24N': 'SUPPORT'
        })
        
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
        print("\nMerging candidate information...")
        
        if len(self.ie_data) == 0:
            print("No IE data to merge!")
            return pd.DataFrame()
        
        if len(self.cn_combined) == 0:
            print("No candidate data available!")
            return pd.DataFrame()
        
        cn_unique = self.cn_combined.sort_values('CAND_ELECTION_YR', ascending=False)\
                                    .drop_duplicates(subset=['CAND_ID'], keep='first')
        
        self.ie_data = self.ie_data.merge(
            cn_unique[['CAND_ID', 'CAND_NAME', 'CAND_PTY_AFFILIATION', 
                      'CAND_OFFICE', 'CAND_OFFICE_ST']],
            on='CAND_ID',
            how='left'
        )
        
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
        
        print("\nCalculating benefiting party for each IE...")
        
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
        
        print("\n  IE Assignment Summary:")
        support_dem = len(self.ie_data[(self.ie_data['IE_TYPE'] == 'SUPPORT') & 
                                       (self.ie_data['CANDIDATE_PARTY'] == 'Democrat')])
        support_rep = len(self.ie_data[(self.ie_data['IE_TYPE'] == 'SUPPORT') & 
                                       (self.ie_data['CANDIDATE_PARTY'] == 'Republican')])
        oppose_dem = len(self.ie_data[(self.ie_data['IE_TYPE'] == 'OPPOSE') & 
                                      (self.ie_data['CANDIDATE_PARTY'] == 'Democrat')])
        oppose_rep = len(self.ie_data[(self.ie_data['IE_TYPE'] == 'OPPOSE') & 
                                      (self.ie_data['CANDIDATE_PARTY'] == 'Republican')])
        
        print(f"    Supporting Democrats: {support_dem:,} - Benefits Democrats")
        print(f"    Supporting Republicans: {support_rep:,} - Benefits Republicans")
        print(f"    Opposing Democrats: {oppose_dem:,} - Benefits Republicans FLIPPED")
        print(f"    Opposing Republicans: {oppose_rep:,} - Benefits Democrats FLIPPED")
        
        benefit_dem = len(self.ie_data[self.ie_data['BENEFITING_PARTY'] == 'Democrat'])
        benefit_rep = len(self.ie_data[self.ie_data['BENEFITING_PARTY'] == 'Republican'])
        print(f"\n  Net Benefiting Party:")
        print(f"    Democrats: {benefit_dem:,}")
        print(f"    Republicans: {benefit_rep:,}")
        
        self.ie_data_filtered = self.ie_data[
            self.ie_data['CAND_OFFICE'].isin(['S', 'P'])
        ].copy()
        
        print(f"\nRecords for Senate/Presidential races: {len(self.ie_data_filtered):,}")
        
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
        print("\nMerging committee information...")
        
        if len(self.cm_combined) == 0:
            print("No committee data available!")
            return pd.DataFrame()
        
        cm_unique = self.cm_combined.drop_duplicates(subset=['CMTE_ID'], keep='last')
        
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
            
            if dataset_name == 'ie_data_filtered':
                self.ie_data_filtered = merged
            elif dataset_name == 'ie_data_senate':
                self.ie_data_senate = merged
            elif dataset_name == 'ie_data_presidential':
                self.ie_data_presidential = merged
        
        print("Committee information merged for all datasets")
        
        print("\nChecking for Super PAC activity in pre-2011 cycles...")
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
                print(f"    These will be EXCLUDED from analysis")
        
        return self.ie_data_filtered
    
    def create_pre_post_comparison(self):
        print("\nCreating pre/post Citizens United comparison...")
        
        def add_period(df):
            if len(df) == 0:
                return df
            
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
                
                df = df[~(
                    (df['CYCLE_END_YEAR'] <= 2010) & 
                    (df['COMMITTEE_CATEGORY'] == 'Super PAC')
                )].copy()
                
                print(f"    Records after filter: {len(df):,} (removed {pre_filter_count - len(df):,})")
            
            df['PERIOD'] = df['CYCLE_END_YEAR'].apply(
                lambda x: 'Pre-Citizens United (2001-2010)' if x <= 2010 
                else 'Post-Citizens United (2011-2020)'
            )
            
            df = df[df['BENEFITING_PARTY'].isin(['Democrat', 'Republican'])].copy()
            
            return df
        
        self.ie_aggregate = add_period(self.ie_data_filtered)
        self.ie_senate = add_period(self.ie_data_senate)
        self.ie_presidential = add_period(self.ie_data_presidential)
        
        print(f"\nFinal counts after all filters:")
        print(f"  Aggregate: {len(self.ie_aggregate):,}")
        print(f"  Senate: {len(self.ie_senate):,}")
        print(f"  Presidential: {len(self.ie_presidential):,}")
        
        for name, df in [('Aggregate', self.ie_aggregate), 
                        ('Senate', self.ie_senate), 
                        ('Presidential', self.ie_presidential)]:
            pre_superpac = df[
                (df['PERIOD'] == 'Pre-Citizens United (2001-2010)') & 
                (df['COMMITTEE_CATEGORY'] == 'Super PAC')
            ]
            if len(pre_superpac) > 0:
                print(f"  WARNING: {name} still has {len(pre_superpac)} Super PAC records in pre-period!")
            else:
                print(f"  {name}: No Super PACs in pre-period (correct)")
        
        return self.ie_aggregate
    
    def save_processed_data(self, output_dir):
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        print("\nSaving processed datasets...")
        
        datasets = {
            'aggregate': self.ie_aggregate,
            'senate': self.ie_senate,
            'presidential': self.ie_presidential
        }
        
        for name, df in datasets.items():
            filepath = output_path / f'{name}_processed.pkl'
            with open(filepath, 'wb') as f:
                pickle.dump(df, f)
            print(f"  Saved {name} dataset: {len(df):,} records")
        
        print(f"\nProcessed data saved to: {output_path}")


def main():
    print("="*80)
    print("FEC Independent Expenditure Data Loader")
    print("="*80)
    
    data_dir = 'C:/Users/sruja/Downloads/Data Collection/data'
    output_dir = 'C:/Users/sruja/Downloads/Data Collection/outputs'
    
    loader = FECDataLoader(data_dir)
    
    loader.load_all_cycles()
    
    loader.identify_independent_expenditures()
    
    loader.merge_candidate_info()
    
    loader.merge_committee_info()
    
    loader.create_pre_post_comparison()
    
    loader.save_processed_data(output_dir)
    
    print("\n" + "="*80)
    print("DATA LOADING COMPLETE")
    print("="*80)
    print("\nRun fec_data_visualizer.py to create visualizations and export results")


if __name__ == '__main__':
    main()