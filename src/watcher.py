import sqlite3
import time
from pathlib import Path
from typing import Generator

from config import settings
from logger import *

log: Logger = get_logger(__name__)

class FileWatcher:
    """ Watches a directory for new files and uploads them to a service
    if they have not been found before. 
    Marks the file as 'found' in the database.
    """
    def __init__(self, 
                 directory: Path = settings.warcraft.path,
                 db_path: Path = settings.database.path,
                 ) -> None:
        self.directory: Path = directory
        self.db_path: Path = db_path
        # Set table name to the directory's path with underscores
        self.table_name: str = self._set_table_name()
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()
        
    # -- Private methods --
    def _set_table_name(self) -> str:
        return '_'.join(self.directory.parts[1:]).lower()

    def _create_table(self) -> None:
        """Create the table if it does not exist.
        """
        with self.conn:
            self.conn.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT UNIQUE
                )
            ''')
            
    # -- DB methods --
    def is_tracked(self, file_path: str) -> bool:
        """Check if the file is in the database

        Args:
            file_path (str): String representation of the file path.

        Returns:
            bool: True if the file has been found before, False otherwise.
        """
        cursor = self.conn.execute(
            f'SELECT 1 FROM {self.table_name} WHERE file_path = ?', (file_path,)
            )
        return cursor.fetchone() is not None

    def start_tracking(self, file_path: str) -> None:
        """Add the file to the database.

        Args:
            file_path (str): String representation of the file path.
        """
        log.info(f'Tracking file: {file_path}')
        with self.conn:
            self.conn.execute(
                f'INSERT OR IGNORE INTO {self.table_name} (file_path) VALUES (?)', 
                (file_path,)
                )
    
    def stop_tracking(self, file_path: str) -> None:
        """Remove the file from the database.

        Args:
            file_path (str): String representation of the file path.
        """
        log.info(f'Stopping tracking for file: {file_path}')
        with self.conn:
            self.conn.execute(
                f'DELETE FROM {self.table_name} WHERE file_path = ?', 
                (file_path,)
                )

    # -- File methods -- 
    def start_watching(self) -> Generator[Path, None, None]:
        """ Get all untracked files in the directory 
            sorted by creation data and yield them.
        """
        log.info(f'Watching for new files in {self.directory}')
        current_files: set[Path] = sorted(set(self.directory.iterdir()), 
                                          key=lambda f: f.stat().st_mtime
                                          )
        while True:
            for file in current_files:
                if self.is_tracked(str(file)):
                    continue
                
                yield file
                    
            log.info('Sleeping for 15 seconds...')
            time.sleep(15)
