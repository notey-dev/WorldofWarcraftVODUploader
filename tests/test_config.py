from pathlib import Path

import pytest
from pydantic import ValidationError

from config import (Authentication, Database, Settings, WarcraftVods,
                    YoutubeVideo)


@pytest.fixture
def mock_is_dir(monkeypatch):
    def mock_is_dir(path):
        return True
    monkeypatch.setattr(Path, "is_dir", mock_is_dir)
    
@pytest.fixture
def mock_root_dir(monkeypatch):
    monkeypatch.setattr('config.ROOT_DIR', Path('.'))


def test_warcraft_vods(mock_is_dir):
    data = {
        "directory": "/path/to/vods",
        "file_types": [".mp4", ".mkv"],
        "search_keywords": ["Raid", "Kill"],
        "difficulties": ["Normal", "Heroic", "Mythic"]
    }
    warcraft_vods = WarcraftVods(**data)
    assert warcraft_vods.directory == Path("/path/to/vods")
    assert warcraft_vods.path == Path("/path/to/vods")
    assert warcraft_vods.file_types == [".mp4", ".mkv"]
    assert warcraft_vods.search_keywords == ["Raid", "Kill"]
    assert warcraft_vods.difficulties == ["Normal", "Heroic", "Mythic"]

def test_youtube_video(mock_is_dir):
    data = {
        "visibility": "unlisted",
        "description": "Test description",
        "tags": ["test", "video"]
    }
    youtube_video = YoutubeVideo(**data)
    assert youtube_video.visibility == "unlisted"
    assert youtube_video.description == "Test description"
    assert youtube_video.tags == ["test", "video"]

def test_authentication(mock_is_dir, mock_root_dir):
    data = {
        "directory": "/path/to/auth",
        "client_secrets_file": "client_secrets.json",
        "token_file": "token.json"
    }
    auth = Authentication(**data)
    assert auth.directory == Path("/path/to/auth")
    assert auth.client_secrets_file == "client_secrets.json"
    assert auth.token_file == "token.json"
    assert auth.client_secrets == Path("/path/to/auth/client_secrets.json")
    assert auth.token == Path("/path/to/auth/token.json")

def test_database(mock_is_dir, mock_root_dir):
    data = {
        "directory": "/path/to/db",
        "name": "database.db"
    }
    db = Database(**data)
    assert db.directory == Path("/path/to/db")
    assert db.name == "database.db"
    assert db.path == Path("/path/to/db/database.db")

def test_settings(mock_is_dir, mock_root_dir):
    data = {
        "log_level": "DEBUG",
        "warcraft_vods": {
            "directory": "/path/to/vods",
            "file_types": [".mp4", ".mkv"],
            "search_keywords": ["Raid", "Kill"],
            "difficulties": ["Normal", "Heroic", "Mythic"]
        },
        "youtube_video": {
            "visibility": "unlisted",
            "description": "Test description",
            "tags": ["test", "video"]
        },
        "authentication": {
            "directory": "/path/to/auth",
            "client_secrets_file": "client_secrets.json",
            "token_file": "token.json"
        },
        "database": {
            "directory": "/path/to/db",
            "name": "database.db"
        }
    }
    settings = Settings(**data)
    assert settings.log_level == "DEBUG"
    assert settings.warcraft.directory == Path("/path/to/vods")
    assert settings.youtube.visibility == "unlisted"
    assert settings.auth.client_secrets == Path("/path/to/auth/client_secrets.json")
    assert settings.database.path == Path("/path/to/db/database.db")

def test_invalid_settings():
    data = {
        "log_level": "INVALID",
        "warcraft_vods": {
            "directory": "/path/to/vods",
            "file_types": [".mp4", ".mkv"],
            "search_keywords": ["Raid", "Kill"],
            "difficulties": ["Normal", "Heroic", "Mythic"]
        },
        "youtube_video": {
            "visibility": "unlisted",
            "description": "Test description",
            "tags": ["test", "video"]
        },
        "authentication": {
            "directory": "/path/to/auth",
            "client_secrets_file": "client_secrets.json",
            "token_file": "token.json"
        },
        "database": {
            "directory": "/path/to/db",
            "name": "database.db"
        }
    }
    with pytest.raises(ValidationError):
        Settings(**data)