#!/usr/bin/python

import sys
import hashlib
import shutil
import logging
import os
from datetime import datetime
from pathlib import Path

def main():
    timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    logdir = Path(os.environ.get('LOGDIR', 'logs'))
    source, target = parse_args(sys.argv)

    if not logdir.exists():
        logdir.mkdir()
    logging.basicConfig(
        filename=logdir/f'example_{timestamp}.log', 
        format='%(levelname)s:%(message)s',
        encoding='utf-8', level=logging.DEBUG)
    
    target_anal = eval_target(Path(target))

    for file in source.iterdir():
        if eval_source_file(file, target_anal) == True:
            cut_paste(file, target)
        else:
            continue


def parse_args(args: list[str]) -> tuple[Path, Path]:
    if len(args) != 3:
        logging.error("Must have exactly 2 arguments")
        raise IndexError("Must have exactly 2 arguments")

    source = Path(args[1])
    target = Path(args[2])

    if not source.exists():
        logging.error("Source folder does not exist")
        raise FileNotFoundError("Source folder does not exist")

    if not target.exists():
        logging.error("Target folder does not exist")
        raise FileNotFoundError("Target folder does not exist")

    return (source, target)

def eval_target(targetdir: Path) -> tuple[list[str], list[str]]:
    targetnames = [
        file.name 
        for file in targetdir.iterdir() 
        if file.is_file()
    ]    

    targethashes = [
        buffer_hash(file) 
        for file in targetdir.iterdir()
        if file.is_file()
    ]

    return (targetnames, targethashes)

def eval_source_file(sourcepath: Path, target_anal: tuple[list, list]) -> bool:
    targetnames, targethashes = target_anal

    if sourcepath.name in targetnames:
        logging.warning(f"no transfer: {sourcepath.name}, file of same name already in target")
        return False
    
    sourcehash = buffer_hash(sourcepath)

    if sourcehash in targethashes:
        logging.warning(f"no transfer: {sourcepath.name}, file with same checksum already in target")
        return False
    
    return True

def buffer_hash(filepath: Path) -> str:
    hash = hashlib.sha256()
    with open(filepath, "rb") as file:
        while True:
            data = file.read(65536)
            if not data:
                break
            hash.update(data)
    
    return hash.hexdigest()

def cut_paste(file: Path, target: Path) -> None:
    try:
        shutil.copy2(file, target)
    except:
        logging.warning(f"no transfer:{file.name}:copy file failed")    
    else:
        file.unlink()
        logging.info(f'success: {file.name} transfered')

if __name__ == "__main__":
    main()
