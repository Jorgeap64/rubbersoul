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
_TEMPERATURE: Final[float] = 0.1
_TOP_K: Final[int] = 20
_TOP_P: Final[float] = 0.5
_REPEAT_PENALTY: Final[float] = 1.3
_NUM_PREDICT: Final[int] = 150
_SYSTEM_PROMPT: str = "You are a commit message generator. You output ONLY the commit message. No reasoning. No explanation. No alternatives. Just the message."
_DIFF_PROMPT: str = """Generate a git commit message for this diff.

RULES:
- Output ONLY the commit message, nothing else
- Format: <type>(<scope>): <summary>
- Types: feat, fix, docs, refactor, chore, ci, build, test, style, perf
- Summary: imperative, lowercase, under 72 chars
- Optional body: blank line, then bullet points

EXAMPLE OUTPUT:
feat(cli): add async session manager

- introduce AsyncClient for streaming responses
- add model validation on startup

FORBIDDEN:
- Do not explain your reasoning
- Do not list alternatives  
- Do not say "here is the commit message"
- Do not use markdown code blocks

DIFF:
{diff}"""

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
        message = [
                { "role": Roles.SYSTEM, "content": _SYSTEM_PROMPT },
                { "role": Roles.USER, "content": prompt }
                ]		

        final_content = ""
        stream = await self.client.chat(
                model=self._config.model,
                messages=message,
                stream=True,
                options={
                    "temperature": _TEMPERATURE,
                    "top_p": _TOP_P,
                    "top_k": _TOP_K,
                    "repeat_penalty": _REPEAT_PENALTY,
                    "num_predict": _NUM_PREDICT,
                    "think": False
                    },
                keep_alive=_KEEP_ALIVE
                )

        async for partial in stream:
            message = partial["message"]
            chunk = message.get("content") or message.get("thinking")
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
