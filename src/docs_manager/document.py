import os
import io
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.auth.google_auth import get_google_credentials

class DocsManager:
    def __init__(self):
        self.creds = get_google_credentials()
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.folders = self._init_folders()
        
    def _find_folder(self, name, parent_id=None):
        q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            q += f" and '{parent_id}' in parents"
            
        try:
            results = self.drive_service.files().list(q=q, spaces='drive', fields='files(id, name)').execute()
            files = results.get('files', [])
            return files[0]['id'] if files else None
        except Exception:
            return None

    def _create_folder(self, name, parent_id=None):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        try:
            file = self.drive_service.files().create(body=file_metadata, fields='id').execute()
            return file.get('id')
        except Exception:
            return None

    def _init_folders(self):
        root_name = "Job Applications Agent Folder"
        resumes_name = "Resumes"
        cl_name = "Cover letters"
        
        root_id = self._find_folder(root_name)
        if not root_id:
            root_id = self._create_folder(root_name)
            
        resumes_id = self._find_folder(resumes_name, root_id) if root_id else None
        if root_id and not resumes_id:
            resumes_id = self._create_folder(resumes_name, root_id)
            
        cl_id = self._find_folder(cl_name, root_id) if root_id else None
        if root_id and not cl_id:
            cl_id = self._create_folder(cl_name, root_id)
            
        tracker_id = os.environ.get('TRACKER_SPREADSHEET_ID')
        if tracker_id and root_id:
            try:
                file = self.drive_service.files().get(fileId=tracker_id, fields='parents').execute()
                previous_parents = ",".join(file.get('parents', []))
                if root_id not in previous_parents:
                    self.drive_service.files().update(
                        fileId=tracker_id,
                        addParents=root_id,
                        removeParents=previous_parents,
                        fields='id, parents'
                    ).execute()
                    print(f"Successfully moved Master Tracker dynamically into '{root_name}' Google Drive Folder!")
            except Exception as e:
                # Failing gracefully if explicit full Drive scope wasn't verified
                pass
                
        return {"root": root_id, "resumes": resumes_id, "cover_letters": cl_id}

    def create_resume_doc_from_file(self, title, file_path, folder_type="resumes"):
        target_parent = self.folders.get(folder_type)
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        if target_parent:
            file_metadata['parents'] = [target_parent]
            
        media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document', resumable=True)
        file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return f"https://docs.google.com/document/d/{file.get('id')}/edit"
