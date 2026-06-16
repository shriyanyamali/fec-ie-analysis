from pathlib import Path

def verify_fec_setup(data_dir):
    data_path = Path(data_dir)
    
    print("="*80)
    print("FEC Data Setup Verification")
    print("="*80)
    
    print("\nChecking directory structure...")
    
    if not data_path.exists():
        print(f"\nERROR: Data directory not found: {data_path}")
        return False
    
    print(f"Found data directory: {data_path}")
    
    header_dir = data_path / 'fec_data_file_headers'
    if not header_dir.exists():
        print(f"\nERROR: Header directory not found: {header_dir}")
        return False
    
    print(f"Found header directory: {header_dir}")
    
    required_headers = ['pas2_header_file.csv', 'cn_header_file.csv', 'cm_header_file.csv']
    for header_file in required_headers:
        header_path = header_dir / header_file
        if not header_path.exists():
            print(f"  ERROR: Missing header file: {header_file}")
            return False
        print(f"  Found: {header_file}")
    
    print("\nChecking election cycle directories...")
    cycles = [
        (2001, 2002), (2003, 2004), (2005, 2006), (2007, 2008),
        (2009, 2010), (2011, 2012), (2013, 2014), (2015, 2016),
        (2017, 2018), (2019, 2020)
    ]
    
    missing_cycles = []
    for start_year, end_year in cycles:
        cycle_dir = data_path / f'{start_year}_{end_year}'
        if not cycle_dir.exists():
            missing_cycles.append(f'{start_year}_{end_year}')
            print(f"  WARNING: Missing cycle directory: {start_year}_{end_year}")
            continue
        
        pas2_dir = cycle_dir / f'pas2{str(end_year)[-2:]}'
        cn_dir = cycle_dir / f'cn{str(end_year)[-2:]}'
        cm_dir = cycle_dir / f'cm{str(end_year)[-2:]}'
        
        pas2_file = pas2_dir / 'itpas2.txt'
        cn_file = cn_dir / 'cn.txt'
        cm_file = cm_dir / 'cm.txt'
        
        if not pas2_file.exists():
            print(f"  ERROR: Missing PAS2 file for {start_year}-{end_year}")
            missing_cycles.append(f'{start_year}_{end_year}')
        if not cn_file.exists():
            print(f"  ERROR: Missing CN file for {start_year}-{end_year}")
        if not cm_file.exists():
            print(f"  ERROR: Missing CM file for {start_year}-{end_year}")
        
        if pas2_file.exists() and cn_file.exists() and cm_file.exists():
            print(f"  Found complete data for: {start_year}-{end_year}")
    
    print("\n" + "="*80)
    if missing_cycles:
        print(f"Verification Failed: Missing {len(missing_cycles)} cycle(s)")
        print("Please download missing data from FEC bulk data archive")
        return False
    else:
        print("Verification Passed: All required files found")
        print("\nYou can now run:")
        print("  1. python fec_data_loader.py")
        print("  2. python fec_data_visualizer.py")
        return True


if __name__ == '__main__':
    data_directory = 'C:/Users/sruja/Downloads/Code/FEC IE Analysis/data'
    verify_fec_setup(data_directory)