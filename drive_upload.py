import os
import mimetypes
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

print("Script started.")

CHUNK_SIZE = 256 * 1024  # 256KB chunk size for resumable uploads
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = r"C:\Users\ACER\Downloads\amazingstoragesystem-449714-bcadc7670925.json"

# Check if the service account file exists:
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    print(f"Error: Service account file not found at: {SERVICE_ACCOUNT_FILE}")
    exit()


def upload_file_to_drive(file_path, file_name=None, folder_id=None):
    """Uploads a file to Google Drive with chunked upload and retries."""
    try:
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Auth error: {e}")
        return None

    if not file_name:
        file_name = os.path.basename(file_path)

    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'

    try:
        with open(file_path, 'rb') as f:
            file_size = os.path.getsize(file_path)
            media = MediaIoBaseUpload(f, mimetype=mime_type, chunksize=CHUNK_SIZE, resumable=True)

            print(f"Uploading {file_name} ({file_size} bytes)...")

            request = service.files().create(body=file_metadata, media_body=media, fields="id")

            response = None
            last_update_time = time.time()
            update_interval = 5  # Update progress every 5 seconds
            retries = 3

            for attempt in range(retries):
                try:
                    while response is None:
                        status, response = request.next_chunk()
                        if status:
                            current_time = time.time()
                            if current_time - last_update_time >= update_interval:
                                progress = int(status.progress() * 100)
                                print(f"Progress: {progress}%", end='\r')
                                last_update_time = current_time
                    print("\nUpload complete.")
                    break
                except HttpError as error:
                    if error.resp.status == 429:
                        wait_time = 2 ** attempt
                        print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"An HTTP error occurred: {error}")
                        return None
                except Exception as e:
                    print(f"An error occurred: {e}")
                    return None

            if response:
                print(f"File ID: {response.get('id')}")
                return response.get('id')
            else:
                print("Upload failed after multiple retries.")
                return None

    except Exception as e:
        print(f"Upload error: {e}")
        return None


def create_dummy_file(file_path, size_in_bytes):
    """Creates a dummy file for testing."""
    with open(file_path, 'wb') as f:
        f.write(os.urandom(size_in_bytes))


def share_file(file_id, email):
    """Shares the uploaded file with a personal Google Drive account."""
    try:
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)

        permission = {
            'type': 'user',
            'role': 'writer',  # 'reader' for view-only access
            'emailAddress': email
        }

        service.permissions().create(fileId=file_id, body=permission, fields='id').execute()
        print(f"✅ File shared with {email}")
    except Exception as e:
        print(f"❌ Error sharing file: {e}")


if __name__ == "__main__":
    print("Inside the main block.")

    file_path = "test_file.txt"
    print(f"File path: {file_path}")

    create_dummy_file(file_path, 1024 * 1024 * 50)  # 50MB file
    print("Dummy file created.")

    folder_id = None  # Replace with actual folder ID if needed
    print(f"Folder ID: {folder_id}")

    uploaded_file_id = upload_file_to_drive(file_path, folder_id=folder_id)

    if uploaded_file_id:
        print(f"File uploaded successfully. ID: {uploaded_file_id}")
        print(f"Check the file at: https://drive.google.com/file/d/{uploaded_file_id}/view")

        # Share the file after uploading
        your_email = "shumaiha.rahman@northsouth.edu"
        share_file(uploaded_file_id, your_email)
    else:
        print("File upload failed.")

    print("Script finished.")