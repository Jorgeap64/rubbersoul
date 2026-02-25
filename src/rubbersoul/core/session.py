import logging

from enum import Enum
from dataclasses import dataclass
from typing import AsyncGenerator, Final

from ollama import list as models_list, AsyncClient

from rubbersoul.core.git_ops import get_git_diff
from rubbersoul.utils.utils import is_ollama_running, SKILLS_DIR
from rubbersoul.config.config import Config

"""
===============================================================================

    Session: Smart conversation manager with context handling.

===============================================================================
"""

log = logging.getLogger(__name__)

_KEEP_ALIVE: Final[str] = "5m"
_TEMPERATURE: Final[float] = 0.0
_TOP_K: Final[int] = 10
_TOP_P: Final[float] = 0.2
_REPEAT_PENALTY: Final[float] = 1.1
_NUM_PREDICT: Final[int] = 300
_SEED: Final[int] = 42
_SYSTEM_PROMPT: Final[str] = (
    "You are a precise execution engine. "
    "Follow instructions exactly as given. "
    "Do not add, interpret, or embellish anything. "
    "Do not explain your reasoning. "
    "Do not offer alternatives or suggestions. "
    "Output only what is explicitly requested. "
    "If something is unclear, do the most literal interpretation possible."
)

class Roles(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass(slots=True)
class Session:
    client: AsyncClient
    _config: Config

    def __init__(self, _config: Config):
        if not is_ollama_running():
            log.error("Ollama is not running...")
            raise RuntimeError("Ollama is not running.")

        self._config = _config
        self._validate_model(self._config.model)
        self.client = AsyncClient()

        log.info(f"Session started for project: {self._config.dir_name}...")

    @staticmethod
    def get_models() -> list[str]:
        if not is_ollama_running():
            log.error("Ollama is not running...")
            raise RuntimeError("Ollama is not running.")
        return [m.model for m in models_list().models]  # type: ignore

    def _validate_model(self, model: str) -> None:
        available = Session.get_models()
        if model not in available:
            log.error(f"Model '{model}' not found. Available models: {available}...")
            raise ValueError(f"Model '{model}' not found. Available models: {available}...")

    def _git_diff_prompt(self) -> str:
        with open(SKILLS_DIR) as f:
            skill = f.read()
        diff = get_git_diff()
        prompt = f"""{skill}
        Now generate a commit message for this diff. Output ONLY the message:
        {diff}"""
        log.info(f"Prompt: {prompt}...")
        return prompt

    async def ask(self) -> str:
        prompt = self._git_diff_prompt()
        messages = [
                { "role": Roles.SYSTEM, "content": _SYSTEM_PROMPT },
                { "role": Roles.USER, "content": prompt }
                ]

        response = await self.client.chat(
                model=self._config.model,
                messages=messages,
                stream=False,
                options={
                    "temperature": _TEMPERATURE,
                    "top_p": _TOP_P,
                    "top_k": _TOP_K,
                    "repeat_penalty": _REPEAT_PENALTY,
                    "num_predict": _NUM_PREDICT,
                    "seed": _SEED,
                    },
                keep_alive=_KEEP_ALIVE
                )
        msg = response["message"]
        result = (msg.get("content") or msg.get("thinking") or "").strip()
        log.info(f"Response complete...")
        return result
   
    async def close_session(self) -> None:
        await self.client.chat(
                model=self._config.model,
                messages=[],
                stream=False,
                keep_alive="0s"
                )
        del self.client
        log.warning("Session closed...")
