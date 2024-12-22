from pathlib import Path
from unittest.mock import patch

import pytest

from video import Video


@pytest.fixture
def mock_settings():
    with patch('video.settings') as mock_settings:
        mock_settings.youtube.description = "Raid fight on {killed_on} at {killed_at} - {difficulty}"
        mock_settings.youtube.tags = ["WoW", "Raid", "{difficulty}"]
        mock_settings.warcraft.file_types = [".mp4", ".mkv"]
        mock_settings.warcraft.search_keywords = ["Raid", "Kill"]
        mock_settings.warcraft.difficulties = ["Normal", "Heroic", "Mythic"]
        yield mock_settings
        
@pytest.fixture
def video_instance():
    file_name = "2023-10-05 12-34-56 - Character - Boss [M] (Kill).mp4"
    return Video(file=Path(file_name))

@pytest.mark.usefixtures("mock_settings")
class TestVideo:
    def test_title(self, video_instance):
        assert video_instance.title == "2023-10-05 - Character - Boss [M]"
    
    def test_description(self, video_instance):
        assert video_instance.description == "Raid fight on 2023-10-05 at 12:34 PM - Mythic"
    
    def test_killed_on(self, video_instance):
        assert video_instance.killed_on == "2023-10-05"

    def test_killed_at(self, video_instance):  
        assert video_instance.killed_at == "12:34 PM"

    def test_difficulty(self, video_instance):
        assert video_instance.difficulty == "Mythic"
    
    def test_tags(self, video_instance):
        expected_tags = ["WoW", "Raid", "Mythic"]
        assert video_instance.tags == expected_tags
    
    def test_invalid_file_extension(self):
        invalid_file = Path("2023-10-05 12-34-56 [M] Raid Kill.avi")
        video = Video(file=invalid_file)
        assert video.is_valid() == False

    def test_missing_keyword(self):
        invalid_file = Path("2023-10-05 12-34-56 [M] NoKeyword.mp4")
        video = Video(file=invalid_file)
        assert video.is_valid() == False

    def test_unsupported_difficulty(self):
        invalid_file = Path("2023-10-05 12-34-56 [X] Raid Kill.mp4")
        video = Video(file=invalid_file)
        with pytest.raises(ValueError):
            video.difficulty
    
    def test_unsupported_tag(self):
        with patch('video.settings') as mock_settings:
            mock_settings.youtube.tags = ["WoW", "Raid", "{unsupported}"]
            video = Video(file=Path("2023-10-05 12-34-56 [M] Raid Kill.mp4"))
            assert video.tags == ["WoW", "Raid", "{unsupported}"]

    def test_unsupported_description_tag(self):
        with patch('video.settings') as mock_settings:
            mock_settings.youtube.description = "Raid fight on {unsupported}"
            video = Video(file=Path("2023-10-05 12-34-56 [M] Raid Kill.mp4"))
            with pytest.raises(Exception, match="Key not supported: unsupported"):
                video.description