import os
import json
import dropbox
import requests
from msal import ConfidentialClientApplication
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Define the scopes for Google Drive, OneDrive, and Dropbox
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

ONEDRIVE_SCOPES = ["Files.ReadWrite.All"]
DROPBOX_SCOPES = ["files.content.write", "files.content.read"]

# Default filenames for single-account mode
DEFAULT_CREDENTIALS_FILENAME = "credentials.json"
DEFAULT_TOKEN_FILENAME = "token.json"

# Global variable to store storage data for each account
global_storage_data = []

# Google Drive Functions
def get_credentials_single() -> Credentials:
    creds = None
    if os.path.exists(DEFAULT_TOKEN_FILENAME):
        try:
            with open(DEFAULT_TOKEN_FILENAME, "r") as f:
                creds = Credentials.from_authorized_user_info(json.load(f), GOOGLE_SCOPES)
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
    if not creds:
        if os.path.exists(DEFAULT_TOKEN_FILENAME):
            os.remove(DEFAULT_TOKEN_FILENAME)
        flow = InstalledAppFlow.from_client_secrets_file(DEFAULT_CREDENTIALS_FILENAME, GOOGLE_SCOPES)
        creds = flow.run_local_server(port=0)
        with open(DEFAULT_TOKEN_FILENAME, "w") as f:
            f.write(creds.to_json())
    return creds

def get_storage_info(service):
    try:
        about = service.about().get(fields="storageQuota").execute()
        used_bytes = int(about["storageQuota"]["usage"])
        total_bytes = int(about["storageQuota"]["limit"])
        return used_bytes, total_bytes
    except Exception as e:
        print(f"Error fetching storage info: {e}")
        return 0, 0

def load_google_drive_service():
    creds = get_credentials_single()
    return build("drive", "v3", credentials=creds)

# OneDrive Functions
def get_onedrive_credentials(client_id, client_secret, tenant_id):
    app = ConfidentialClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant_id}", client_credential=client_secret)
    result = app.acquire_token_for_client(scopes=ONEDRIVE_SCOPES)
    return result['access_token']

def get_onedrive_storage_info(access_token):
    response = requests.get("https://graph.microsoft.com/v1.0/me/drive", headers={"Authorization": f"Bearer {access_token}"})
    if response.status_code == 200:
        data = response.json()
        return data['quota']['used'], data['quota']['total']
    else:
        print("Error fetching OneDrive storage info")
        return 0, 0

# Dropbox Functions
def get_dropbox_credentials(access_token):
    return dropbox.Dropbox(access_token)

def get_dropbox_storage_info(client):
    return client.users_get_space_usage()

# Load Services
def load_services():
    accounts = []

    # Load Google Drive
    drive_service = load_google_drive_service()
    accounts.append(("Google Drive", drive_service))

    # Load OneDrive
    onedrive_client_id = "YOUR_ONEDRIVE_CLIENT_ID"
    onedrive_client_secret = "YOUR_ONEDRIVE_CLIENT_SECRET"
    onedrive_tenant_id = "YOUR_ONEDRIVE_TENANT_ID"
    onedrive_token = get_onedrive_credentials(onedrive_client_id, onedrive_client_secret, onedrive_tenant_id)
    accounts.append(("OneDrive", onedrive_token))

    # Load Dropbox
    dropbox_access_token = "YOUR_DROPBOX_ACCESS_TOKEN"
    dropbox_client = get_dropbox_credentials(dropbox_access_token)
    accounts.append(("Dropbox", dropbox_client))

    return accounts

def format_size(size_in_bytes):
    if size_in_bytes >= 1_073_741_824:  # 1 GB
        return f"{size_in_bytes / 1_073_741_824:.2f} GB"
    elif size_in_bytes >= 1_048_576:  # 1 MB
        return f"{size_in_bytes / 1_048_576:.2f} MB"
    elif size_in_bytes >= 1024:  # 1 KB
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes} B"

