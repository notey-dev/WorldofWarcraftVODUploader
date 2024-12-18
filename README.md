# YouTube Uploader

This project is an automated script that watches a specified directory for new video files and uploads them to a designated YouTube channel using the YouTube API.

## Features

- Monitors a directory for new video files.
- Automatically uploads new files to YouTube.
- Utilizes the YouTube API for seamless integration.

## Project Structure

```
youtube-uploader
├── src
│   ├── main.py          # Entry point of the application
│   ├── uploader.py      # Handles YouTube API interactions
│   ├── watcher.py       # Monitors the directory for new files
│   └── utils
│       └── __init__.py  # Utility functions and constants
├── requirements.txt      # Project dependencies
├── pyproject.toml        # Poetry configuration
└── README.md             # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd youtube-uploader
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Configure your YouTube API credentials in the `src/utils/__init__.py` file.

4. Run the application:
   ```
   poetry run python src/main.py
   ```

## Usage

- Place video files in the monitored directory.
- The script will automatically upload any new files to your YouTube channel.

## License

This project is licensed under the MIT License.