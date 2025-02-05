import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# List of service account credentials
SERVICE_ACCOUNTS = ["credentials/account1.json", "credentials/account2.json"]

def authenticate_drive(credentials_file):
    """Authenticate and return a Google Drive service."""
    creds = service_account.Credentials.from_service_account_file(credentials_file)
    return build('drive', 'v3', credentials=creds)

def list_files(service):
    """List files from a specific Google Drive account."""
    results = service.files().list(fields="files(id, name)").execute()
    return results.get('files', [])

def upload_file(service, file_path):
    """Upload a file to Google Drive."""
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded {file_path} with ID: {file['id']}")

def main():
    """Test listing files across multiple accounts."""
    for account in SERVICE_ACCOUNTS:
        service = authenticate_drive(account)
        print(f"Files from {account}:")
        for file in list_files(service):
            print(f"- {file['name']} (ID: {file['id']})")

if __name__ == '__main__':
    main()
