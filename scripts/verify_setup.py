import os
from pathlib import Path

def verify_data_structure(data_dir):
    print("="*80)
    print("FEC Data Structure Verification")
    print("="*80)
    
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"\n❌ ERROR: Data directory not found at: {data_path}")
        print(f"\nPlease create this directory and upload your data files.")
        return False
    
    print(f"\n✓ Data directory found: {data_path}")
    
    # Check for header files
    print("\n" + "-"*80)
    print("Checking Header Files...")
    print("-"*80)
    
    header_dir = data_path / 'fec_data_file_headers'
    required_headers = ['pas2_header_file.csv', 'cn_header_file.csv', 'cm_header_file.csv']
    
    headers_found = True
    if not header_dir.exists():
        print(f"❌ Header directory not found: {header_dir}")
        print("   Please create: data/fec_data_file_headers/")
        headers_found = False
    else:
        for header in required_headers:
            header_path = header_dir / header
            if header_path.exists():
                size = header_path.stat().st_size
                print(f"✓ {header} ({size:,} bytes)")
            else:
                print(f"❌ Missing: {header}")
                headers_found = False
    
    # Check for cycle directories
    print("\n" + "-"*80)
    print("Checking Election Cycle Directories...")
    print("-"*80)
    
    expected_cycles = [
        ('2001_2002', '02'), ('2003_2004', '04'), ('2005_2006', '06'),
        ('2007_2008', '08'), ('2009_2010', '10'), ('2011_2012', '12'),
        ('2013_2014', '14'), ('2015_2016', '16'), ('2017_2018', '18'),
        ('2019_2020', '20')
    ]
    
    cycles_summary = []
    
    for cycle_name, year_suffix in expected_cycles:
        cycle_path = data_path / cycle_name
        
        if not cycle_path.exists():
            print(f"\n❌ {cycle_name}: Directory not found")
            cycles_summary.append((cycle_name, False, 0, 0, 0))
            continue
        
        # Check for required subdirectories and files
        pas2_file = cycle_path / f'pas2{year_suffix}' / 'itpas2.txt'
        cn_file = cycle_path / f'cn{year_suffix}' / 'cn.txt'
        cm_file = cycle_path / f'cm{year_suffix}' / 'cm.txt'
        
        files_found = 0
        total_size = 0
        
        print(f"\n{cycle_name}:")
        
        if pas2_file.exists():
            size = pas2_file.stat().st_size
            total_size += size
            files_found += 1
            print(f"  ✓ itpas2.txt ({size/1024/1024:.1f} MB)")
        else:
            print(f"  ❌ Missing: pas2{year_suffix}/itpas2.txt")
        
        if cn_file.exists():
            size = cn_file.stat().st_size
            total_size += size
            files_found += 1
            print(f"  ✓ cn.txt ({size/1024/1024:.1f} MB)")
        else:
            print(f"  ❌ Missing: cn{year_suffix}/cn.txt")
        
        if cm_file.exists():
            size = cm_file.stat().st_size
            total_size += size
            files_found += 1
            print(f"  ✓ cm.txt ({size/1024/1024:.1f} MB)")
        else:
            print(f"  ❌ Missing: cm{year_suffix}/cm.txt")
        
        cycles_summary.append((cycle_name, files_found == 3, files_found, 
                              total_size/1024/1024, 3))
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_cycles = len(expected_cycles)
    complete_cycles = sum(1 for _, complete, _, _, _ in cycles_summary if complete)
    total_files_found = sum(found for _, _, found, _, _ in cycles_summary)
    total_files_expected = sum(expected for _, _, _, _, expected in cycles_summary)
    total_data_size = sum(size for _, _, _, size, _ in cycles_summary)
    
    print(f"\nCycles: {complete_cycles}/{total_cycles} complete")
    print(f"Files: {total_files_found}/{total_files_expected} found")
    print(f"Total data size: {total_data_size:.1f} MB")
    
    if headers_found and complete_cycles == total_cycles:
        print("\n✅ All required files found! You're ready to run the analysis.")
        print("\nNext step: Run 'python analyze_fec_data.py'")
        return True
    else:
        print("\n⚠️  Some files are missing. Please upload the missing files before running the analysis.")
        
        if not headers_found:
            print("\n❌ Missing header files - these are required!")
        
        missing_cycles = [name for name, complete, _, _, _ in cycles_summary if not complete]
        if missing_cycles:
            print(f"\n❌ Incomplete cycles: {', '.join(missing_cycles)}")
        
        return False


