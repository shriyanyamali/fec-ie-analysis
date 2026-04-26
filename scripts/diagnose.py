import pandas as pd
import pickle

with open('C:/Users/sruja/Downloads/Code/FEC IE Analysis/outputs/aggregate_processed.pkl', 'rb') as f:
    ie_aggregate = pickle.load(f)

other_unknown = ie_aggregate[ie_aggregate['COMMITTEE_CATEGORY'] == 'Other/Unknown']

print(f"Total Other/Unknown amount: ${other_unknown['TRANSACTION_AMT'].sum():,.2f}")
print(f"Total Other/Unknown records: {len(other_unknown):,}")
print("\n--- Breakdown by CMTE_TP ---")
print(other_unknown.groupby('CMTE_TP', dropna=False)['TRANSACTION_AMT']\
    .agg(['sum', 'count'])\
    .sort_values('sum', ascending=False))