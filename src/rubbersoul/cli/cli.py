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

async def spinner_task(msg: str = "Thinking") -> None:
    frames = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    try:
        while True:
            print(f"\r{next(frames)} {msg}...", end="", flush=True)
            await asyncio.sleep(0.08)
    except asyncio.CancelledError:
        print("\r" + " " * (len(msg) + 6) + "\r", end="", flush=True)

@dataclass(slots=True)
class CLI:
    _config: Config
    _session: Session

    def __init__(self, _config: Config):
        self._config = _config
        self._session = Session(self._config)

    async def start(self):
        spin = asyncio.create_task(spinner_task())
        first_chunk = True
        try:
            async for chunk in self._session.ask_stream():
                if first_chunk:
                    spin.cancel()
                    await asyncio.sleep(0)  # let cancellation flush
                    first_chunk = False
                print(chunk, end="", flush=True)
        except Exception as e:
            spin.cancel()
            print(f"[error] {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            if not spin.cancelled():
                spin.cancel()
            await self._session.close_session()

