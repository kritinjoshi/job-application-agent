from src.sheets_manager.spreadsheet import SheetsManager
import os
from dotenv import load_dotenv

def manual_cleanup():
    load_dotenv()
    sheets = SheetsManager()
    # Clearing rows 12-21 in the 'Job Applications' tab
    sheets.clear_range("Job Applications", "A12:J21")
    print("One-time manual cleanup of rows 12-21 complete.")

if __name__ == "__main__":
    manual_cleanup()
