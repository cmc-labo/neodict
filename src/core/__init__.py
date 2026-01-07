"""
NeoDict Core Module
辞書の基本機能を提供
"""

from .dictionary import NeoDict
from .word import Word, WordEntry, PartOfSpeech, WordSource
from .storage import DictStorage

__all__ = ["NeoDict", "Word", "WordEntry", "DictStorage", "PartOfSpeech", "WordSource"]
