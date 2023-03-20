"""
Exceptions module: basic errors
"""
from __future__ import annotations


class Error(Exception):
    """
    パッケージ内例外の基本クラス
    """
    pass


class DataWriteError(Error):
    """
    データ読み出し失敗の例外
    """
    pass


class DataReadError(Error):
    """
    データ書き込み失敗の例外
    """
    pass


class ImageAnalysisError(Error):
    """
    画像解析失敗の例外
    """
    pass


class NoNewDataException(Error):
    """
    新規データがない例外
    """
    pass


class InsertError(Error):
    """
    DB書き込みエラー
    """
    pass


class DBError(Error):
    """
    DBオペレーションでのエラー
    """
    pass


class UsageError(Error):
    """
    関数の使用法が間違っているバグのエラー
    """
    pass


class ProcessError(Error):
    """
    外部プロセス実行失敗のエラー
    """
    pass


class ConsistencyError(Error):
    """
    データの一貫性についてのエラー。例えばあるはずのない値の組み合わせが現れた、など。
    """
    pass


class MultipleUseError(Error):
    """
    複数の同一プロセスを起動したエラー
    """
    pass


class Interruption(Error):
    """
    キーボード入力での中断のエラー
    """
    pass
