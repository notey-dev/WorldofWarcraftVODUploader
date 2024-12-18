from pathlib import Path
from typing import Literal

from dynaconf import Dynaconf
from pydantic import BaseModel, DirectoryPath, Field

SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent


class Database(BaseModel):
    directory: DirectoryPath
    name: str
    table_name: str
    
    @property
    def path(self) -> Path:
        return Path(ROOT_DIR, self.directory, self.name)

class Authentication(BaseModel):
    # The directory where the client secrets and token files are stored
    directory: DirectoryPath
    # The name of the client secrets file in the authentication directory
    client_secrets_file: str
    # The name of the token file in the authentication directory
    token_file: str
    
    @property
    def client_secrets(self) -> Path:
        return Path(ROOT_DIR, self.directory, self.client_secrets_file)
    
    @property
    def token(self) -> Path:
        return Path(ROOT_DIR, self.directory, self.token_file)

class YoutubeVideo(BaseModel):
    # The visibility of the video on YouTube
    visibility: Literal['public', 'private', 'unlisted']
    # The format for the video's description
    description: str
    # Tags to be applied to the video
    tags: list[str]

class Settings(BaseModel):
    warcraft_vod_directory_: DirectoryPath = Field(alias='warcraft_vod_directory')
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    youtube_video: YoutubeVideo
    auth: Authentication = Field(alias='authentication')
    database: Database
    
    @property
    def vod_directory(self) -> Path:
        return Path(self.warcraft_vod_directory_)
    
    @classmethod
    def from_dynaconf(cls, _d: Dynaconf):
        return cls(
            **{k.lower(): v for k, v in _d.items() if v is not None}
        )
    

d = Dynaconf(
    environments=True,
    settings_files=[Path(ROOT_DIR, 'config.yaml')],
)

settings = Settings.from_dynaconf(d)


def reload() -> Settings:
    """

    Returns:
        Settings: The settings object, 
            reloaded with new values from the environment
    """
    d.reload()
    
    global settings
    settings = Settings.from_dynaconf(d)
    return settings