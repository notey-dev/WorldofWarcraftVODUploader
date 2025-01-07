import os
from pathlib import Path
from typing import Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import settings
from logger import *

log: Logger = get_logger(__name__)

class Uploader:
    def __init__(self, 
                 client_secrets_file: Path = settings.auth.client_secrets, 
                 token: Path = settings.auth.token,
                 api_service_name: str = 'youtube',
                 api_version: str = 'v3'
                 ) -> None:
        self.client_secrets_file: Path = client_secrets_file
        self.token: Path = token
        self.api_service_name: str = api_service_name
        self.api_version: str = api_version
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.api_service = self.get_authenticated_service()

    def get_authenticated_service(self) -> Any:
        creds: Optional[Credentials] = None
        if os.path.exists(self.token) and os.path.getsize(self.token) > 0:
            creds: Credentials = Credentials.from_authorized_user_file(
                        self.token, 
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
            with open(self.token, 'w') as token:
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
                                resumable=True, 
                                chunksize=4 * 1024 * 1024
                            )
        request = self.api_service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        response = None
        prev_percent = 0
        while response is None:
            status, response = request.next_chunk()
            if not status:
                continue
            percent: int = int(status.progress() * 100)
            if percent % 5 == 0 and percent != prev_percent:
                log.info(f"Uploaded {percent}%")
                prev_percent: int = percent
        log.info(f"Video uploaded successfully: {response['id']}")
        return response['id']