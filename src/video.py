import re
from dataclasses import dataclass as dc
from datetime import datetime
from pathlib import Path

from config import settings
from logger import *


@dc
class Video:
    file: Path
    
    @property
    def title(self) -> str:
        # Remove time code
        title = re.sub(r'\b\d{2}-\d{2}-\d{2}\b', '', self.file.stem)
        # Remove (Kill) from the title
        return title.replace(' (Kill)', '').strip().replace('  ', ' ')
    
    @property
    def killed_at(self) -> str:
        time_code_match = re.search(r'\b\d{2}-\d{2}-\d{2}\b', 
                                    self.file.stem)
        time_code = time_code_match.group(0) if time_code_match else ''
        if time_code:
            time_obj = datetime.strptime(time_code, '%H-%M-%S')
            return time_obj.strftime('%I:%M %p')
        return 'Unknown'
    
    @property
    def difficulty(self) -> str:
        if '[M]' in self.file.name:
            return 'Mythic'
        elif '[HC]' in self.file.name:
            return 'Heroic'
        elif '[N]' in self.file.name:
            return 'Normal'
        
        raise ValueError(f'Difficulty not found: {self.file.name}')
    
    @property
    def description(self):
        return f'Killed at {self.killed_at} on {self.difficulty}'
    
    @property
    def tags(self) -> list[str]:
        cfg_tags = settings.youtube.tags
        for tag in cfg_tags:
            if tag == r'{difficulty}':
                cfg_tags.remove(tag)
                cfg_tags.append(self.difficulty)
        return cfg_tags
    
    def __repr__(self):
        return f'Video({self.title}, {self.killed_at}, {self.difficulty})'
    
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
        
        return True