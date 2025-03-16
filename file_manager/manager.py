"""Main copy functional"""

import os
import time
import logging
import itertools
import asyncio
import hashlib
from aiopath import AsyncPath
from aioshutil import copyfile
from tqdm import tqdm
from file_manager.error import handle_error


class FileProgressBar:
    """Progress bar method for file manager"""

    def __init__(self):
        pass

    @handle_error
    async def show_progress(self, tasks, description) -> None:
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

    async def loader(self, stop, message="Scanning folders...") -> None:
        """Animation for reading directories"""

        spinner = itertools.cycle(["|", "/", "-", "\\"])
        while not stop.is_set():
            print(f"\r{message} {next(spinner)}", end="", flush=True)
            await asyncio.sleep(0.1)
        print(f"\r{message} completed  ! ✅")


class FileManagerInfo:
    """File manager basic information"""

    def __init__(self):
        self.start_time = time.perf_counter()
        self.elapsed_time = time.perf_counter() - self.start_time
        self.files = []
        self.copied_files = []
        self.folders = []
        self.extensions = []
        self.duplicates = {}
        self.duplicated_names = {}

    def set_end_time(
        self,
    ) -> None:
        """Add to copy files"""
        self.elapsed_time = time.perf_counter() - self.start_time

    def show_general_stat(
        self,
    ) -> None:
        """Show stat for files"""
        print(f"\rTotal elapsed time .......  : ⏱️  {self.elapsed_time:.2f}")
        print("\rTotal different extensions  : 🧩", len(self.extensions))
        print("\rTotal duplicated file names : 📝", len(self.duplicated_names))
        print("\rTotal duplicates files ..   : 🔁", len(self.duplicates))
        print("\rTotal folders processed ..  : 📂", len(self.folders))
        print("\rTotal files found  .......  : 📝", len(self.files))
        print("\rTotal copied files .......  : ✅", len(self.copied_files))

    def add_duplicates(self, file_hash: str, file: AsyncPath) -> None:
        """Add to duplicates files"""
        self.duplicates.setdefault(file_hash, []).append(file)

    def add_duplicated_names(self, file: AsyncPath) -> None:
        """Add to duplicated name of files"""
        self.duplicated_names.setdefault(file.name, []).append(file)


class FileCopyManager(FileManagerInfo, FileProgressBar):
    """Copy file manager"""

    def __init__(self, root_path, dest_path):
        self.unknown_suffix = ".unknown_suffix"
        self.root = root_path
        self.dest = dest_path
        if not os.path.exists(self.dest):
            self.dest.mkdir(parents=True, exist_ok=False)
        super().__init__()

    def get_hash(self, file):
        """Checking file hash to allow duplicates name copy"""
        with open(file, "rb") as file_to_check:
            data = file_to_check.read()
            md5 = hashlib.md5(data).hexdigest()
        return md5

    @handle_error
    async def copy_file(self, file: AsyncPath, make_exstesion=False):
        """Copy file from path to dest path"""
        do_copy, suffix = True, file.suffix or self.unknown_suffix
        if make_exstesion and not await AsyncPath(self.dest, suffix).exists():
            await self.make_extension_folder(suffix)

        new_path = AsyncPath(self.dest, suffix, file.name)
        if await new_path.exists():
            current_file_hash = self.get_hash(file)
            if current_file_hash == self.get_hash(new_path):
                logging.debug(
                    "File %s alredy copied to target directory %s", file.name, new_path
                )
                self.add_duplicates(current_file_hash, file)
                do_copy = False
            else:
                new_name = current_file_hash + "__" + str(file.name)
                logging.debug("File: %s must be renamed to %s", file, new_name)
                new_path = AsyncPath(self.dest, suffix, new_name)
                self.add_duplicated_names(file)

        if do_copy:
            logging.debug("Copy file %s to %s", file, new_path)
            await copyfile(file, new_path)
            self.copied_files.append(new_path)

    @handle_error
    async def scan_folder(self, apath: AsyncPath = None) -> None:
        """Read all files from target dir recursive"""
        folder = apath if apath else AsyncPath(self.root)
        self.folders.append(apath)
        async for aitem in folder.iterdir():
            if await aitem.is_dir():
                logging.debug("Its folder, add it to task %s", aitem)
                await asyncio.create_task(self.scan_folder(apath=aitem))
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
    async def make_extension_folder(self, suffix) -> None:
        """Make copies for files and sort by extentios"""
        new_path = AsyncPath(self.dest, suffix)
        await new_path.mkdir(exist_ok=True, parents=True)

    @handle_error
    async def read_folder(self, apath: AsyncPath = None) -> None:
        """Read all files from target dir recursive and run copy task"""
        folder = apath if apath else AsyncPath(self.root)
        self.folders.append(apath)
        tasks = []
        async for aitem in folder.iterdir():
            if await aitem.is_dir():
                logging.debug("Its folder, add it to task %s", aitem)
                tasks.append(asyncio.create_task(self.read_folder(apath=aitem)))
            else:
                self.add_to_copy(aitem)
                logging.debug("Add to copy new file %s", aitem)
                tasks.append(
                    asyncio.create_task(self.copy_file(file=aitem, make_exstesion=True))
                )

        if tasks:
            await asyncio.gather(*tasks)


class FileCopyProcessor(FileCopyManager):
    """File copy process class"""

    @handle_error
    async def process_copy(
        self,
    ) -> None:
        """Run copy file in async tasks"""
        tasks = [asyncio.create_task(self.copy_file(file)) for file in self.files]
        await self.show_progress(tasks, "📄 Copying files to new dir  🔁")

    @handle_error
    async def process_folder(
        self,
    ) -> None:
        """Process folders in async tasks"""
        stop_event = asyncio.Event()
        loader_task = asyncio.create_task(self.loader(stop_event))
        await self.scan_folder()
        stop_event.set()
        await loader_task

    async def process_extension(
        self,
    ) -> None:
        """Create extesion folders in async tasks"""
        tasks = [
            asyncio.create_task(self.make_extension_folder(folder))
            for folder in self.extensions
        ]
        await self.show_progress(tasks, "📂 Creating extensions dir .. 🧩")

    @handle_error
    async def process_all(
        self,
    ) -> None:
        """Process all task to copy files"""
        await self.process_folder()
        await self.process_extension()
        await self.process_copy()
        self.set_end_time()
        self.show_general_stat()

    @handle_error
    async def process_all_immediately(
        self,
    ) -> None:
        """Process scan and copy immediately"""
        stop_event = asyncio.Event()
        loader_task = asyncio.create_task(self.loader(stop_event, "Processing folders"))
        await self.read_folder()
        stop_event.set()
        await loader_task
        self.set_end_time()
        self.show_general_stat()
