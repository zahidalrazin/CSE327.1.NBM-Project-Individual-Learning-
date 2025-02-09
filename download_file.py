import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Configuration
SERVICE_ACCOUNT_FILE = 'path/to/your/service_account.json'  # Path to your service account JSON file

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive']
)
drive_service = build('drive', 'v3', credentials=credentials)

def download_file(file_id, destination_path):
    """Download a file from Google Drive by its ID."""
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}% complete.")

    print(f"File downloaded to {destination_path}")

# Example Usage
if __name__ == "__main__":
    file_id = 'your_file_id_here'  # Replace with the actual file ID
    destination_path = 'downloaded_file.txt'  # Replace with the desired local file path
    download_file(file_id, destination_path)