import sys
import itertools
import asyncio

from dataclasses import dataclass

from rubbersoul.config.config import Config
from rubbersoul.core.session import Session

"""
===============================================================================

    CLI: Interface for terminal

===============================================================================
"""

@dataclass(slots=True)
class CLI:
    _config: Config
    _session: Session

    def __init__(self, _config: Config):
        self._config = _config
        self._session = Session(self._config)

    async def start(self):
        try:
            result = await self._session.ask()
            print(result)
        except Exception as e:
            print(f"[error] {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            await self._session.close_session()

