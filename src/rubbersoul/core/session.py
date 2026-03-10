import logging

from enum import Enum
from dataclasses import dataclass
from typing import AsyncGenerator, Final

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from ollama import list as models_list 

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
    "Output only what is explicitly requested. "
    "Do not explain your reasoning or offer alternatives."
)

@dataclass(slots=True)
class Session:
    _llm: ChatOllama
    _config: Config

    def __init__(self, _config: Config):
        if not is_ollama_running():
            log.error("Ollama is not running...")
            raise RuntimeError("Ollama is not running.")

        self._config = _config
        self._validate_model(self._config.model)
        self._llm = ChatOllama(
            model=self._config.model,
            temperature=_TEMPERATURE,        # determinism
            top_k=_TOP_K,
            top_p=_TOP_P,
            repeat_penalty=_REPEAT_PENALTY,
            num_predict=_NUM_PREDICT,
            seed=_SEED,
            keep_alive=_KEEP_ALIVE,
        )

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
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        response = await self._llm.ainvoke(messages)
        result = (response.content or "")
        log.info(f"Response complete...")
        return result
   
    async def close_session(self) -> None:
        self._llm.keep_alive = "0s"
        await self._llm.ainvoke([
            HumanMessage(content="")
        ])
        del self._llm
        log.warning("Session closed...")
