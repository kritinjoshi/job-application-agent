import os
import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from src.auth.google_auth import get_google_credentials

class SheetsManager:
    def __init__(self, spreadsheet_id=None):
        # Locate the local .env file gracefully assuming we are 2 dirs deep (src/sheets_manager)
        self.env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        load_dotenv(self.env_path)
        
        self.creds = get_google_credentials()
        self.service = build('sheets', 'v4', credentials=self.creds)
        
        # Precedence: 1. Local override, 2. Env state
        self.spreadsheet_id = spreadsheet_id or os.environ.get('TRACKER_SPREADSHEET_ID')
        
        if self.spreadsheet_id:
            print(f"Docs: Found existing Master Tracker: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")
        else:
            self.spreadsheet_id = self._create_spreadsheet()
            
        self._ensure_sheet_architecture()

    def _ensure_sheet_architecture(self):
        try:
            sheet_meta = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheets = sheet_meta.get('sheets', [])
            
            jobs_board_exists = False
            requests = []
            
            for s in sheets:
                title = s['properties']['title']
                sheet_id = s['properties']['sheetId']
                if title == 'Sheet1':
                    requests.append({
                        'updateSheetProperties': {
                            'properties': {
                                'sheetId': sheet_id,
                                'title': 'Job Applications'
                            },
                            'fields': 'title'
                        }
                    })
                elif title == 'Jobs Board':
                    jobs_board_exists = True
                    
            if not jobs_board_exists:
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': 'Jobs Board'
                        }
                    }
                })
                
            if requests:
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id, 
                    body={'requests': requests}
                ).execute()
                print("Explicitly provisioned dual-tab schema strictly correctly resolving `Job Applications` & `Jobs Board` hooks.")
        except Exception as e:
            print(f"Failed to aggressively ensure dual-sheet architecture logically mapping structural IDs: {e}")

    def _create_spreadsheet(self):
        spreadsheet = {
            'properties': {'title': 'Job Application VIP Tracker'}
        }
        spreadsheet = self.service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        
        # Add beautiful bold headers including the new fields requested
        values = [["Job Title", "Company", "Job URL", "Tailored Resume URL", "Cover Letter URL", "Match Score", "Expected Salary", "Role Seniority", "Work Logistics", "Date Inserted"]]
        body = {'values': values}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range="Sheet1!A1:J1",
            valueInputOption="RAW", body=body).execute()
            
        try:
            reqs = [{'repeatCell': {'range': {'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 1}, 'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}}, 'fields': 'userEnteredFormat.textFormat.bold'}}]
            self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': reqs}).execute()
        except:
            pass
            
        print(f"Created brand new Master Tracker: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        
        if os.path.exists(self.env_path):
            with open(self.env_path, 'a') as f:
                f.write(f'\nTRACKER_SPREADSHEET_ID="{spreadsheet_id}"\n')
            
            # Immediately load that back into the active environment so it works synchronously later
            os.environ['TRACKER_SPREADSHEET_ID'] = spreadsheet_id
            print(f"Successfully saved TRACKER_SPREADSHEET_ID into `{self.env_path}`. All future runs will append here.")
            
        return spreadsheet_id

    def get_existing_signatures(self):
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range="'Job Applications'!A:C"
            ).execute()
            values = result.get('values', [])
            
            # Combine "Company_Title" strings alongside raw urls to robustly deduplicate.
            cache = []
            for row in values:
                if len(row) > 1:
                    title, company = row[0], row[1]
                    cache.append(f"{company.lower().strip()}_{title.lower().strip()}")
                if len(row) > 2 and row[2] != "No Link":
                    cache.append(row[2])
            return cache
        except Exception as e:
            print(f"Docs: Warning, failed to sync active deduplication schema! {e}")
            return []

    def append_job_row(self, job_title, company, job_url, resume_url, cover_letter_url, salary, seniority, match_score, logistics):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        job_hyperlink = f'=HYPERLINK("{job_url}", "LINK")' if "http" in job_url else "No Link"
        res_hyperlink = f'=HYPERLINK("{resume_url}", "LINK")' if "http" in resume_url else "N/A - Quota Hit"
        cl_hyperlink = f'=HYPERLINK("{cover_letter_url}", "LINK")' if "http" in cover_letter_url else "N/A - Quota Hit"
        
        values = [[job_title, company, job_hyperlink, res_hyperlink, cl_hyperlink, match_score, salary, seniority, logistics, now_str]]
        body = {'values': values}
        
        # Actively scan for the first completely blank row physically natively
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range="'Job Applications'!A:A"
            ).execute()
            
            col_a_vals = result.get('values', [])
            target_row = 1
            for row in col_a_vals:
                if not row or not str(row[0]).strip():
                    break
                target_row += 1
                
            range_str = f"'Job Applications'!A{target_row}:J{target_row}"
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range=range_str,
                valueInputOption="USER_ENTERED", body=body).execute()
                
            print(f"Appended dynamically formatted 10-column analytic row into Master Tracker explicitly overriding Row {target_row} for {job_title} at {company}")
        except Exception as e:
            # Fallback natively structurally to raw append
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id, range="'Job Applications'",
                valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body=body).execute()
            print(f"Appended dynamically formatted 10-column analytic row into Master Tracker structurally for {job_title} at {company} (Fallback mode)")

    def clear_range(self, tab_name, range_str):
        try:
            full_range = f"'{tab_name}'!{range_str}"
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id, range=full_range,
                body={}
            ).execute()
            print(f"Docs: Surgically cleared range {full_range} in Master Tracker.")
        except Exception as e:
            print(f"Docs: Failed to clear range {range_str}: {e}")

    def overwrite_jobs_board(self, jobs_matrix):
        try:
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range="'Jobs Board'!A:Z"
            ).execute()
            
            headers = ["Job Title", "Company", "Job URL", "Recency", "Location", "Recruiting Status", "Days Ago", "Local Score", "Level"]
            values = [headers] + jobs_matrix
            body = {'values': values}
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range="'Jobs Board'!A1",
                valueInputOption="USER_ENTERED", body=body).execute()
                
            # Watermark cell J2 with deterministic update timestamp structurally
            ts_val = [[f"Last Refreshed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]]
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range="'Jobs Board'!J2",
                valueInputOption="USER_ENTERED", body={'values': ts_val}).execute()
                
            try:
                # Retrieve the sheetId strictly natively resolving `Jobs Board` bounds structurally correctly!
                sheet_meta = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
                target_sheet_id = None
                for s in sheet_meta.get('sheets', []):
                    if s['properties']['title'] == 'Jobs Board':
                        target_sheet_id = s['properties']['sheetId']
                        break
                        
                if target_sheet_id is not None:
                    reqs = [{'repeatCell': {'range': {'sheetId': target_sheet_id, 'startRowIndex': 0, 'endRowIndex': 1}, 'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}}, 'fields': 'userEnteredFormat.textFormat.bold'}}]
                    self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body={'requests': reqs}).execute()
            except Exception:
                pass
                
            print(f"Instantly overwrote exactly {len(jobs_matrix)} generic jobs into Jobs Board tab.")
        except Exception as e:
            print(f"Failed to overwrite Jobs Board tab: {e}")

