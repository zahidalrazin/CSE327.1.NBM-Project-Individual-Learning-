# python -m venv myenv
# myenv\Scripts\activate

# pip install -r requirements.txt

# pip install flask google-auth google-auth-oauthlib google-auth-httplib2 google-auth-requests google-api-python-client

import os
import sys
import time
import json 
import os.path 
from googleapiclient.discovery import build 
from google_auth_oauthlib.flow import InstalledAppFlow 
from google.auth.transport.requests import Request 
from google.oauth2.credentials import Credentials 

from googleapiclient.errors import HttpError 
from googleapiclient.http import MediaFileUpload

# Define the scopes (same for all accounts)
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

# Default filenames for single-account mode
DEFAULT_CREDENTIALS_FILENAME = "credentials.json"
DEFAULT_TOKEN_FILENAME = "token.json"

# Global variable to store storage data for each account
global_storage_data = []

def get_credentials_single() -> Credentials:
    """Gets credentials for a single account using local credentials.json and token.json."""
    creds = None
    if os.path.exists(DEFAULT_TOKEN_FILENAME):
        try:
            with open(DEFAULT_TOKEN_FILENAME, "r") as f:
                creds = Credentials.from_authorized_user_info(json.load(f), SCOPES)
        except Exception as e:
            print(f"Error loading token file {DEFAULT_TOKEN_FILENAME}: {e}")
            creds = None
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Failed to refresh credentials from {DEFAULT_TOKEN_FILENAME}: {e}")
            creds = None
    # If we still don't have valid creds, remove the token file and run the flow.
    if not creds:
        if os.path.exists(DEFAULT_TOKEN_FILENAME):
            os.remove(DEFAULT_TOKEN_FILENAME)
        flow = InstalledAppFlow.from_client_secrets_file(DEFAULT_CREDENTIALS_FILENAME, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(DEFAULT_TOKEN_FILENAME, "w") as f:
            f.write(creds.to_json())
    return creds

def get_credentials_multi(cred_file: str, token_file: str) -> Credentials:
    """Gets credentials for an account using specified credential and token files."""
    creds = None
    if os.path.exists(token_file):
        try:
            with open(token_file, "r") as f:
                creds = Credentials.from_authorized_user_info(json.load(f), SCOPES)
        except Exception as e:
            print(f"Error loading token file {token_file}: {e}")
            creds = None
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Failed to refresh credentials from {token_file}: {e}")
            creds = None
    # If credentials are not available or could not be refreshed, remove token and reauthorize.
    if not creds:
        if os.path.exists(token_file):
            os.remove(token_file)
        flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return creds

def load_services():
    """
    Loads drive services.
    If a 'credentials' folder exists with .json files, load all accounts from there.
    Otherwise, load the default single account.
    """
    accounts = []
    credentials_folder = "credentials"
    if os.path.exists(credentials_folder) and os.path.isdir(credentials_folder):
        credential_files = [f for f in os.listdir(credentials_folder) if f.endswith(".json")]
        if credential_files:
            for cred_filename in credential_files:
                cred_path = os.path.join(credentials_folder, cred_filename)
                # Token file will be named token_<credential_filename>
                token_filename = f"token_{cred_filename}"
                token_path = os.path.join(credentials_folder, token_filename)
                creds = get_credentials_multi(cred_path, token_path)
                drive_service = build("drive", "v3", credentials=creds)
                account_name = os.path.splitext(cred_filename)[0]
                accounts.append((account_name, drive_service))
        else:
            # Fallback to single account if no credential files found in the folder.
            creds = get_credentials_single()
            drive_service = build("drive", "v3", credentials=creds)
            accounts.append(("default", drive_service))
    else:
        # No credentials folder found, use single-account mode.
        creds = get_credentials_single()
        drive_service = build("drive", "v3", credentials=creds)
        accounts.append(("default", drive_service))
    return accounts

def format_size(size_in_bytes):
    """Dynamically formats file size from Bytes to GB, choosing the most appropriate unit."""
    if size_in_bytes >= 1_073_741_824:  # 1 GB
        return f"{size_in_bytes / 1_073_741_824:.2f} GB"
    elif size_in_bytes >= 1_048_576:  # 1 MB
        return f"{size_in_bytes / 1_048_576:.2f} MB"
    elif size_in_bytes >= 1024:  # 1 KB
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes} B"

def get_storage_info(service):
    """Gets the storage info (used and total) for the given Drive service and returns formatted strings."""
    try:
        about = service.about().get(fields="storageQuota").execute()
        used_bytes = int(about["storageQuota"]["usage"])
        total_bytes = int(about["storageQuota"]["limit"])
        used = format_size(used_bytes)
        total = format_size(total_bytes)
        return used, total
    except Exception as e:
        print(f"Error fetching storage info: {e}")
        return "Unknown", "Unknown"

