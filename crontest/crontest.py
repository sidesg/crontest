#!/usr/bin/python

import sys
import hashlib
import shutil
import logging
import os
from datetime import datetime
from pathlib import Path
from collections import Counter

def main():
    timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    logdir = Path(os.environ.get('LOGDIR', 'logs'))
    sourcedir, targetdir = parse_args(sys.argv)

    if not logdir.exists():
        logdir.mkdir()
    logging.basicConfig(
        filename=logdir/f'example_{timestamp}.log', 
        format='%(levelname)s:%(message)s',
        encoding='utf-8', level=logging.DEBUG)
    
    source_whitelist = eval_sourcedir(sourcedir)
    
    target_anal = eval_targetdir(Path(targetdir))

    for file in source_whitelist:
        if eval_source_file(file, target_anal) == True:
            cut_paste(file, targetdir)
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

def eval_sourcedir(sourcedir: Path) -> list[Path]:
    doubles = list()
    hashlist = [
        (file, buffer_hash(file))
        for file in sourcedir.iterdir()
        if file.is_file()
    ]
    
    for i, file in enumerate(hashlist):
        if file[0] not in doubles:
            for comparison in hashlist[i+1:]:
                if file[1] == comparison[1]:
                    doubles.append(file[0])
                    doubles.append(comparison[0])

                    logging.warning(f"Files skipped: {file[0].name}, {comparison[0].name} duplicate hashes")

    doubles = list(set(doubles))

    whitelist = [
        tup[0]
        for tup in hashlist
        if not tup[0] in doubles
    ]

    return whitelist

def eval_targetdir(targetdir: Path) -> tuple[list[str], list[str]]:
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
