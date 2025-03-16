"""Home work 4"""

import argparse
import os
from pathlib import Path
import logging
import asyncio

from file_manager.error import PathNotFound, handle_error
from file_manager.copier import FileCopyManager

parser = argparse.ArgumentParser(description="Copy files.")
parser.add_argument(
    "--src", type=str, nargs="?", default="src", help="From path to copy files"
)
parser.add_argument(
    "--dest", type=str, nargs="?", default="dest", help="Destination path to copy files"
)
input_args = parser.parse_args()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.DEBUG,
    handlers=[logging.StreamHandler()],
)

logging.getLogger().setLevel(logging.INFO)


@handle_error
async def main():
    """Main function"""
    root, dest = Path(input_args.src), Path(input_args.dest)
    if not os.path.exists(root):
        raise PathNotFound
    await FileCopyManager(root, dest).process_all()


if __name__ == "__main__":
    logging.debug("Script started")
    asyncio.run(main())
    logging.debug("Script finished")
