import re
from dataclasses import dataclass as dc
from datetime import datetime
from pathlib import Path


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
    
    def __repr__(self):
        return f'Video({self.title}, {self.killed_at}, {self.difficulty})'
    
    def is_valid(self) -> bool:
        """Check if the file meets the criteria for uploading.
        
        Criteria:
            - The file exists.
            - The file is a .mp4 file.
            - The file name contains 'Kill'.

        Args:
            file (Path): Path object representing the file.

        Returns:
            bool: True if the file is valid, False otherwise.
        """
        return self.file.name.endswith('.mp4') and 'Kill' in self.file.stem