def show_sample_data(data_dir, cycle='2015_2016', year_suffix='16'):
    """
    Show a sample of the data to verify it's loading correctly
    
    Parameters:
    -----------
    data_dir : str
        Path to the data directory
    cycle : str
        Cycle directory name (e.g., '2015_2016')
    year_suffix : str
        Year suffix for file names (e.g., '16')
    """
    import pandas as pd
    
    print("\n" + "="*80)
    print(f"Sample Data from {cycle}")
    print("="*80)
    
    data_path = Path(data_dir)
    
    # Try to load a sample of PAS2 data
    pas2_file = data_path / cycle / f'pas2{year_suffix}' / 'itpas2.txt'
    
    if not pas2_file.exists():
        print(f"❌ Cannot find {pas2_file}")
        return
    
    try:
        # Default column names for PAS2
        pas2_cols = [
            'CMTE_ID', 'AMNDT_IND', 'RPT_TP', 'TRANSACTION_PGI', 'IMAGE_NUM',
            'TRANSACTION_TP', 'ENTITY_TP', 'NAME', 'CITY', 'STATE', 'ZIP_CODE',
            'EMPLOYER', 'OCCUPATION', 'TRANSACTION_DT', 'TRANSACTION_AMT',
            'OTHER_ID', 'CAND_ID', 'TRAN_ID', 'FILE_NUM', 'MEMO_CD', 'MEMO_TEXT',
            'SUB_ID'
        ]
        
        print(f"\nLoading first 5 rows from: {pas2_file.name}")
        df = pd.read_csv(pas2_file, sep='|', header=None, names=pas2_cols,
                        encoding='latin-1', nrows=5)
        
        print(f"\nTotal columns: {len(df.columns)}")
        print(f"Column names: {list(df.columns)[:10]}... (showing first 10)")
        print(f"\nFirst few rows:")
        print(df[['CMTE_ID', 'TRANSACTION_TP', 'CAND_ID', 'TRANSACTION_AMT', 
                 'TRANSACTION_DT']].to_string())
        
        # Check for independent expenditures
        ie_mask = df['TRANSACTION_TP'].isin(['24E', '24A', '24N'])
        ie_count = ie_mask.sum()
        print(f"\n✓ Found {ie_count} independent expenditure(s) in this sample")
        
        if ie_count > 0:
            print("\nSample IE transaction:")
            print(df[ie_mask][['CMTE_ID', 'TRANSACTION_TP', 'CAND_ID', 
                              'TRANSACTION_AMT']].iloc[0].to_string())
        
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")


if __name__ == '__main__':
    # Check if running in the uploads directory or locally
    possible_paths = [
        '/mnt/user-data/uploads/data',  # Cloud environment
        'data',  # Local directory
        'C:/Users/sruja/Downloads/Data Collection/data'  # User's local path
    ]
    
    data_dir = None
    for path in possible_paths:
        if Path(path).exists():
            data_dir = path
            break
    
    if data_dir is None:
        print("❌ Could not find data directory.")
        print("\nSearched in:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\nPlease update the path in this script or upload your data.")
    else:
        verify_data_structure(data_dir)
        
        # Optionally show sample data
        response = input("\nWould you like to see a sample of the data? (y/n): ")
        if response.lower() == 'y':
            show_sample_data(data_dir)