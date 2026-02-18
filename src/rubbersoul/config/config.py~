import os
import json

from pathlib import Path
from dataclasses import dataclass

from rubbersoul.utils.utils import RUBBERSOUL_DIR 

"""
===============================================================================

	Config

===============================================================================
"""

DEFAULT_DIR: Path = Path(".")

_ENV_DIR: Path = RUBBERSOUL_DIR / ".env"
_ENV_JSON: Path = _ENV_DIR / "env.json"

@dataclass(slots=True)
class Config:
	model: str
	path: Path

	def __init__(self, model: str="", path: Path=DEFAULT_DIR):
		self.model = model
		self.path = path

	@property
	def dir_name(self) -> str:
		return self.path.resolve().name

	@staticmethod
	def load_config(*, json_: Path=_ENV_JSON) -> "Config":
		if not os.path.exists(json_):
			return Config()
		with open(json_, "r") as f:
			data = json.load(f)
			return Config(**data)

	def save_config(self, *, dir: Path=_ENV_DIR, json_: Path=_ENV_JSON) -> None:
		os.makedirs(dir, exist_ok=True)
		with open(json_, "w") as f:
			json.dump({"model": self.model}, f, indent=2)

	def empty(self) -> None:
		self.model = ""
		self.path = DEFAULT_DIR

	def is_model_empty(self) -> bool:
		return self.model.strip() == ""
