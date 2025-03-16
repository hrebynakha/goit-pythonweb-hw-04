"""Home work 4"""

import argparse
import os
import sys
from pathlib import Path
import logging
import asyncio
from file_manager.manager import FileCopyProcessor

parser = argparse.ArgumentParser(
    description="""
    Copy files from src to dest directory and sort it by exstesions file.
    You can choose the varian how to copy files:
        --copy_type=in_scan(default) Files fill be copy when scan process is running
        --copy_type=after_scan Files will be copy after all src folders scans
"""
)
parser.add_argument(
    "--src", type=str, nargs="?", default="src", help="From path to copy files"
)
parser.add_argument(
    "--dest", type=str, nargs="?", default="dest", help="Destination path to copy files"
)
parser.add_argument(
    "--copy-type",
    type=str,
    nargs="?",
    default="in_scan",
    help="Way how to copy files..",
)
input_args = parser.parse_args()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.DEBUG,
    handlers=[logging.StreamHandler()],
)

logging.getLogger().setLevel(logging.INFO)


root, dest = Path(input_args.src), Path(input_args.dest)
if not os.path.exists(root):
    logging.error("Cannot find source path: %s", root)
    sys.exit(0)

copy_processor = FileCopyProcessor(root, dest)


async def main(processor):
    """Main function"""
    if input_args.copy_type == "in_scan":
        await processor.process_all_immediately()
    elif input_args.copy_type == "after_scan":
        await processor.process_all()


if __name__ == "__main__":
    logging.debug("Script started")
    try:
        asyncio.run(main(processor=copy_processor))
    except KeyboardInterrupt:
        copy_processor.set_end_time()
        copy_processor.show_general_stat()
    logging.debug("Script finished")
