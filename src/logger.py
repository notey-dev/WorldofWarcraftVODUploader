import logging

from config import settings
from constants import LOG_DIR

__all__ = ['get_logger']

LOG_FILE = LOG_DIR / 'app.log'

# Create the log directory if it doesn't exist
LOG_DIR.mkdir(exist_ok=True)

def get_log_level(level_str: str) -> int:
    return getattr(logging, level_str.upper(), logging.INFO)

# Configure the logger
logging.basicConfig(
    level=get_log_level(settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Create a logger instance
logger = logging.getLogger(__name__)

def get_logger() -> logging.Logger:
    return logger