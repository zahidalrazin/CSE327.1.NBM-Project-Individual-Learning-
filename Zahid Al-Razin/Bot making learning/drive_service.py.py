from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os, pickle

SCOPES = ['https://www.googleapis.com/auth/drive']

class DriveService:
    def __init__(self, account):
        creds = None
        token_path = f"tokens/{account}_token.pickle"
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            os.makedirs("tokens", exist_ok=True)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        self.service = build('drive', 'v3', credentials=creds)

    def list_files(self):
        results = self.service.files().list(pageSize=10).execute()
        items = results.get('files', [])
        for item in items:
            print(f"{item['name']} ({item['id']})")

    def upload_file(self, filepath):
        from googleapiclient.http import MediaFileUpload
        file_metadata = {'name': os.path.basename(filepath)}
        media = MediaFileUpload(filepath, resumable=False)
        file = self.service.files().create(body=file_metadata, media_body=media).execute()
        print(f"Uploaded: {file.get('name')}")

    def download_file(self, file_id, destination):
        request = self.service.files().get_media(fileId=file_id)
        with open(destination, 'wb') as f:
            downloader = request.execute()
            f.write(downloader)
        print(f"Downloaded to {destination}")
