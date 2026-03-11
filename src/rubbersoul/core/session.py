import logging

from dataclasses import dataclass
from typing import Final

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from ollama import list as models_list

from rubbersoul.utils.utils import is_ollama_running
from rubbersoul.config.config import Config
from rubbersoul.core.commit_generator import get_commit 

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


    def ask(self) -> str:
        response = get_commit(self._llm)
        result = (response or "")
        log.info(f"Response complete...")
        return result

    def close_session(self) -> None:
        try:
            self._llm.keep_alive = "0m" 
            self._llm.invoke([
                HumanMessage(content="")
            ])
            log.warning("Model unloaded from Ollama...")
        except Exception as e:
            log.error(f"Failed to unload model: {e}...")
        finally:
            del self._llm
            log.warning("Session closed...")