def get_remaining_space(service):
    """Returns the remaining space (in bytes) for the given Drive service."""
    try:
        about = service.about().get(fields="storageQuota").execute()
        used_bytes = int(about["storageQuota"]["usage"])
        total_bytes = int(about["storageQuota"]["limit"])
        return total_bytes - used_bytes
    except Exception as e:
        print(f"Error fetching storage info: {e}")
        return 0

def update_storage_data(accounts):
    """Updates the global storage data list with remaining space for each account."""
    global global_storage_data
    global_storage_data = []
    for (account_name, service) in accounts:
        remaining = get_remaining_space(service)
        global_storage_data.append({
            "account_name": account_name,
            "remaining_space": remaining,
            "service": service
        })

def list_files_all(accounts, page_size=10):
    """Lists files and storage info for each account."""
    for (account_name, service) in accounts:
        print(f"\nAccount: {account_name}")
        used, total = get_storage_info(service)
        print(f"Storage: {used} / {total}")
        try:
            results = service.files().list(pageSize=page_size, fields="files(id, name)").execute()
            items = results.get("files", [])
            if not items:
                print("  No files found.")
            else:
                for item in items:
                    print(f"  {item['name']} ({item['id']})")
        except Exception as e:
            print(f"Error listing files: {e}")

def upload_file_auto(accounts):
    """
    Automatically selects the account with the smallest remaining space that can store the file.
    If no account has enough space, an error is printed.
    """
    file_path = input("Enter the path of the file to upload: ").strip()
    if not os.path.exists(file_path):
        print("Error: The file does not exist.")
        return

    file_size = os.path.getsize(file_path)
    update_storage_data(accounts)
    
    # Sort accounts by remaining_space (ascending)
    sorted_accounts = sorted(global_storage_data, key=lambda x: x["remaining_space"])
    
    chosen_account = None
    for account in sorted_accounts:
        # Check if the account has enough space
        if account["remaining_space"] >= file_size:
            chosen_account = account
            break

    if chosen_account is None:
        print("Error: No account has enough space to upload this file.")
        return

    print(f"Uploading file to account: {chosen_account['account_name']}")
    file_name = os.path.basename(file_path)
    file_metadata = {"name": file_name}
    media = MediaFileUpload(file_path, resumable=True)
    
    try:
        file = chosen_account["service"].files().create(
            body=file_metadata, 
            media_body=media
        ).execute()
        print(f"File uploaded successfully: {file.get('name')} ({file.get('id')})")
        # Optionally, update the remaining space for that account in the global data
        chosen_account["remaining_space"] -= file_size
    except Exception as e:
        print(f"Upload failed: {e}")

def download_file_smart(accounts):
    """
    Searches each account for the file ID entered by the user.
    If the file is found, downloads it from that account.
    Otherwise, shows an error message.
    """
    file_id = input("Enter the file ID to download: ").strip()
    found_service = None
    found_account = None

    # Search for the file across all accounts
    for (account_name, service) in accounts:
        try:
            # Attempt to get file info to confirm its existence
            file_info = service.files().get(fileId=file_id, fields="id, name").execute()
            found_service = service
            found_account = account_name
            break
        except Exception:
            continue

    if found_service is None:
        print("Error: File not found in any account.")
        return
    else:
        print(f"File found in account: {found_account}")

    save_dir = input("Enter the directory to save the file: ").strip()
    if not os.path.exists(save_dir):
        print("Error: The directory does not exist.")
        return
    file_name = input("Enter the name for the saved file (including extension): ").strip()
    save_path = os.path.join(save_dir, file_name)
    try:
        request = found_service.files().get_media(fileId=file_id)
        with open(save_path, "wb") as f:
            f.write(request.execute())
        print(f"File downloaded successfully to: {save_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")

def main():
    accounts = load_services()
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        # Show storage info for each account in the header.
        print("Google Drive Storage for each account:")
        for account_name, service in accounts:
            used, total = get_storage_info(service)
            print(f"  {account_name}: {used} / {total}")
        print("\nOptions:")
        print("  1. List files (from all accounts)")
        print("  2. Upload a file (auto-select based on remaining space)")
        print("  3. Download a file (smart search)")
        print("  4. Exit")
        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            list_files_all(accounts)
        elif choice == "2":
            upload_file_auto(accounts)
        elif choice == "3":
            download_file_smart(accounts)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()