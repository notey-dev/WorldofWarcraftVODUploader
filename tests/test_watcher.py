import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from watcher import FileWatcher


class TestFileWatcher(TestCase):
    def setUp(self):
        self.patcher_settings = patch('config.settings')
        self.mock_settings = self.patcher_settings.start()
        self.mock_settings.database.path = Path(tempfile.mktemp())
        
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = Path(self.test_dir.name)
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db_path = Path(self.test_db.name)
        
        self.watcher = FileWatcher(
            directory=self.test_dir_path,
            db_path=self.test_db_path
        )
    
    def tearDown(self):
        self.patcher_settings.stop()
        self.test_dir.cleanup()
        self.test_db.close()
        self.watcher.conn.close()
        Path(self.test_db.name).unlink()

    def test_set_table_name(self):
        expected_table_name = '_'.join(self.test_dir_path.parts[1:]).lower()
        self.assertEqual(self.watcher._set_table_name(), expected_table_name)

    def test_create_table(self):
        self.watcher._create_table()
        cursor = self.watcher.conn.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.watcher.table_name}'"
        )
        self.assertIsNotNone(cursor.fetchone())

    def test_is_tracked(self):
        file_path = str(self.test_dir_path / 'test_file.txt')
        self.watcher.start_tracking(file_path)
        self.assertTrue(self.watcher.is_tracked(file_path))
        self.assertFalse(self.watcher.is_tracked('non_existent_file.txt'))

    def test_start_tracking(self):
        file_path = str(self.test_dir_path / 'test_file.txt')
        self.watcher.start_tracking(file_path)
        cursor = self.watcher.conn.execute(
            f"SELECT 1 FROM {self.watcher.table_name} WHERE file_path = ?", (file_path,)
        )
        self.assertIsNotNone(cursor.fetchone())

    def test_stop_tracking(self):
        file_path = str(self.test_dir_path / 'test_file.txt')
        self.watcher.start_tracking(file_path)
        self.watcher.stop_tracking(file_path)
        cursor = self.watcher.conn.execute(
            f"SELECT 1 FROM {self.watcher.table_name} WHERE file_path = ?", (file_path,)
        )
        self.assertIsNone(cursor.fetchone())

    @patch('watcher.time.sleep', return_value=None)
    def test_start_watching(self, mock_sleep):
        # Create some test files
        file1 = self.test_dir_path / 'file1.txt'
        file2 = self.test_dir_path / 'file2.txt'
        file1.touch()
        file2.touch()
    
        generator = self.watcher.start_watching()
        detected_files = sorted([next(generator), next(generator)])
        expected_files = sorted([file1, file2])
        self.assertEqual(detected_files, expected_files)