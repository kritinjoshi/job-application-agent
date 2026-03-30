import os
from dotenv import load_dotenv

base_dir = os.path.dirname(__file__)
load_dotenv(os.path.join(base_dir, '.env'))

from src.integrations.google.sheets.spreadsheet import SheetsManager

print("Initializing API connection inherently...")
sheets = SheetsManager()

print("Wiping previous values globally keeping strictly core Header blocks explicitly!")
sheets.service.spreadsheets().values().clear(
    spreadsheetId=sheets.spreadsheet_id,
    range="'Job Applications'!A2:J1000"
).execute()

# Ensure strictly 10-column headers definitively exist organically explicitly
values = [["Job Title", "Company", "Job URL", "Tailored Resume URL", "Cover Letter URL", "Match Score", "Expected Salary", "Role Seniority", "Work Logistics", "Date Inserted"]]
body = {'values': values}

sheets.service.spreadsheets().values().update(
    spreadsheetId=sheets.spreadsheet_id, range="'Job Applications'!A1:J1",
    valueInputOption="RAW", body=body).execute()

# FORCE unbolding for all body rows natively explicitly cleanly!
try:
    reqs = [{
        'repeatCell': {
            'range': {'sheetId': 0, 'startRowIndex': 1, 'endRowIndex': 1000},
            'cell': {'userEnteredFormat': {'textFormat': {'bold': False, 'link': None}}},
            'fields': 'userEnteredFormat.textFormat.bold'
        }
    }]
    sheets.service.spreadsheets().batchUpdate(
        spreadsheetId=sheets.spreadsheet_id, 
        body={'requests': reqs}
    ).execute()
except Exception as e:
    print(f"Failed to logically unbold sheet bounds correctly securely: {e}")

print("Master Tracker explicitly formally erased cleanly, Expanded to 9 Columns & Unbolded seamlessly! Awaiting Cron trigger arrays.")
