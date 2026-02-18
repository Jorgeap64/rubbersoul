from argparse import ArgumentParser 
from typing import Final

from rubbersoul.utils.logger import get_logger
from rubbersoul.utils.uitls import DEFAULT_DIR

"""
===============================================================================

	Main 

===============================================================================
"""

log = get_logger("app", console=False)

TITLE: Final[str] = "Rubber Soul" 

def _parse_args():
	parser = ArgumentParser(description=f"Start the {TITLE}")

	parser.add_argument(
		"-p", "--path",
		nargs="?",
		default=DEFAULT_DIR,
		help="Path to the project (default: current directory)"
	)

	return parser.parse_args()

def main():
	log.info("Starting application...")
	args = _parse_args()


if __name__ == "__main__":
	main()
