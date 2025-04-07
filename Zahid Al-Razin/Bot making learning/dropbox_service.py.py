import dropbox
from config import DROPBOX_TOKENS

class DropboxService:
    def __init__(self, account):
        self.dbx = dropbox.Dropbox(DROPBOX_TOKENS[account])

    def list_files(self):
        files = self.dbx.files_list_folder('').entries
        for f in files:
            print(f.name)

    def upload_file(self, filepath):
        with open(filepath, 'rb') as f:
            self.dbx.files_upload(f.read(), f"/{os.path.basename(filepath)}", mode=dropbox.files.WriteMode.overwrite)
        print("Uploaded to Dropbox.")

    def download_file(self, filename, destination):
        with open(destination, 'wb') as f:
            metadata, res = self.dbx.files_download(path=f"/{filename}")
            f.write(res.content)
        print("Downloaded from Dropbox.")
