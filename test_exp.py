"""
unit test of exp.py
"""
import os
import pathlib as p

import pytest

from exp import is_wsl2_path, wsl2_full_path2windows_path, UsageError


def test_is_wsl2_path():
    assert is_wsl2_path(p.Path("/mnt/c/home"))
    assert not is_wsl2_path(p.Path("/home/ykanya"))
    assert not is_wsl2_path(p.Path(""))
    if os.name != "nt":
        assert not is_wsl2_path(p.PureWindowsPath(r"C:\\home"))


def test_wsl2_full_path2windows_path():
    assert wsl2_full_path2windows_path(p.Path("/mnt") / "c" / "home" / "ykanya") \
           == p.PureWindowsPath(r"C:\\") / "home" / "ykanya"
    assert wsl2_full_path2windows_path(p.Path("/mnt") / "z" / "lib") \
           == p.PureWindowsPath(r"z:\\") / "lib"
    assert wsl2_full_path2windows_path((p.Path("/mnt") / "c")) \
           == p.PureWindowsPath(r"C:\\")
    with pytest.raises(UsageError):
        wsl2_full_path2windows_path((p.Path("/mt") / "c"))
