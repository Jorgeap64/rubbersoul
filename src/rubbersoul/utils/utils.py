import logging
import os
import socket
from pathlib import Path
from typing import Final
from importlib.resources import files

import psutil

"""
===============================================================================

	Utils

===============================================================================
"""

APP_DIR = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "rubbersoul"
SKILLS_DIR = files("rubbersoul").joinpath("skills/SKILL.md")
DEFAULT_DIR = Path(".")

_OLLAMA_HOST: Final[str] = "127.0.0.1"
_OLLAMA_PORT: Final[int] = 11434
_TIMEOUT: Final[int] = 1  # seconds

log = logging.getLogger(__name__)


def is_ollama_running(*, host: str = _OLLAMA_HOST, port: int = _OLLAMA_PORT) -> bool:
    try:
        with socket.create_connection((host, port), timeout=_TIMEOUT):
            return True
    except OSError:
        return False


def get_available_ram_gb() -> float:
    try:
        return psutil.virtual_memory().available / (1024**3)
    except ImportError:
        log.warning("psutil not installed — assuming 8 GB RAM")
        return 8.0


def get_available_vram_gb() -> float:
    # NVIDIA
    try:
        import pynvml

        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return info.free / (1024**3)
    except Exception:
        pass

    # AMD
    try:
        import rsmi

        r = rsmi.rsmi_wrapper()
        r.rsmi_init(0)
        _, used = r.rsmi_dev_memory_usage_get(0, rsmi.RSMI_MEM_TYPE_VRAM)
        _, total = r.rsmi_dev_memory_total_get(0, rsmi.RSMI_MEM_TYPE_VRAM)
        return (total - used) / (1024**3)
    except Exception:
        pass

    log.warning("Could not detect VRAM — assuming CPU-only (0 GB VRAM)")
    return 0.0
