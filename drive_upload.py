import os
import mimetypes
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

print("Script started.")


CHUNK_SIZE = 256 * 1024
SCOPES = ['https://www.googleapis.com/auth/drive.file']


SERVICE_ACCOUNT_FILE = r"C:\Users\ACER\Downloads\amazingstoragesystem-449714-bcadc7670925.json"

# Check if the service account file exists:
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    print(f"Error: Service account file not found at: {SERVICE_ACCOUNT_FILE}")
    exit()

def upload_file_to_drive(file_path, file_name=None, folder_id=None):
    """Uploads file to Drive (chunked) with MIME type detection and retries."""

    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Auth error: {e}")
        return None

    if not file_name:
        file_name = os.path.basename(file_path)

    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    mime_type, _ = mimetypes.guess_type(file_path)  # Detect MIME type
    if not mime_type:
        mime_type = 'application/octet-stream'  # Fallback

    try:
        with open(file_path, 'rb') as f:
            file_size = os.path.getsize(file_path)
            media = MediaIoBaseUpload(f, mimetype=mime_type, chunksize=CHUNK_SIZE, resumable=True)

            print(f"Uploading {file_name} ({file_size} bytes)...")

            response = None
            last_update_time = time.time()
            update_interval = 5  # Update progress every 5 seconds

            retries = 3
            for attempt in range(retries):
                try:
                    while response is None:
                        status, response = media.next_chunk()
                        if status:
                            current_time = time.time()
                            if current_time - last_update_time >= update_interval:
                                progress = int(status.progress() * 100)
                                print(f"Progress: {progress}%", end='\r')
                                last_update_time = current_time
                    print()  # Newline after upload
                    break  # Exit retry loop if successful
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
    """Creates dummy file (for testing)."""
    with open(file_path, 'wb') as f:
        f.write(os.urandom(size_in_bytes))


if __name__ == "__main__":
    file_path = "test_file.txt"
    create_dummy_file(file_path, 1024 * 1024 * 5)  # 5MB dummy file for testing
    folder_id = None




if __name__ == "__main__":
    print("Inside the main block.")  # Check if the main block is executed

    file_path = "test_file.txt"
    print(f"File path: {file_path}")  # Print the file path to make sure it's correct

    create_dummy_file(file_path, 1024 * 1024 * 5)
    print("Dummy file created.")

    folder_id = None  # Or your folder ID
    print(f"Folder ID: {folder_id}")

    uploaded_file_id = upload_file_to_drive(file_path, folder_id=folder_id)

    if uploaded_file_id:
        print(f"File uploaded successfully. ID: {uploaded_file_id}")
    else:
        print("File upload failed.")

    print("Script finished.")


