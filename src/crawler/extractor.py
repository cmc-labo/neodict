"""
テキストから新語を抽出
"""

import re
from typing import List, Set, Dict
import logging

logger = logging.getLogger(__name__)


class WordExtractor:
    """テキストから新語や固有表現を抽出"""

    def __init__(self):
        # カタカナ語のパターン
        self.katakana_pattern = re.compile(r'[ァ-ヴー]{2,}')

        # 英数字混じりの語(例: ChatGPT, iPhone15)
        self.alphanum_pattern = re.compile(r'[A-Za-z0-9][A-Za-z0-9ァ-ヴー]{1,}[A-Za-z0-9]')

        # 固有名詞パターン(カタカナ+助詞の前)
        self.proper_noun_pattern = re.compile(r'([ァ-ヴー]{2,})(が|は|を|に|で|と|や|の)')

        # 除外パターン
        self.exclude_patterns = [
            re.compile(r'^[ァ-ヴー]{1}$'),  # 1文字のカタカナ
            re.compile(r'^ー+$'),  # 長音符のみ
            re.compile(r'^[0-9]+$'),  # 数字のみ
        ]

    def extract_katakana_words(self, text: str) -> Set[str]:
        """
        カタカナ語を抽出

        Args:
            text: 入力テキスト

        Returns:
            抽出したカタカナ語の集合
        """
        words = set()

        for match in self.katakana_pattern.finditer(text):
            word = match.group(0)
            if not self._should_exclude(word):
                words.add(word)

        return words

    def extract_alphanum_words(self, text: str) -> Set[str]:
        """
        英数字混じりの語を抽出

        Args:
            text: 入力テキスト

        Returns:
            抽出した語の集合
        """
        words = set()

        for match in self.alphanum_pattern.finditer(text):
            word = match.group(0)
            if not self._should_exclude(word):
                words.add(word)

        return words

    def extract_proper_nouns(self, text: str) -> Set[str]:
        """
        固有名詞を抽出(簡易版)

        Args:
            text: 入力テキスト

        Returns:
            抽出した固有名詞の集合
        """
        words = set()

        for match in self.proper_noun_pattern.finditer(text):
            word = match.group(1)
            if not self._should_exclude(word):
                words.add(word)

        return words

    def extract_all(self, text: str) -> Dict[str, Set[str]]:
        """
        全ての新語候補を抽出

        Args:
            text: 入力テキスト

        Returns:
            カテゴリ別の語の辞書
        """
        return {
            "katakana": self.extract_katakana_words(text),
            "alphanum": self.extract_alphanum_words(text),
            "proper_nouns": self.extract_proper_nouns(text)
        }

    def _should_exclude(self, word: str) -> bool:
        """
        除外すべき語かチェック

        Args:
            word: チェックする語

        Returns:
            除外する場合True
        """
        for pattern in self.exclude_patterns:
            if pattern.match(word):
                return True

        # 長すぎる語を除外
        if len(word) > 20:
            return True

        return False

    def count_frequency(self, text: str, words: Set[str]) -> Dict[str, int]:
        """
        テキスト中の語の出現頻度をカウント

        Args:
            text: 対象テキスト
            words: カウント対象の語の集合

        Returns:
            語とその頻度の辞書
        """
        frequency = {}

        for word in words:
            count = text.count(word)
            if count > 0:
                frequency[word] = count

        return frequency
