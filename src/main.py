from pathlib import Path

from uploader import Uploader
from video import Video
from watcher import FileWatcher

SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent

def upload_videos(watcher: FileWatcher, uploader: Uploader) -> None:
    for file in watcher.start_watching():
        video = Video(file)
        print(f'Found {video}')
        
        if not video.is_valid():
            continue
        
        uploader.upload_video(
            file_path=str(video.file), 
            title=video.title,
            description=video.description, 
            tags=['Warcraft', 'Kill', video.difficulty]
        )
        watcher.mark_file_as_observed(str(file))


def main():
    directory_to_watch = Path('D:\\Videos\\Warcraft')
    client_secrets_file = Path(ROOT_DIR, 'auth', 'client_secret.json')
    
    uploader = Uploader(client_secrets_file)

    watcher = FileWatcher(directory_to_watch, 
                            db_path=Path(ROOT_DIR, 'wow_vods.db')
                        )
    
    upload_videos(watcher, uploader)

if __name__ == "__main__":
    main()