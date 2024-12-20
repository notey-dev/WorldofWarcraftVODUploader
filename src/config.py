from pathlib import Path
from typing import Literal

from dynaconf import Dynaconf
from pydantic import BaseModel, DirectoryPath, Field

from constants import *


class WarcraftVods(BaseModel):
    # The directory where the Warcraft VODs are stored
    directory: DirectoryPath
    # The file types to search for in the directory
    file_types: list[str]
    # Keywords to search for in the file names
    search_keywords: list[str]
    # The difficulties to search for in the file names
    difficulties: list[Literal['Normal', 'Heroic', 'Mythic']]
    
    @property
    def path(self) -> Path:
        '''Returns the fully qualified path to the directory 
        where the Warcraft VODs are stored'''
        return Path(self.directory)

class Database(BaseModel):
    # The directory where the database file is stored
    directory: DirectoryPath
    # The name of the database file
    name: str
    
    @property
    def path(self) -> Path:
        '''Returns the fully qualified path to the database file'''
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
        '''Returns the fully qualified path to the client secrets file'''
        return Path(ROOT_DIR, self.directory, self.client_secrets_file)
    
    @property
    def token(self) -> Path:
        '''Returns the fully qualified path to the token file'''
        return Path(ROOT_DIR, self.directory, self.token_file)

class YoutubeVideo(BaseModel):
    # The visibility of the video on YouTube
    visibility: Literal['public', 'private', 'unlisted']
    # The format for the video's description
    description: str
    # Tags to be applied to the video
    tags: list[str]

class Settings(BaseModel):
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    warcraft: WarcraftVods = Field(alias='warcraft_vods')
    youtube: YoutubeVideo = Field(alias='youtube_video')
    auth: Authentication = Field(alias='authentication')
    database: Database
    
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
        Settings: The settings object reloaded with new values 
    """
    d.reload()
    
    global settings
    settings = Settings.from_dynaconf(d)
    return settings