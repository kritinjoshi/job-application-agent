import os
import sys
from dotenv import load_dotenv

def deep_clean():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(base_dir, '.env'))
    sys.path.append(base_dir)
    
    from src.sheets_manager.spreadsheet import SheetsManager
    sheets = SheetsManager()
    
    print("\n[Deep Clean] Wiping 'Jobs Board'...")
    sheets.clear_range("Jobs Board", "A2:Z200")
    
    print("[Deep Clean] Wiping 'Job Applications' Rows 12-30...")
    sheets.clear_range("Job Applications", "A12:J35")
    
    print("\nSheets are now pristine. Ready for the High-Efficiency Pipeline demo!")

if __name__ == "__main__":
    deep_clean()
