from constants import *
from logger import *
from uploader import Uploader
from video import Video
from watcher import FileWatcher

log: Logger = get_logger(__name__)

def upload_video(video: Video, uploader: Uploader) -> None:
    """Upload a single video to YouTube.

    Args:
        video (Video): The video to upload.
        uploader (Uploader): Uploads videos to YouTube.
    """
    
    log.info(f'Uploading video: {video.title}')
    
    try:
        uploader.upload_video(
            file_path=str(video.file), 
            title=video.title,
            description=video.description, 
            tags=video.tags
        )
        
        # log.info(f'Successfully uploaded video: {video.title}')
    except Exception as e:
        log.error(f'Failed to upload video: {video.title}')
        log.exception(e)
        raise e


def run() -> None:
    """Run the main loop of the program."""
    uploader = Uploader()
    watcher = FileWatcher()
    for i, file in enumerate(watcher.start_watching()):
        video = Video(file)
        log.debug(f'({i}) Found new video: {video.title}')
        
        if not video.is_valid():
            log.debug(f'Video not valid: {video.title}')
            continue
        
        upload_video(video, uploader)
        watcher.start_tracking(str(video.file))
    else:
        log.info('No new videos found')


def main() -> None:
    log.info('Starting the World of Warcraft VOD uploader...')
    try:
        run()
    except KeyboardInterrupt:
        log.info('Shutting down the World of Warcraft VOD uploader...')
        exit()

if __name__ == "__main__":
    main()