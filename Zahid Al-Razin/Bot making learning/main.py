from drive_service import DriveService
from dropbox_service import DropboxService
from config import ACCOUNTS

def choose_account():
    print("Choose an account:")
    for i, acc in enumerate(ACCOUNTS, 1):
        print(f"{i}. {acc}")
    return ACCOUNTS[int(input("Enter number: ")) - 1]

def choose_service():
    print("\n1. Google Drive\n2. Dropbox")
    choice = input("Choose service: ")
    return "drive" if choice == "1" else "dropbox"

def file_actions(service):
    while True:
        print("\n1. List Files\n2. Upload File\n3. Download File\n4. Exit")
        action = input("Choose action: ")

        if action == "1":
            service.list_files()
        elif action == "2":
            path = input("Enter file path to upload: ")
            service.upload_file(path)
        elif action == "3":
            file_id = input("Enter file ID or name to download: ")
            dest = input("Enter destination path: ")
            service.download_file(file_id, dest)
        elif action == "4":
            break
        else:
            print("Invalid option.")

def main():
    account = choose_account()
    cloud = choose_service()

    if cloud == "drive":
        service = DriveService(account)
    else:
        service = DropboxService(account)

    file_actions(service)

if __name__ == "__main__":
    main()
