import os
import mimetypes
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

CHUNK_SIZE = 256 * 1024

def authenticate_service(service_account_file):
    creds = service_account.Credentials.from_service_account_file(service_account_file)
    return build('drive', 'v3', credentials=creds)

def upload_file_to_drive(service, file_path):
    file_name = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)

    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path, mimetype=mime_type, chunksize=CHUNK_SIZE, resumable=True)

    request = service.files().create(body=file_metadata, media_body=media, fields='id')
    response = request.execute()
    print(f"Uploaded {file_name} to Drive with ID: {response['id']}")

def main():
    file_path = "path_to_your_file.txt"  # Replace with the path to the file you want to upload
    for service_account_file in SERVICE_ACCOUNT_FILES:
        service = authenticate_service(service_account_file)
        upload_file_to_drive(service, file_path)

if __name__ == "__main__":
    main()