from pathlib import Path

__all__ = ['ROOT_DIR', 'SRC_DIR', 'LOG_DIR', 'AUTH_DIR']

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / 'src'
LOG_DIR = ROOT_DIR / 'logs'
AUTH_DIR = ROOT_DIR / 'auth'
