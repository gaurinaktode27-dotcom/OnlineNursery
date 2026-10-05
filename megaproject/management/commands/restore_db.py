import os
import shutil
import glob
from django.core.management.base import BaseCommand
from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import pickle
import os.path

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class Command(BaseCommand):
    help = 'Restores the SQLite database from Google Drive backup'

    def get_google_drive_service(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('drive', 'v3', credentials=creds)

    def handle(self, *args, **options):
        try:
            service = self.get_google_drive_service()
            
            # Find the backup folder
            results = service.files().list(
                q="name='OnlineNurseryBackups' and mimeType='application/vnd.google-apps.folder'",
                spaces='drive',
                fields='files(id, name)').execute()
            items = results.get('files', [])
            
            if not items:
                self.stdout.write(self.style.ERROR('Backup folder not found'))
                return
                
            folder_id = items[0]['id']
            
            # Get the most recent backup file
            results = service.files().list(
                q=f"'{folder_id}' in parents and mimeType='application/x-sqlite3'",
                spaces='drive',
                fields='files(id, name, createdTime)',
                orderBy='createdTime desc').execute()
            items = results.get('files', [])
            
            if not items:
                self.stdout.write(self.style.ERROR('No backup files found'))
                return
                
            latest_backup = items[0]
            
            # Download the backup file
            request = service.files().get_media(fileId=latest_backup['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Save the downloaded file
            db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            with open(db_path, 'wb') as f:
                f.write(fh.getvalue())
            
            self.stdout.write(self.style.SUCCESS(f'Database restored from backup: {latest_backup["name"]}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error restoring database: {str(e)}')) 