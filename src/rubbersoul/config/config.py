import json
import logging
import os
import psutil

from dataclasses import dataclass
from pathlib import Path

from rubbersoul.utils.utils import APP_DIR

"""
===============================================================================

	Config

===============================================================================
"""

DEFAULT_DIR: Path = Path(".")
_ENV_JSON: Path = APP_DIR / "env.json"

log = logging.getLogger(__name__)

@dataclass(slots=True)
class Config:
    model: str
    path: Path

    def __init__(self, model: str = "", path: Path = DEFAULT_DIR):
        self.model = model
        self.path = path

    @property
    def dir_name(self) -> str:
        return self.path.resolve().name

    @staticmethod
    def load_config(*, json_: Path = _ENV_JSON) -> "Config":
        if not os.path.exists(json_):
            return Config()
        with open(json_, "r") as f:
            data = json.load(f)
            return Config(**data)

    def save_config(self, *, dir: Path = APP_DIR, json_: Path = _ENV_JSON) -> None:
        os.makedirs(dir, exist_ok=True)
        with open(json_, "w") as f:
            json.dump({"model": self.model}, f, indent=2)

    def empty(self) -> None:
        self.model = ""
        self.path = DEFAULT_DIR

    def is_model_empty(self) -> bool:
        return self.model.strip() == ""

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
