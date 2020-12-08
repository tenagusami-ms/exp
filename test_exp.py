import os

import pytest

from exp import is_wsl2_path, wsl2_full_path2windows_path, UsageError, get_path, NotInspectableError, open_on_windows, \
    Options
import pathlib as p


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


def test_get_path():
    assert get_path("") == p.Path(".").resolve()
    assert get_path(None) == p.Path(".").resolve()
    if os.name != "nt":
        assert get_path("/home/ykanya") == p.Path("/home/ykanya").resolve()
        assert get_path("/home/ykanya/tmp") == p.Path("/mnt/z/tmp")


def test_open_on_windows():
    if os.name != "nt":
        with pytest.raises(NotInspectableError):
            open_on_windows(p.Path(r"/mnt") / "c" / "Windows" / "explorer.exe", p.Path("/home/ykanya"))


class TestOptions:
    def test_options(self):
        assert Options(p.Path("/home/ykanya")).path == p.Path("/home/ykanya")
