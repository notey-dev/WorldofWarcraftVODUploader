import re
from dataclasses import dataclass as dc
from datetime import datetime
from logging import Logger, getLogger
from pathlib import Path
from typing import Literal

from config import settings

log: Logger = getLogger(__name__)

@dc
class Video:
    file: Path
    
    # -- Properties --
    @property
    def title(self) -> str:
        """Get the title of the video for YouTube

        Returns:
            str: yyyy-mm-dd - {Character} - {Boss} [{difficulty}]
        """
        # Remove time code
        title = re.sub(r'\b\d{2}-\d{2}-\d{2}\b', '', self.file.stem)
        # Remove (Kill) from the title
        return title.replace(' (Kill)', '').strip().replace('  ', ' ')
    
    @property
    def killed_on(self) -> datetime:
        """Get the date the video was created

        Returns:
            datetime: yyyy-mm-dd
        """
        match = re.search(r'(\d{4}-\d{2}-\d{2}) (\d{2}-\d{2}-\d{2})', 
                        self.file.stem)
        return match.group(1) or ''
    
    @property
    def killed_at(self) -> str:
        """Get the time the video was created

        Returns:
            str: hh:mm AM/PM
        """
        time_code_match = re.search(r'\b\d{2}-\d{2}-\d{2}\b', 
                                    self.file.stem)
        time_code = time_code_match.group(0) if time_code_match else ''
        if time_code:
            time_obj = datetime.strptime(time_code, '%H-%M-%S')
            return time_obj.strftime('%I:%M %p')
        
    @property
    def difficulty(self) -> Literal['Normal', 'Heroic', 'Mythic']:
        """Get the difficulty of the raid fight

        Raises:
            ValueError: If the difficulty is not supported

        Returns:
            str: The difficulty of the raid fight
        """
        if '[M]' in self.file.name:
            return 'Mythic'
        elif '[HC]' in self.file.name:
            return 'Heroic'
        elif '[N]' in self.file.name:
            return 'Normal'
        
        raise ValueError(f'Difficulty not found: {self.file.name}')
    
    @property
    def description(self) -> str:
        """Get the description for the YouTube video
        Supports the following tags:
            - {difficulty}
            - {killed_at}
            - {killed_on}

        Returns:
            str: Formatted description for the YouTube video
        """
        unformatted_str: str = settings.youtube.description
        supported_tags: dict = {
            'difficulty': self.difficulty,
            'killed_at': self.killed_at,
            'killed_on': self.killed_on
        }
        
        return unformatted_str.format_map(DynamicDict(supported_tags))
    
    @property
    def tags(self) -> list[str]:
        """Get the tags for the YouTube video
        Supports the following tags:
            - {difficulty}

        Returns:
            list[str]: Formatted list of tags for the YouTube video
        """
        cfg_tags = settings.youtube.tags
        for tag in cfg_tags:
            if tag == r'{difficulty}':
                cfg_tags.remove(tag)
                cfg_tags.append(self.difficulty)
        return cfg_tags
    
    # -- Methods --
    def __repr__(self):
        return f'{self.title}, {self.killed_on}, {self.killed_at}, {self.difficulty}'
    
    def is_valid(self) -> bool:
        """Check if the file meets the criteria for uploading.
        
        Criteria:
            - The file exists.
            - The file is a valid extension.
                (from the settings file)
            - The file name contains any of the keywords.
                (from the settings file

        Args:
            file (Path): Path object representing the file.

        Returns:
            bool: True if the file is valid, False otherwise.
        """
        # Check if the file exists
        if not self.file.exists():
            return False
        
        # Check file type
        if not self.file.suffix in settings.warcraft.file_types:
            return False
        
        # Check if the file name contains the search keywords
        if not any([kw in self.file.stem 
                    for kw in settings.warcraft.search_keywords]):
            return False
        
        # Check difficulty
        if self.difficulty not in settings.warcraft.difficulties:
            return False
        
        return True

class DynamicDict(dict):
    """Helper class to provide default values for missing keys
    
    Used for dynamic string formatting from the config file
    """
    def __missing__(self, key: str) -> str:
        raise Exception(f'Key not supported: {key}')