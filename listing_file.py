from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuration
SERVICE_ACCOUNT_FILE = 'path/to/your/service_account.json'  # Path to your service account JSON file
BUCKET_FOLDER_ID = 'your_bucket_folder_id'  # Replace with your Google Drive folder ID

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive']
)
drive_service = build('drive', 'v3', credentials=credentials)

def list_files(folder_id):
    """List all files in a specific Google Drive bucket."""
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print("No files found in the bucket.")
    else:
        print("Files in the bucket:")
        for file in files:
            print(f"{file['name']} (ID: {file['id']})")

# Example Usage
if __name__ == "__main__":
    list_files(BUCKET_FOLDER_ID)