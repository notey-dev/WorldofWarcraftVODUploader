from config import settings
from constants import *
from logger import *
from uploader import Uploader
from video import Video
from watcher import FileWatcher


def upload_videos(watcher: FileWatcher, uploader: Uploader) -> None:
    """Uploaded newly found Warcraft VODs to YouTube.

    Args:
        watcher (FileWatcher): Watches for new Warcraft VODs.
        uploader (Uploader): Uploads videos to YouTube.

    Raises:
        e: Any exception that occurs during the upload process.
    """
    for file in watcher.start_watching():
        video = Video(file)
        get_logger().debug(f'Found new video: {video.title}')
        
        if not video.is_valid():
            get_logger().debug(f'Video not valid: {video.title}')
            continue
        
        get_logger().info(f'Uploading video: {video.title}')
        
        try:
            uploader.upload_video(
                file_path=str(video.file), 
                title=video.title,
                description=video.description, 
                tags=video.tags
            )
        except Exception as e:
            get_logger().error(f'Failed to upload video: {video.title}')
            get_logger().exception(e)
            raise e
        watcher.mark_file_as_observed(str(file))


def main() -> None:
    get_logger().info('Starting the World of Warcraft VOD uploader...')
    uploader = Uploader(settings.auth.client_secrets)
    watcher = FileWatcher(
        directory=settings.warcraft.path, 
        db_path=settings.database.path
    )
    
    upload_videos(watcher, uploader)

if __name__ == "__main__":
    main()