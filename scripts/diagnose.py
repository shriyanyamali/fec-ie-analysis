import pandas as pd
import pickle

with open('C:/Users/sruja/Downloads/Code/FEC IE Analysis/outputs/aggregate_processed.pkl', 'rb') as f:
    ie_aggregate = pickle.load(f)

other_unknown = ie_aggregate[ie_aggregate['COMMITTEE_CATEGORY'] == 'Other/Unknown']

results = {}

def get_breakdown(df, label):
    breakdown = df.groupby('CMTE_TP', dropna=False)['TRANSACTION_AMT']\
        .agg(['sum', 'count'])\
        .sort_values('sum', ascending=False)\
        .reset_index()
    breakdown.columns = ['CMTE_TP', 'Total_Amount', 'Record_Count']
    breakdown['Group'] = label
    breakdown['Total_Amount_In_Group'] = df['TRANSACTION_AMT'].sum()
    breakdown['Pct_Of_Group'] = (breakdown['Total_Amount'] / df['TRANSACTION_AMT'].sum() * 100).round(2)
    
    print(f"\n=== {label} ===")
    print(f"Total Amount: ${df['TRANSACTION_AMT'].sum():,.2f}")
    print(f"Total Records: {len(df):,}")
    print(breakdown[['CMTE_TP', 'Total_Amount', 'Record_Count', 'Pct_Of_Group']].to_string(index=False))
    
    return breakdown

pre_cu = other_unknown[other_unknown['PERIOD'] == 'Pre-Citizens United (2001-2010)']
results['pre_overall'] = get_breakdown(pre_cu, 'Pre-CU Overall')

post_cu = other_unknown[other_unknown['PERIOD'] == 'Post-Citizens United (2011-2020)']
results['post_overall'] = get_breakdown(post_cu, 'Post-CU Overall')

pre_dem = pre_cu[pre_cu['BENEFITING_PARTY'] == 'Democrat']
results['pre_dem'] = get_breakdown(pre_dem, 'Pre-CU Democrats')

pre_rep = pre_cu[pre_cu['BENEFITING_PARTY'] == 'Republican']
results['pre_rep'] = get_breakdown(pre_rep, 'Pre-CU Republicans')

post_dem = post_cu[post_cu['BENEFITING_PARTY'] == 'Democrat']
results['post_dem'] = get_breakdown(post_dem, 'Post-CU Democrats')

post_rep = post_cu[post_cu['BENEFITING_PARTY'] == 'Republican']
results['post_rep'] = get_breakdown(post_rep, 'Post-CU Republicans')

combined = pd.concat(results.values(), ignore_index=True)
combined = combined[['Group', 'CMTE_TP', 'Total_Amount', 'Record_Count', 'Pct_Of_Group', 'Total_Amount_In_Group']]

output_path = 'C:/Users/sruja/Downloads/Code/FEC IE Analysis/outputs/other_IEs_breakdown.csv'
combined.to_csv(output_path, index=False)
print(f"\nSaved to: {output_path}")