"""
NeoDict - 自動更新型日本語新語辞書ライブラリ

NEologdの後継として、ウェブから自動的に新語や固有表現を収集・更新する
次世代日本語辞書システム
"""

__version__ = "0.1.1"
__author__ = "NeoDict Contributors"
__license__ = "MIT"

from .core import NeoDict, Word, WordEntry
from .updater import DictUpdater, UpdateScheduler

__all__ = [
    "NeoDict",
    "Word",
    "WordEntry",
    "DictUpdater",
    "UpdateScheduler",
]
