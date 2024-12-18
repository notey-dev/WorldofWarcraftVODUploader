import sqlite3
import time
from pathlib import Path
from typing import Generator

from logger import *


class FileWatcher:
    """ Watches a directory for new files and uploads them to a service
    if they have not been found before. 
    Marks the file as 'found' in the database.
    """
    def __init__(self, 
                 directory: Path, 
                 db_path: Path= Path('files.db')
                 ) -> None:
        self.directory: Path = directory
        self.db_path: Path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self) -> None:
        """Create the table if it does not exist.
        """
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS wow_vods (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT UNIQUE
                )
            ''')

    def is_file_observed(self, file_path: str) -> bool:
        """Check if the file has been found before.

        Args:
            file_path (str): String representation of the file path.

        Returns:
            bool: True if the file has been found before, False otherwise.
        """
        cursor = self.conn.execute(
            'SELECT 1 FROM wow_vods WHERE file_path = ?', (file_path,)
            )
        return cursor.fetchone() is not None

    def mark_file_as_observed(self, file_path: str) -> None:
        """Mark the file as 'found'.

        Args:
            file_path (str): String representation of the file path.
        """
        with self.conn:
            self.conn.execute(
                'INSERT OR IGNORE INTO wow_vods (file_path) VALUES (?)', 
                (file_path,)
                )

    def start_watching(self) -> Generator[Path, None, None]:
        """Start watching the directory for new files.
        Upload the file if it has not been found before.
        Update the database to mark the file as 'found'.
        """
        get_logger().info(f'Watching for new files in {self.directory}')
        while True:
            current_files: set[Path] = set(self.directory.iterdir())
            for file in current_files:
                if self.is_file_observed(str(file)):
                    continue
                
                yield file
                
            get_logger().debug('Sleeping for 15 seconds...')
            time.sleep(15)
            
    # -- Utility functions
    def _remove_indexes(self, start_index: int, end_index: int) -> None:
        """ Utility function for removing indexes from the database. 

        Args:
            start_index (int): Starting range index.
            end_index (int): Ending range index.
        """
        with self.conn:
            self.conn.execute(
                'DELETE FROM wow_vods WHERE id BETWEEN ? AND ?', 
                (start_index, end_index)
                )
            self.conn.commit()  
    
    def _copy_table(self, src_table: str, dst_table: str) -> None:
        """Utility function to copy all rows from one table to another.

        Args:
            source_table (str): Name of the source table.
            destination_table (str): Name of the destination table.
        """
        with self.conn:
            self.conn.execute(f'''
                INSERT OR IGNORE INTO {dst_table} (id, file_path)
                SELECT id, file_path FROM {src_table}
            ''')
            self.conn.commit()

if __name__ == '__main__':
    ROOT_DIR = Path(__file__).resolve().parent.parent
    watcher = FileWatcher(Path('D:\\Videos\\Warcraft'),
                          Path(ROOT_DIR, 'wow_vods.db')
                          )
    watcher.copy_table('observed_files', 'wow_vods')
    
