"""Alternative-classification run of the FEC IE pipeline (robustness check for the STS report).

Differences from fec_data_loader.py, each flagged with  # CHANGE:
  1. IEs = transaction types 24A and 24E only (24N is a Form 7 communication cost AGAINST a candidate, not an IE).
  2. Committee type is taken from the committee master file of the SAME cycle as the expenditure
     (fallback: most recent type) instead of the most recent type for all cycles.
  3. Hybrid PACs (types V and W) form their own category instead of V -> Traditional PAC, W -> Other/Unknown.
  4. Candidate dedup uses a stable sort so results are reproducible.
Everything else (negatives dropped, Senate/presidential only, Dem/Rep only, pre-2011 Super PAC rows dropped,
candidate committees dropped) is unchanged.

Usage:  python scripts/fec_data_loader_corrected.py  [data_dir] [output_dir]
Then:   python scripts/fec_regression_analysis.py --data-dir outputs/robustness_check
        (regression outputs are written to outputs/robustness_check/regressions/)
"""
import sys, pickle
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from fec_data_loader import FECDataLoader

data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / 'data'
out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent.parent / 'outputs' / 'robustness_check'
out_dir.mkdir(parents=True, exist_ok=True)

L = FECDataLoader(str(data_dir))
cycles = [(2001,2002),(2003,2004),(2005,2006),(2007,2008),(2009,2010),(2011,2012),(2013,2014),(2015,2016),(2017,2018),(2019,2020)]
ies, cns, cms = [], [], []
for s, e in cycles:
    L.pas2_data, L.cn_data, L.cm_data = [], [], []
    L.load_cycle_data(s, e)
    df = L.pas2_data[0]
    ies.append(df[df['TRANSACTION_TP'].isin(['24A', '24E'])].copy())   # CHANGE 1
    cns.append(L.cn_data[0]); cms.append(L.cm_data[0])
    del df
pas = pd.concat(ies, ignore_index=True); cn = pd.concat(cns, ignore_index=True); cm = pd.concat(cms, ignore_index=True)

ie = pas.copy()
ie['TRANSACTION_AMT'] = pd.to_numeric(ie['TRANSACTION_AMT'], errors='coerce')
neg = ie[ie['TRANSACTION_AMT'] < 0]
print(f"negative records dropped: {len(neg):,} (${neg['TRANSACTION_AMT'].sum():,.0f})")
ie = ie[ie['TRANSACTION_AMT'] >= 0].copy()
ie['IE_TYPE'] = ie['TRANSACTION_TP'].map({'24E': 'SUPPORT', '24A': 'OPPOSE'})

cn_u = cn.sort_values('CAND_ELECTION_YR', ascending=False, kind='mergesort').drop_duplicates('CAND_ID', keep='first')  # CHANGE 4
ie = ie.merge(cn_u[['CAND_ID', 'CAND_NAME', 'CAND_PTY_AFFILIATION', 'CAND_OFFICE', 'CAND_OFFICE_ST']], on='CAND_ID', how='left')
party_map = {'DEM': 'Democrat', 'REP': 'Republican'}
ie['CANDIDATE_PARTY'] = ie['CAND_PTY_AFFILIATION'].map(lambda x: party_map.get(x, 'Other'))
def benefiting(r):
    if r['IE_TYPE'] == 'SUPPORT':
        return r['CANDIDATE_PARTY']
    return {'Democrat': 'Republican', 'Republican': 'Democrat'}.get(r['CANDIDATE_PARTY'], 'Unknown')
ie['BENEFITING_PARTY'] = ie.apply(benefiting, axis=1)
ie = ie[ie['CAND_OFFICE'].isin(['S', 'P'])].copy()

cm_cycle = cm.drop_duplicates(['CMTE_ID', 'CYCLE'], keep='last')[['CMTE_ID', 'CYCLE', 'CMTE_NM', 'CMTE_TP', 'CMTE_DSGN']]
cm_latest = cm.drop_duplicates('CMTE_ID', keep='last')[['CMTE_ID', 'CMTE_TP']].rename(columns={'CMTE_TP': 'CMTE_TP_LATEST'})
ie = ie.merge(cm_cycle, on=['CMTE_ID', 'CYCLE'], how='left').merge(cm_latest, on='CMTE_ID', how='left')  # CHANGE 2
ie['CMTE_TP'] = ie['CMTE_TP'].fillna(ie['CMTE_TP_LATEST'])

def categorize(tp):  # CHANGE 3
    if tp == 'O': return 'Super PAC'
    if tp in ('V', 'W'): return 'Hybrid PAC'
    if tp in ('N', 'Q'): return 'Traditional PAC'
    if tp == 'U': return 'Individual IE Committee'
    if tp in ('X', 'Y', 'Z'): return 'Party Committee'
    if tp in ('H', 'S', 'P'): return 'Candidate Committee'
    return 'Other/Unknown'
ie['COMMITTEE_CATEGORY'] = ie['CMTE_TP'].map(categorize)

cc = ie[ie['COMMITTEE_CATEGORY'] == 'Candidate Committee']
print(f"candidate-committee records dropped: {len(cc):,} (${cc['TRANSACTION_AMT'].sum():,.0f})")
ie = ie[ie['COMMITTEE_CATEGORY'] != 'Candidate Committee']
pre_sp = ie[(ie['CYCLE_END_YEAR'] <= 2010) & (ie['COMMITTEE_CATEGORY'] == 'Super PAC')]
print(f"pre-2011 Super PAC records dropped: {len(pre_sp):,} (${pre_sp['TRANSACTION_AMT'].sum():,.0f})")
ie = ie[~((ie['CYCLE_END_YEAR'] <= 2010) & (ie['COMMITTEE_CATEGORY'] == 'Super PAC'))]
ie['PERIOD'] = np.where(ie['CYCLE_END_YEAR'] <= 2010, 'Pre-Citizens United (2001-2010)', 'Post-Citizens United (2011-2020)')
ie = ie[ie['BENEFITING_PARTY'].isin(['Democrat', 'Republican'])].copy()

for name, d in [('aggregate', ie), ('senate', ie[ie['CAND_OFFICE'] == 'S']), ('presidential', ie[ie['CAND_OFFICE'] == 'P'])]:
    with open(out_dir / f'{name}_processed.pkl', 'wb') as f:
        pickle.dump(d.copy(), f)
    print(f"saved {name}: {len(d):,} records")

pd.set_option('display.width', 250)
print("\nPeriod x party totals:\n", ie.groupby(['PERIOD', 'BENEFITING_PARTY'])['TRANSACTION_AMT'].sum())
t = ie.groupby(['PERIOD', 'BENEFITING_PARTY', 'COMMITTEE_CATEGORY'])['TRANSACTION_AMT'].sum().unstack().fillna(0)
print("\nPeriod x party x category ($):\n", t.astype('int64'))
print("\n(% of party-period):\n", (t.div(t.sum(axis=1), axis=0) * 100).round(2))
print("\nNext: python scripts/fec_regression_analysis.py --data-dir", out_dir)
