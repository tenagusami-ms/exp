#! /usr/bin/python3
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
import dataclasses
import os
from subprocess import call
import re
import pathlib as p
import sys
from functools import reduce
from typing import Optional

from docopt import docopt
from schema import Schema, SchemaError, Use, And


class Error(Exception):
    """
    The fundamental exception class
    """
    pass


class NotInspectableError(Error):
    """
    The Error when the path on a pure WSL2 filesystem is inspected.
    """
    pass


class UsageError(Error):
    """
    The error for usage of a function.
    """
    pass


@dataclasses.dataclass
class Options:
    """
    dataclass for arguments and options
    """
    path: p.Path


def read_options() -> Options:
    """
    read command line arguments and options

    Returns:
        option class(Options)

    Raises:
        NotInspectableError: the file or the directory does not exists.
    """
    args = docopt(__doc__)
    schema = Schema({
        "<path>": And(Use(get_path), lambda path: path.is_file() or path.is_dir(),
                      error=f"The specified path {args['<path>']}"
                            + " does not exist.\n")
    })
    try:
        args = schema.validate(args)
    except SchemaError as e:
        raise NotInspectableError(e.args[0])
    return Options(args["<path>"])


def wsl2_full_path2windows_path(wsl2_path: p.Path) -> p.PureWindowsPath:
    """
    convert a wsl2 path (posix path) to the corresponding windows path.
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
                         + f"(function {wsl2_full_path2windows_path.__name__} "
                         + f"in module {__name__}).\n")
    return reduce(lambda reduced, name: reduced.joinpath(name), p.Path(path).parts,
                  p.PureWindowsPath(rf"{drive}:\\"))


def is_wsl2_path(path: p.PurePath) -> bool:
    """
    Whether the given path is a correct WSL2 path.
    Args:
        path(pathlib.Path): a path

    Returns:
        True if correct.
    """
    return re.match(r"^/mnt/[a-z]/", path.as_posix()) is not None


def get_path(path_str: Optional[str]) -> p.Path:
    """
    Convert the WSL2 path specified as the command line argument to a pathlib.Path object.
    If nothing is specified, the current directory is used.
    Args:
        path_str(str): the command line argument

    Returns:
        path object(pathlib.Path)
    """
    if path_str is None or len(path_str) == 0:
        return p.Path(".").resolve()
    return p.Path(path_str).resolve()


def open_on_windows(explorer: p.Path, path: p.Path) -> None:
    """
    open path on Windows with explorer.exe

    Args:
        explorer(pathlib.Path): the path to the windows explorer.
        path(pathlib.Path): the specified path.

    Raises:
        NotInspectableError: the specified path is not inspectable from Windows system.
    """
    if is_wsl2_path(path):
        windows_path = wsl2_full_path2windows_path(path)
        call([explorer, windows_path])
        return
    raise NotInspectableError(
        f"The specified path {path.as_posix()} is not in the windows filesystem "
        + f"(function {open_on_windows.__name__} "
        + f"in module {__name__}).\n")


def main() -> None:
    """
    The main procedure
    """
    if os.name == "nt":
        print(f"This tool {__file__} is usable only on WSL2.\n")
        sys.exit(1)
    try:
        options: Options = read_options()
        explorer: p.Path = p.Path(r"/mnt") / "c" / "Windows" / "explorer.exe"
        open_on_windows(explorer, options.path)
    except(UsageError, NotInspectableError) as e:
        sys.stderr.write(e.args[0])
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    main()
    sys.exit(0)
