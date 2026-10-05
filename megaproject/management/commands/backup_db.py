import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
import glob
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
import os.path

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class Command(BaseCommand):
    help = 'Backs up the SQLite database to Google Drive'

    def get_google_drive_service(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('drive', 'v3', credentials=creds)

    def handle(self, *args, **options):
        try:
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Define paths
            db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            backup_path = os.path.join(backup_dir, f'db_backup_{timestamp}.sqlite3')
            
            # Create backups directory if it doesn't exist
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Copy the database file
            shutil.copy2(db_path, backup_path)
            self.stdout.write(self.style.SUCCESS(f'Local backup created at {backup_path}'))
            
            # Upload to Google Drive
            service = self.get_google_drive_service()
            
            # Check if backup folder exists, create if not
            results = service.files().list(
                q="name='OnlineNurseryBackups' and mimeType='application/vnd.google-apps.folder'",
                spaces='drive',
                fields='files(id, name)').execute()
            items = results.get('files', [])
            
            if not items:
                file_metadata = {
                    'name': 'OnlineNurseryBackups',
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = service.files().create(body=file_metadata, fields='id').execute()
                folder_id = folder.get('id')
            else:
                folder_id = items[0]['id']
            
            # Upload the backup file
            file_metadata = {
                'name': f'db_backup_{timestamp}.sqlite3',
                'parents': [folder_id]
            }
            media = MediaFileUpload(backup_path, mimetype='application/x-sqlite3')
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            
            self.stdout.write(self.style.SUCCESS(f'Backup uploaded to Google Drive with ID: {file.get("id")}'))
            
            # Clean up local backup
            os.remove(backup_path)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error backing up database: {str(e)}')) 