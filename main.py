"""Home work 4"""
import argparse
import os
from pathlib import Path
import shutil
import hashlib
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.DEBUG,
    handlers=[logging.StreamHandler()],
)

parser = argparse.ArgumentParser(description='Copy files.')
parser.add_argument('--src', type=str, nargs='?', default='src',
                    help='From path to copy files')
parser.add_argument('--dest',  type=str, nargs='?', default='dest',
                    help='Destination path to copy files')
args = parser.parse_args()

class PathNotFound(Exception):
    """Not found path in os"""


def handle_error(func):
    """Decorator function to handle errors"""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PathNotFound:
            logging.error("Path not found.")
        except PermissionError:
            logging.error("Permission denied for this folder.")
        # except TypeError:
        #     logging.error("Opps...Some type not correct...")
        # except Exception: # disable it to show error
            # logging.error("Opps...Some error happend...")
    return inner


class FileCopy:
    def __init__(self, root_path, dest_path ):
        self.root = root_path
        self.dest = dest_path
        if not os.path.exists(self.dest):
            self.dest.mkdir(parents=True, exist_ok=False)

    def check_hash(file):
        """Checking file hash to allow duplicates name copy"""
        with open(file, 'rb') as file_to_check:
            data = file_to_check.read()
            md5 = hashlib.md5(data).hexdigest()
        return md5

    @handle_error
    def copy_file(self, file):
        """Copy file from path to dest path"""
        pass


    @handle_error
    def read_folder(self, ):
        """Make copies for files and sort by extentios"""
        pass

    @handle_error
    def make_copy(self, ):
        """Make copies for files and sort by extentios"""
        pass
    

@handle_error
def main():
    """Main function"""
    root, dest = Path(args.src), Path(args.dest)
    if not os.path.exists(root):
        raise PathNotFound

    FileCopy(root, dest).read_folder().make_copy()

if __name__ == "__main__":
    main()