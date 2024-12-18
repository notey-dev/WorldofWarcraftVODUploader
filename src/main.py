from pathlib import Path

from config import settings
from logger import *
from uploader import Uploader
from video import Video
from watcher import FileWatcher

SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent

def upload_videos(watcher: FileWatcher, uploader: Uploader) -> None:
    for file in watcher.start_watching():
        video = Video(file)
        get_logger().debug(f'Found new video: {video.title}')
        
        if not video.is_valid():
            get_logger().debug(f'Video not valid: {video.title}')
            continue
        
        get_logger().info(f'Uploading video: {video.title}')
        
        print(video.tags)
        
        uploader.upload_video(
            file_path=str(video.file), 
            title=video.title,
            description=video.description, 
            tags=video.tags
        )
        watcher.mark_file_as_observed(str(file))


def main():
    get_logger().info('Starting the World of Warcraft VOD uploader...')
    uploader = Uploader(settings.auth.client_secrets)
    watcher = FileWatcher(
        directory=settings.vod_directory, 
        db_path=settings.database.path
    )
    
    upload_videos(watcher, uploader)

if __name__ == "__main__":
    main()