"""Main copy functional"""

import os
import logging
import itertools
import asyncio
import hashlib
from aiopath import AsyncPath
from aioshutil import copyfile
from tqdm import tqdm
from file_manager.error import handle_error


class FileCopyManager:
    """Copy file manager"""

    def __init__(self, root_path, dest_path):
        self.files = []
        self.folders = []
        self.extensions = []
        self.duplicates = {}
        self.duplicated_names = {}
        self.unknown_suffix = ".unknown_suffix"
        self.root = root_path
        self.dest = dest_path
        if not os.path.exists(self.dest):
            self.dest.mkdir(parents=True, exist_ok=False)

    def get_hash(self, file):
        """Checking file hash to allow duplicates name copy"""
        with open(file, "rb") as file_to_check:
            data = file_to_check.read()
            md5 = hashlib.md5(data).hexdigest()
        return md5

    @handle_error
    async def copy_file(self, file: AsyncPath):
        """Copy file from path to dest path"""
        do_copy, suffix = True, file.suffix or self.unknown_suffix
        new_path = AsyncPath(self.dest, suffix, file.name)
        if await new_path.exists():
            current_file_hash = self.get_hash(file)
            if current_file_hash == self.get_hash(new_path):
                logging.debug(
                    "File %s alredy copied to target directory %s", file.name, new_path
                )
                self.duplicates.setdefault(current_file_hash, []).append(file)
                do_copy = False
            else:
                new_name = current_file_hash + "__" + str(file.name)
                logging.debug("File: %s must be renamed to %s", file, new_name)
                new_path = AsyncPath(self.dest, suffix, new_name)
                self.duplicated_names.setdefault(file.name, []).append(file)

        if do_copy:
            logging.debug("Copy file %s to %s", file, new_path)
            await copyfile(file, new_path)

    @handle_error
    async def read_folder(self, apath: AsyncPath = None) -> None:
        """Read all files from target dir recursive"""
        folder = apath if apath else AsyncPath(self.root)
        self.folders.append(apath)
        async for aitem in folder.iterdir():
            if await aitem.is_dir():
                logging.debug("Its folder, add it to task %s", aitem)
                task = asyncio.create_task(self.read_folder(apath=aitem))
                await task
            else:
                logging.debug("Add to copy new file %s", aitem)
                self.add_to_copy(aitem)

    def add_to_copy(self, file: AsyncPath) -> None:
        """Add to copy files"""
        suffix = file.suffix if file.suffix else self.unknown_suffix
        if suffix not in self.extensions:
            self.extensions.append(suffix)
        self.files.append(file)

    @handle_error
    async def make_extension_folder(self, suffix):
        """Make copies for files and sort by extentios"""
        new_path = AsyncPath(self.dest, suffix)
        await new_path.mkdir(exist_ok=True, parents=True)

    @handle_error
    async def show_progress(self, tasks, description):
        """Show progress for runned task"""
        with tqdm(total=len(tasks), desc=description) as pbar:
            completed = set()
            while tasks:
                done, tasks = await asyncio.wait(
                    tasks, timeout=0.1, return_when=asyncio.FIRST_COMPLETED
                )
                for task in done:
                    if task not in completed:
                        completed.add(task)
                        pbar.update(1)
                await asyncio.sleep(0.1)

    async def loader(self, stop):
        """Animation for reading directories"""

        spinner = itertools.cycle(["|", "/", "-", "\\"])
        while not stop.is_set():
            print(f"\rScanning files {next(spinner)}", end="", flush=True)
            await asyncio.sleep(0.1)
        print("\rScanning folders completed  ! ✅")

    @handle_error
    async def process_copy(
        self,
    ):
        """Run copy file in async tasks"""
        tasks = [asyncio.create_task(self.copy_file(file)) for file in self.files]
        await self.show_progress(tasks, "📄 Copying files to new dir  🔁")

    @handle_error
    async def process_folder(
        self,
    ):
        """Run copy file in async tasks"""
        stop_event = asyncio.Event()
        loader_task = asyncio.create_task(self.loader(stop_event))
        await self.read_folder()
        stop_event.set()
        await loader_task

    async def process_extension(
        self,
    ):
        """Run copy file in async tasks"""
        tasks = [
            asyncio.create_task(self.make_extension_folder(folder))
            for folder in self.extensions
        ]
        await self.show_progress(tasks, "📂 Creating extensions dir .. ♻️")

    @handle_error
    async def process_all(
        self,
    ):
        """Process all task to copy files"""
        await self.process_folder()
        await self.process_extension()
        await self.process_copy()
        self.show_general_stat()

    def show_general_stat(
        self,
    ):
        """Show stat for files"""
        print("\rTotal different extensions  : 🧩", len(self.extensions))
        print("\rTotal duplicated file names : 📝", len(self.duplicated_names))
        print("\rTotal duplicates files ..   : 🔁", len(self.duplicates))
        print("\rTotal folders processed ..  : 📂", len(self.folders))
        print("\rFiles copied successfully ... ✅", len(self.files))
