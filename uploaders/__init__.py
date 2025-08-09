from typing import Protocol


class UploaderProtocol(Protocol):
    def upload_video(
        self, file_path: str, title: str, description: str, tags: list[str]
    ) -> str: ...


def get_uploader(uploader_name: str) -> UploaderProtocol:
    """
    Factory function to get the appropriate uploader instance based on the uploader name.
    """
    from uploaders.youtube import YoutubeUploader

    if uploader_name == "youtube":
        return YoutubeUploader()
    else:
        raise ValueError(f"Unsupported uploader: {uploader_name}")
