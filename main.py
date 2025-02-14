import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload



def load_drive_service(creds_file):

    SCOPES = ['https://www.googleapis.com/auth/drive']

    credentials = service_account.Credentials.from_service_account_file(creds_file, scopes=SCOPES)

    service = build('drive', 'v3', credentials=credentials)
    return service



def upload_file(service, file_path, folder_id=None):

    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name}

    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("File uploaded successfully. File ID:", file.get('id'))



def list_files(service, query=None):

    results = service.files().list(
        q=query,
        pageSize=100,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])
    if not items:
        print("No files found.")
    else:
        print("\nFiles and Folders:")
        for item in items:
            print("Name: {0}, ID: {1}, Type: {2}".format(item['name'], item['id'], item['mimeType']))



def download_file(service, file_id, destination):

    request = service.files().get_media(fileId=file_id)

    fh = io.FileIO(destination, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    print("Downloading file...")

    while not done:
        status, done = downloader.next_chunk()
        if status:
            print("Download %d%% complete." % int(status.progress() * 100))
    print("File downloaded successfully.")


#
def show_storage_usage(service):

    about = service.about().get(fields="storageQuota").execute()
    quota = about.get('storageQuota', {})

    limit = int(quota.get('limit', 0))
    usage = int(quota.get('usage', 0))
    usage_in_gb = usage / (1024 ** 3)
    if limit > 0:
        limit_in_gb = limit / (1024 ** 3)
        free = limit - usage
        free_in_gb = free / (1024 ** 3)
    else:
        limit_in_gb = None
        free_in_gb = None

    print("\nStorage Usage:")
    print("Used: {:.2f} GB".format(usage_in_gb))
    if limit_in_gb:
        print("Total: {:.2f} GB".format(limit_in_gb))
        print("Remaining: {:.2f} GB".format(free_in_gb))
    else:
        print("Total: Unlimited")
        print("Remaining: Unlimited")



def main():


    drives = {
        "Drive1": load_drive_service("account1.json"),
        "Drive2": load_drive_service("account2.json")
    }

    while True:

        print("\nAvailable Drives:")
        for i, drive_name in enumerate(drives.keys(), 1):
            print(f"{i}. {drive_name}")
        drive_choice = input("Select a drive by number (or type 'exit' to quit): ")
        if drive_choice.lower() == 'exit':
            break
        try:
            drive_choice = int(drive_choice)
            if drive_choice < 1 or drive_choice > len(drives):
                print("Invalid choice. Please try again.")
                continue
        except ValueError:
            print("Please enter a valid number.")
            continue


        drive_name = list(drives.keys())[drive_choice - 1]
        service = drives[drive_name]
        print(f"\nSelected {drive_name}")




        print("\nOperations:")
        print("1. Upload a file")
        print("2. View files/folders")
        print("3. Download a file")
        print("4. Change drive")
        op_choice = input("Select an operation by number: ")

        if op_choice == '1':

            file_path = input("Enter the full path of the file to upload: ")
            if not os.path.isfile(file_path):
                print("File does not exist. Please check the path.")
            else:
                folder_id = input("Enter folder ID (press Enter to upload to root): ")
                if folder_id.strip() == "":
                    folder_id = None
                upload_file(service, file_path, folder_id)
        elif op_choice == '2':

            list_files(service)
        elif op_choice == '3':

            file_id = input("Enter the file ID to download: ")
            destination = input("Enter the destination file path (including file name): ")
            download_file(service, file_id, destination)
        elif op_choice == '4':

            continue
        else:
            print("Invalid operation choice.")


if __name__ == '__main__':
    main()
