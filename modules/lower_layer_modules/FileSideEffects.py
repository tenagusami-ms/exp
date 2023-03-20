"""
FileSideEffectsモジュール: ファイルシステムに関する副作用
"""
from __future__ import annotations

import csv
import inspect
import io
import json
from json import JSONDecodeError
from pathlib import Path
from types import MappingProxyType
from typing import Union, Mapping, Any, Sequence, Iterable

from .Exceptions import DataWriteError, DataReadError

JSONWritable = Union[Mapping[str, Any], Sequence[Any], str, int, float]


def prepare_directory(
        output_directory: Path
) -> None:
    """
    ディレクトリ生成
    Args:
        output_directory(pathlib.Path): ディレクトリパス
    """
    if not output_directory.is_dir():
        try:
            output_directory.mkdir(parents=True, exist_ok=True)
        except (FileExistsError, OSError) as e:
            raise DataWriteError(e.args)


def read_json(json_file: Path, *, encoding="utf-8") -> Mapping[str, Any]:
    """
    JSONファイルを読み出す
    Args:
        json_file(pathlib.Path): JSONファイル
        encoding(str, optional): テキストエンコーディング (default: "utf-8")
    Returns:
        JSON辞書(Mapping[str, Any])
    Raises:
        DataReadError: JSONパース失敗
    """
    try:
        return MappingProxyType(json.loads(read_text_contents(json_file, encoding=encoding)))
    except JSONDecodeError as err:
        raise DataReadError(f"data readout of JSON file {json_file} failed."
                            f" (message: {err.args},"
                            f" {inspect.currentframe().f_code.co_name} in module {__name__})")


def write_json(
        json_writable: JSONWritable,
        json_file: Path,
        indent=2
) -> None:
    """
    辞書をJSONファイルに書き出す
    Args:
        json_writable(Mapping[str, Any]): 辞書
        json_file(pathlib.Path): JSONファイル
        indent(Optional[int], optional): 書き出し時に、行ごとの出力に整形するときのインデント。Noneなら改行なし。(default: 2)
    Raises:
        DataWriteError: データ読み出し失敗
    """
    if json_file.is_dir():
        raise DataWriteError(f"The specified path {json_file} is a directory so not writable."
                             f" ({inspect.currentframe().f_code.co_name} in module {__name__}")
    try:
        prepare_directory(json_file.parent)
        with open(json_file, mode="w", encoding="utf-8", newline="\n") as f:
            json.dump(json_writable, f, ensure_ascii=False, indent=indent)
    except (OSError, TypeError) as err:
        raise DataWriteError(f"data writing of JSON to {json_file} failed."
                             f" (message: {err.args},"
                             f" {inspect.currentframe().f_code.co_name} in module {__name__})")


def read_text_contents(file: Path, *, encoding="utf-8") -> str:
    """
    テキストファイルの内容の文字列
    Args:
        file(pathlib.Path): テキストファイル
        encoding(str, optional): 読み出しのエンコーディング
    Returns:
        文字列(str)
    Raises:
        DataReadError: データ読み出し失敗
    """
    if not file.is_file():
        raise DataReadError(f"The specified file {file} does not exist."
                            f" ({inspect.currentframe().f_code.co_name} in module {__name__}")
    try:
        with open(file, mode="r", encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError as err:
        raise DataReadError(f"The specified file {file} has an invalid character to read in {encoding} encoding"
                            f" (message: {err.args},"
                            f" {inspect.currentframe().f_code.co_name} in module {__name__})")


def write_text_contents2file(contents: str, file: Path, *, encoding="utf-8") -> None:
    """
    テキスト文字列をファイルに新規書き込み
    Args:
        contents(str): 書き込む文字列
        file(pathlib.Path): テキストファイル
        encoding(str, optional): 読み出しのエンコーディング
    Returns:
        文字列(str)
    Raises:
        DataWriteError: データ書き込み失敗
    """
    try:
        with open(file, mode="w", encoding=encoding, newline="\n") as f:
            f.write(contents)
    except UnicodeDecodeError as err:
        raise DataWriteError(f"Writing text contents failed because of existence of an invalid character."
                             f" (message: {err.args},"
                             f" {inspect.currentframe().f_code.co_name} in module {__name__})")


def parse_csv_contents(csv_contents_text: str) -> Sequence[Sequence[str]]:
    """
    CSV文字列をパース
    Args:
        csv_contents_text(str): CSV文字列
    Returns:
        CSV配列(Sequence[Sequence[str]])
    """
    with io.StringIO() as stream:
        stream.write(csv_contents_text)
        stream.seek(0)
        csv_reader: Iterable[Iterable[str]] = csv.reader(stream)
        return tuple(tuple(column.strip() for column in row) for row in csv_reader)


def relative_path2absolute(
        path: Path,
        relative_to=None
) -> Path:
    """
    もしパスが相対パスなら絶対パスにする。絶対パスならそのまま。

    Args:
        path(pathlib.Path): パス
        relative_to(p.Path, optional): 相対パスの起点。デフォルトは./

    Returns:
        絶対パスに変換したパス(pathlib.Path)
    """
    if relative_to is None:
        relative_to: Path = Path("..").resolve()
    if not path.is_absolute():
        return (relative_to / path).resolve()
    return Path(path)
