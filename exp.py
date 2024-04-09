#! /usr/bin/env python
"""Overview:
    exp.py : open a directory or a file looked from WSL2 with Windows Explorer
             if it is in the Windows filesystem.
             If no path is specified, current directory is opened.
Usage:
    exp.py [<path>]

    exp.py -h | --help

Options:
    -h --help                Show this screen and exit.
"""
from __future__ import annotations

import os
import re
import sys
from functools import reduce
from pathlib import Path, PureWindowsPath, PurePath
from subprocess import run

from modules.lower_layer_modules.FileSideEffects import relative_path2absolute


def main() -> None:
    """
    The main procedure
    """
    if os.name == "nt":
        print(f"This tool {__file__} is usable only on WSL2.\n")
        sys.exit(1)
    try:
        current_directory: Path = Path(".").resolve()
        to_open: Path = relative_path2absolute(Path(sys.argv[1]).expanduser(), relative_to=current_directory)
        explorer: Path = Path(r"/mnt") / "c" / "Windows" / "explorer.exe"
        open_on_windows(explorer, to_open)
    except Error as e:
        sys.stderr.write(e.args[0])
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


class Error(Exception):
    """
    The fundamental exception class
    """
    pass


class UsageError(Error):
    """
    The error for usage of a function.
    """
    pass


def wsl2_full_path2windows_path(wsl2_path: Path) -> PureWindowsPath:
    """
    convert a wsl2 path (posix path) to the corresponding windows' path.
    Args:
        wsl2_path(pathlib.Path):  wsl2 path

    Returns:
        windows path(pathlib.Path)

    Raises:
        UsageError: wsl2_path is not correct WSL2 path.
    """
    try:
        [(drive, path)] = re.findall(r"^/mnt/([a-z])(/?.*)", wsl2_path.as_posix())
    except ValueError:
        raise UsageError(f"The input path {wsl2_path.as_posix()} is not a correct WSL2 path "
                         f"(function {wsl2_full_path2windows_path.__name__} "
                         f"in module {__name__}).\n")
    return reduce(lambda reduced, name: reduced.joinpath(name), Path(path).parts,
                  PureWindowsPath(rf"{drive}:\\"))


def is_wsl2_path(path: PurePath) -> bool:
    """
    Whether the given path is a correct WSL2 path.
    Args:
        path(pathlib.Path): a path

    Returns:
        True if correct.
    """
    return path.as_posix().startswith(r"/mnt/")


def open_on_windows(explorer: Path, path: Path) -> None:
    """
    open path on Windows with explorer.exe

    Args:
        explorer(pathlib.Path): the path to the Windows explorer.
        path(pathlib.Path): the specified path.

    Raises:
        NotInspectableError: the specified path is not inspectable from Windows system.
    """
    if is_wsl2_path(path):
        windows_path: PureWindowsPath = wsl2_full_path2windows_path(path)
        run([explorer, windows_path])
        return
    wsl_windows_path: PureWindowsPath = PureWindowsPath("\\wsl$") / "Ubuntu-20.04"
    run([explorer, wsl_windows_path / path])
    return


if __name__ == '__main__':
    main()
    sys.exit(0)
