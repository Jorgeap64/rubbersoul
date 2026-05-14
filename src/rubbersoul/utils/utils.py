import os
import socket

from pathlib import Path
from typing import Final
from importlib.resources import files
from dotenv import load_dotenv


"""
===============================================================================

	Utils

===============================================================================
"""

load_dotenv()
DEV_MODE: Final[bool] = os.getenv("DEV") == "1"

if DEV_MODE:
    APP_DIR = Path(__file__).resolve().parents[3]
else:
    APP_DIR = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "rubbersoul"
    
SKILLS_DIR = files("rubbersoul").joinpath("skills/SKILL.md")

_OLLAMA_HOST: Final[str] = "127.0.0.1"
_OLLAMA_PORT: Final[int] = 11434
_TIMEOUT: Final[int] = 1  # seconds

def is_ollama_running(*, host: str = _OLLAMA_HOST, port: int = _OLLAMA_PORT) -> bool:
    try:
        with socket.create_connection((host, port), timeout=_TIMEOUT):
            return True
    except OSError:
        return False

