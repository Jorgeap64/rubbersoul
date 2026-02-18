import asyncio

from argparse import ArgumentParser, Namespace
from typing import Final

from rubbersoul.cli.cli import CLI
from rubbersoul.config.config import Config
from rubbersoul.utils.logger import get_logger
from rubbersoul.utils.utils import DEFAULT_DIR

"""
===============================================================================

    Main 

===============================================================================
"""

log = get_logger("app", console=False)

TITLE: Final[str] = "Rubber Soul" 

def _get_config(args: Namespace) -> Config:
    config = Config.load_config()

    if args.reset:
        config.empty()
        log.info("Config reset...")
    if args.model:
        config.model = args.model
        log.info(f"Model set to: {args.model}...")
    if args.path:
        config.path = args.path
        log.info(f"Path set to: {args.path}...")

    config.save_config()
    return config

def _parse_args():
    parser = ArgumentParser(description=f"Start the {TITLE}")

    parser.add_argument(
            "-p", "--path",
            nargs="?",
            default=DEFAULT_DIR,
            help="Path to the project (default: current directory)"
            )

    parser.add_argument(
            "-m", "--model",
            help="Model to use (overrides saved default and updates config)"
            )

    parser.add_argument(
            "-r", "--reset",
            action="store_true",
            help="Reset configs that where saved"
            )

    return parser.parse_args()

async def setup():
    log.info("Starting application...")
    args = _parse_args() 
    config = _get_config(args)

    cli = CLI(config)
    try:
        await cli.start()
    except Exception as e:
        log.error(f"Died: {e}...")

def main():
    try:
        asyncio.run(setup())
    except KeyboardInterrupt:
        print("\n[Interrupted]")

if __name__ == "__main__":
    main()
