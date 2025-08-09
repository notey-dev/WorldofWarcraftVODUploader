import logging
from logging import Logger

from config import settings
from constants import LOG_DIR

__all__ = ["get_logger", "Logger"]

LOG_FILE = LOG_DIR / "app.log"

# Create the log directory if it doesn't exist
LOG_DIR.mkdir(exist_ok=True)


def get_log_level(level_str: str) -> int:
    """Returns the logging level based on the string representation"""
    return getattr(logging, level_str.upper(), logging.INFO)


# Configure the logger
logging.basicConfig(
    level=get_log_level(settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        # logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ],
)


def get_logger(name: str) -> logging.Logger:
    """Returns the logger instance"""
    if name == "__main__":
        name = "main"
    return logging.getLogger(name)
