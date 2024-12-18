import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import settings

ROOT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = Path(ROOT_DIR, 'auth', 'token.json')

class Uploader:
    def __init__(self, client_secrets_file: Path, 
                 api_service_name='youtube',
                 api_version='v3'):
        self.client_secrets_file: Path = client_secrets_file
        self.api_service_name: str = api_service_name
        self.api_version: str = api_version
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.api_service = self.get_authenticated_service()

    def get_authenticated_service(self):
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(
                        TOKEN_PATH, 
                        self.scopes
                    )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secrets_file, 
                        self.scopes
                    )
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        return build(self.api_service_name, 
                     self.api_version, 
                     credentials=creds
                )

    def upload_video(self, 
                    file_path: str, 
                    title: str, 
                    description: str, 
                    tags: list[str]
                ) -> str:
        body: dict = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': settings.youtube.visibility
        }
    }
        media = MediaFileUpload(file_path, 
                                chunksize=-1, 
                                resumable=True
                            )
        request = self.api_service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")
        print(f"Video uploaded successfully: {response['id']}")
        return response['id']