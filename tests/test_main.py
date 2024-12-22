from pathlib import Path
from unittest.mock import MagicMock

import pytest

from main import run, upload_video


@pytest.fixture
def mock_settings(monkeypatch):
    mock_setting = MagicMock()
    mock_settings.youtube.visibility = 'unlisted'
    mock_settings.log_level = 'DEBUG'
    monkeypatch.setattr('config.settings', mock_settings)
    return mock_settings

@pytest.fixture
def mock_uploader(monkeypatch):
    mock_uploader = MagicMock()
    monkeypatch.setattr('main.Uploader', mock_uploader)
    return mock_uploader

@pytest.fixture
def mock_video(monkeypatch):
    mock_video = MagicMock()
    monkeypatch.setattr('main.Video', mock_video)
    return mock_video

@pytest.fixture
def mock_file_watcher(monkeypatch):
    mock_file_watcher = MagicMock()
    monkeypatch.setattr('main.FileWatcher', mock_file_watcher)
    return mock_file_watcher

def test_upload_video(mock_settings,  mock_uploader, mock_video):
    # Create mock instances
    mock_uploader_instance = mock_uploader.return_value
    mock_video_instance = mock_video.return_value
    mock_video_instance.title = 'Test Video'
    mock_video_instance.description = 'Test Description'
    mock_video_instance.tags = ['test', 'video']
    mock_video_instance.file = Path('test.mp4')
    mock_video_instance.is_valid.return_value = True

    # Call the function
    upload_video(mock_video_instance, mock_uploader_instance)

    # Assertions
    mock_uploader_instance.upload_video.assert_called_once_with(
        file_path='test.mp4',
        title='Test Video',
        description='Test Description',
        tags=['test', 'video']
    )

def test_run(mock_settings, mock_uploader, mock_file_watcher, mock_video):
     # Create mock instances
    mock_uploader_instance = mock_uploader.return_value
    mock_file_watcher_instance = mock_file_watcher.return_value
    mock_file_watcher_instance.start_watching.return_value = [Path('test.mp4')]
    mock_video_instance = mock_video.return_value
    mock_video_instance.title = 'Test Video'
    mock_video_instance.description = 'Test Description'
    mock_video_instance.tags = ['test', 'video']
    mock_video_instance.file = Path('test.mp4')
    mock_video_instance.is_valid.return_value = True

    # Call the function
    run()

    # Assertions
    mock_file_watcher_instance.start_watching.assert_called_once()
    mock_uploader_instance.upload_video.assert_called()