def update_storage_data(accounts):
    global global_storage_data
    global_storage_data = []
    for (account_name, service) in accounts:
        if account_name == "Google Drive":
            used, total = get_storage_info(service)
        elif account_name == "OneDrive":
            used, total = get_onedrive_storage_info(service)
        elif account_name == "Dropbox":
            usage = get_dropbox_storage_info(service)
            used = usage.used
            total = usage.allocation.get_individual().allocated
        global_storage_data.append({
            "account_name": account_name,
            "used_space": used,
            "total_space": total,
            "remaining_space": total - used,
            "service": service
        })

def list_files_all(accounts):
    for (account_name, service) in accounts:
        print(f"\nAccount: {account_name}")
        if account_name == "Google Drive":
            used, total = get_storage_info(service)
            print(f"Storage: {format_size(used)} / {format_size(total)}")
            try:
                results = service.files().list(pageSize=10, fields="files(id, name)").execute()
                items = results.get("files", [])
                if not items:
                    print("  No files found.")
                else:
                    for item in items:
                        print(f"  {item['name']} ({item['id']})")
            except Exception as e:
                print(f"Error listing files: {e}")
        elif account_name == "OneDrive":
            used, total = get_onedrive_storage_info(service)
            print(f"Storage: {format_size(used)} / {format_size(total)}")
            # OneDrive file listing can be implemented here
        elif account_name == "Dropbox":
            usage = get_dropbox_storage_info(service)
            used = usage.used
            total = usage.allocation.get_individual().allocated
            print(f"Storage: {format_size(used)} / {format_size(total)}")
            # Dropbox file listing can be implemented here

def upload_file_auto(accounts):
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
        if account["remaining_space"] >= file_size:
            chosen_account = account
            break

    if chosen_account is None:
        print("Error: No account has enough space to upload this file.")
        return

    print(f"Uploading file to account: {chosen_account['account_name']}")
    file_name = os.path.basename(file_path)

    if chosen_account["account_name"] == "Google Drive":
        file_metadata = {"name": file_name}
        media = MediaFileUpload(file_path, resumable=True)
        try:
            file = chosen_account["service"].files().create(body=file_metadata, media_body=media).execute()
            print(f"File uploaded successfully: {file.get('name')} ({file.get('id')})")
        except Exception as e:
            print(f"Upload failed: {e}")
    elif chosen_account["account_name"] == "OneDrive":
        with open(file_path, "rb") as f:
            response = requests.put(f"https://graph.microsoft.com/v1.0/me/drive/root:/{file_name}:/content",
                                    headers={"Authorization": f"Bearer {chosen_account['service']}"}, data=f)
            if response.status_code == 201:
                print(f"File uploaded successfully to OneDrive: {file_name}")
            else:
                print("Upload failed to OneDrive.")
    elif chosen_account["account_name"] == "Dropbox":
        with open(file_path, "rb") as f:
            chosen_account["service"].files_upload(f.read(), f"/{file_name}")
            print(f"File uploaded successfully to Dropbox: {file_name}")

def download_file_smart(accounts):
    file_id = input("Enter the file ID to download: ").strip()
    found_service = None
    found_account = None

    for (account_name, service) in accounts:
        try:
            if account_name == "Google Drive":
                file_info = service.files().get(fileId=file_id, fields="id, name").execute()
                found_service = service
                found_account = account_name
                break
            elif account_name == "OneDrive":
                # Implement OneDrive file search logic here
                pass
            elif account_name == "Dropbox":
                # Implement Dropbox file search logic here
                pass
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
        if found_account == "Google Drive":
            request = found_service.files().get_media(fileId=file_id)
            with open(save_path, "wb") as f:
                f.write(request.execute())
            print(f"File downloaded successfully to: {save_path}")
        elif found_account == "OneDrive":
            # Implement OneDrive file download logic here
            pass
        elif found_account == "Dropbox":
            # Implement Dropbox file download logic here
            pass
    except Exception as e:
        print(f"Error downloading file: {e}")

def main():
    accounts = load_services()
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("Storage for each account:")
        for account in accounts:
            account_name = account[0]
            if account_name == "Google Drive":
                used, total = get_storage_info(account[1])
            elif account_name == "OneDrive":
                used, total = get_onedrive_storage_info(account[1])
            elif account_name == "Dropbox":
                usage = get_dropbox_storage_info(account[1])
                used = usage.used
                total = usage.allocation.get_individual().allocated
            print(f"  {account_name}: {format_size(used)} / {format_size(total)}")

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