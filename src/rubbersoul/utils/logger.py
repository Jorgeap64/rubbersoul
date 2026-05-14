import logging
import os

from logging import Logger
from pathlib import Path

from rubbersoul.utils.utils import DEV_MODE

"""
===============================================================================

	Logger

===============================================================================
"""

if DEV_MODE:
    _LOG_DIR = Path(__file__).resolve().parents[3] / "logs"
else:
    _LOG_DIR = Path(
        os.getenv("XDG_STATE_HOME", Path.home() / ".local" / "state" / "rubbersoul" / "logs" )
    )

def get_logger(name: str, *, log_dir: Path = _LOG_DIR, console: bool = False) -> Logger:
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f"{name}.log"

    log_path = os.path.join(log_dir, log_filename)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    file_handler = logging.FileHandler(log_path, mode="w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Suppress third-party library logs
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("markdown_it").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger.warning(f"Log path: {_LOG_DIR}...")

    return logger
