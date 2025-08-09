import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from uploaders.youtube import Uploader


class TestUploader(unittest.TestCase):

    @patch('uploader.Credentials')
    @patch('uploader.os.path.exists')
    @patch('uploader.build')
    def test_get_authenticated_service_with_existing_token(self, mock_build, mock_exists, mock_credentials):
        mock_exists.return_value = True
        mock_credentials.from_authorized_user_file.return_value = MagicMock(valid=True)
        
        uploader = Uploader()
        service = uploader.get_authenticated_service()
        
        mock_exists.assert_called_once_with(Path(uploader.TOKEN_PATH))
        mock_credentials.from_authorized_user_file.assert_called_once()
        mock_build.assert_called_once_with(uploader.api_service_name, uploader.api_version, credentials=mock_credentials.from_authorized_user_file.return_value)
        self.assertEqual(service, mock_build.return_value)

    @patch('uploader.Credentials')
    @patch('uploader.os.path.exists')
    @patch('uploader.InstalledAppFlow')
    @patch('uploader.build')
    def test_get_authenticated_service_without_existing_token(self, mock_build, mock_flow, mock_exists, mock_credentials):
        mock_exists.return_value = False
        mock_flow.from_client_secrets_file.return_value.run_local_server.return_value = MagicMock()
        
        uploader = Uploader()
        service = uploader.get_authenticated_service()
        
        mock_exists.assert_called_once_with(Path(uploader.TOKEN_PATH))
        mock_flow.from_client_secrets_file.assert_called_once_with(uploader.client_secrets_file, uploader.scopes)
        mock_build.assert_called_once_with(uploader.api_service_name, uploader.api_version, credentials=mock_flow.from_client_secrets_file.return_value.run_local_server.return_value)
        self.assertEqual(service, mock_build.return_value)

    @patch('uploader.MediaFileUpload')
    @patch('uploader.Uploader.get_authenticated_service')
    def test_upload_video(self, mock_get_authenticated_service, mock_media_file_upload):
        mock_service = MagicMock()
        mock_get_authenticated_service.return_value = mock_service
        mock_request = mock_service.videos().insert.return_value
        mock_request.next_chunk.side_effect = [(MagicMock(progress=lambda: 0.5), None), (None, {'id': 'video_id'})]
        
        uploader = Uploader()
        video_id = uploader.upload_video('test.mp4', 'Test Title', 'Test Description', ['test', 'video'])
        
        mock_media_file_upload.assert_called_once_with('test.mp4', resumable=True, chunksize=4 * 1024 * 1024)
        mock_service.videos().insert.assert_called_once()
        self.assertEqual(video_id, 'video_id')

if __name__ == '__main__':
    unittest.main()