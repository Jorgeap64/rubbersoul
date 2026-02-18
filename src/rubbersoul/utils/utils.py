import socket

from pathlib import Path
from typing import Final

"""
===============================================================================

	Utils

===============================================================================
"""

RUBBERSOUL_DIR: Path = Path(__file__).resolve().parents[3]
DEFAULT_DIR: Path = Path(".")

_OLLAMA_HOST: Final[str] = "127.0.0.1"
_OLLAMA_PORT: Final[int] = 11434
_TIMEOUT: Final[int] = 1 # seconds

def is_ollama_running(*, host: str=_OLLAMA_HOST, port: int=_OLLAMA_PORT) -> bool:
	try:
		with socket.create_connection((host, port), timeout=_TIMEOUT):
			return True
	except OSError:
		return False
