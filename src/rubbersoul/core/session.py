import logging

from enum import Enum
from dataclasses import dataclass
from typing import AsyncGenerator, Final

from ollama import list as models_list, AsyncClient

from rubbersoul.core.git_ops import get_git_diff
from rubbersoul.utils.utils import is_ollama_running
from rubbersoul.config.config import Config

"""
===============================================================================

    Session: Smart conversation manager with context handling.

===============================================================================
"""

log = logging.getLogger(__name__)

_KEEP_ALIVE: Final[str] = "5m"
_TEMPERATURE: Final[float] = 0.2
_TOP_P: Final[int] = 40
_TOP_K: Final[float] = 0.9
_REPEAT_PENALTY: Final[float] = 1.3
_DIFF_PROMPT: str = """
You are a senior software engineer.

Write a professional git commit message using Conventional Commits.

Rules:
- First line: <type>: <short summary>
- Use imperative mood
- Keep summary under 72 characters
- If helpful, add bullet points

Diff:
{diff}
"""

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
        git_diff = get_git_diff() 
        if git_diff:
            log.info(f"The files: \n{git_diff}\n...")
        return _DIFF_PROMPT.format(diff=git_diff)

    async def ask_stream(self) -> AsyncGenerator[str, None]:
        prompt = self._git_diff_prompt()
        message = {
            "role": Roles.SYSTEM, "content": prompt 
        }		

        final_content = ""
        stream = await self.client.chat(
                model=self._config.model,
                messages=message,
                stream=True,
                options={
                    "temperature": _TEMPERATURE,
                    "top_p": _TOP_P,
                    "top_k": _TOP_K,
                    "repeat_penalty": _REPEAT_PENALTY
                    },
                keep_alive=_KEEP_ALIVE
                )

        async for partial in stream:
            chunk = partial["message"]["content"]
            final_content += chunk
            yield chunk
        log.info(f"Response complete...")

    async def close_session(self) -> None:
        await self.client.chat(
                model=self._config.model,
                messages=[],
                stream=False,
                keep_alive="0s"
                )
        del self.client
        log.warning("Session closed...")
