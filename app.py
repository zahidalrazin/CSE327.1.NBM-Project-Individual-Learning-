# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os

# Configuration for Google Drive service accounts
SERVICE_ACCOUNT_FILES = [
    r"path_to_your_first_service_account.json",
    r"path_to_your_second_service_account.json",
    # Add more service account paths as needed
]

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def authenticate_service(service_account_file):
    """Authenticate and return the Google Drive service."""
    creds = service_account.Credentials.from_service_account_file(service_account_file)
    return build('drive', 'v3', credentials=creds)

def list_files(service):
    """List files in the Google Drive account."""
    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    return items

def upload_file(service, file):
    """Upload a file to Google Drive."""
    file_metadata = {'name': file.filename}
    media = MediaFileUpload(file.file, mimetype=file.content_type)
    service.files().create(body=file_metadata, media_body=media).execute()

def delete_file(service, file_id):
    """Delete a file from Google Drive."""
    service.files().delete(fileId=file_id).execute()

@app.get("/", response_class=HTMLResponse)
async def index(request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/files")
async def files():
    all_files = []
    for service_account_file in SERVICE_ACCOUNT_FILES:
        service = authenticate_service(service_account_file)
        files = list_files(service)
        all_files.extend(files)
    return all_files

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    for service_account_file in SERVICE_ACCOUNT_FILES:
        service = authenticate_service(service_account_file)
        upload_file(service, file)
    return {"message": "File uploaded successfully!"}

@app.delete("/delete/{file_id}")
async def delete(file_id: str):
    for service_account_file in SERVICE_ACCOUNT_FILES:
        service = authenticate_service(service_account_file)
        delete_file(service, file_id)
    return {"message": "File deleted successfully!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)