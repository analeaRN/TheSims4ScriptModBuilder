"""
This script uses decompyle3 to de-compile the game binaries

TODO 
- use config.ini to inform program which decompiler to use
- do not require both de-compilers, only one in constants.py
- combine two de-compiler files together (if possible)
"""
import fnmatch
import multiprocessing
import os
import shutil
import string
import threading
from pathlib import Path
from subprocess import run
import subprocess
from zipfile import PyZipFile
from utils.constants import *
from utils.utils import create_directory, prepare_directory
from multiprocessing import Pool
from decompile import prepare, copy_zip, unzip


def decompile_worker(args):
    dest_path, src_file, *_ = (arg.absolute() for arg in args)
    
    rv = run(
        rf"{decompyle3} {src_file} --output {dest_path}",
        text=True,
        capture_output=True)

    print("Done %s" % src_file)
    return [rv.returncode, rv.stderr]


def decompile(src: string):
    print('start decompiling ' + src)

    # total = 0
    # success = 0
    todo = []

    for root, _, files in os.walk(src):
        # print('.', end='') if success % 30 or success == 0 else print('.')  # next line
        # total += 1
        
        root_path = Path(root)
        desc_path = Path(project_game_decompile_dir) / \
            root_path.relative_to(project_game_unzip_dir)

        if not desc_path.exists():
            create_directory(desc_path)

        for filename in fnmatch.filter(files, "*.pyc"):
            src_file_path = root_path / filename
            todo.append([desc_path, src_file_path])

    with Pool(num_decompilers) as pool:
        rv = pool.map(decompile_worker, todo)

    total = len(todo)
    success = sum([1 for x in rv if x[0] == 0 and not x[1]])

    print('success rate: ' + str(round((success * 100) / total, 2)) + '%')


def run_decompile():
    for folder in [project_game_unzip_dir + '/' + x for x in os.listdir(project_game_unzip_dir)]:
        decompile(folder)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    prepare()
    run_decompile()
