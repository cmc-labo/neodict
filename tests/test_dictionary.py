"""
辞書機能のテスト
"""

import pytest
import sys
from pathlib import Path
import tempfile

# パスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core import NeoDict, Word, WordEntry, PartOfSpeech, WordSource


class TestNeoDict:
    """NeoDictクラスのテスト"""

    @pytest.fixture
    def temp_dict(self):
        """一時的な辞書を作成"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        neodict = NeoDict(db_path=db_path)
        yield neodict

        # クリーンアップ
        Path(db_path).unlink(missing_ok=True)

    def test_add_word(self, temp_dict):
        """単語追加のテスト"""
        word_id = temp_dict.add_word(
            surface="テスト語",
            pos="名詞",
            reading="テストゴ",
            source="manual"
        )

        assert word_id > 0

    def test_search_word(self, temp_dict):
        """単語検索のテスト"""
        # 単語を追加
        temp_dict.add_word(
            surface="ChatGPT",
            pos="名詞",
            reading="チャットジーピーティー",
            source="manual"
        )

        # 検索
        results = temp_dict.search("ChatGPT")
        assert len(results) > 0
        assert results[0]["surface"] == "ChatGPT"

    def test_fuzzy_search(self, temp_dict):
        """あいまい検索のテスト"""
        # 複数の単語を追加
        words = ["ChatGPT", "生成AI", "AIアシスタント"]
        for word in words:
            temp_dict.add_word(surface=word, source="manual")

        # あいまい検索
        results = temp_dict.search("AI", fuzzy=True)
        assert len(results) >= 2  # "生成AI" と "AIアシスタント" がヒット

    def test_get_word(self, temp_dict):
        """単語取得のテスト"""
        surface = "推し活"
        temp_dict.add_word(
            surface=surface,
            pos="名詞",
            reading="オシカツ",
            source="manual"
        )

        result = temp_dict.get_word(surface)
        assert result is not None
        assert result["surface"] == surface

    def test_remove_word(self, temp_dict):
        """単語削除のテスト"""
        surface = "削除テスト"
        temp_dict.add_word(surface=surface, source="manual")

        # 削除
        count = temp_dict.remove_word(surface)
        assert count == 1

        # 削除後は見つからない
        result = temp_dict.get_word(surface)
        assert result is None

    def test_stats(self, temp_dict):
        """統計情報のテスト"""
        # 複数の単語を追加
        for i in range(10):
            temp_dict.add_word(
                surface=f"単語{i}",
                source="manual"
            )

        stats = temp_dict.get_stats()
        assert stats["total_words"] == 10


class TestWord:
    """Wordクラスのテスト"""

    def test_word_creation(self):
        """単語オブジェクト作成のテスト"""
        word = Word(
            surface="テスト",
            reading="テスト"
        )

        assert word.surface == "テスト"
        assert word.reading == "テスト"
        assert word.pronunciation == "テスト"  # 自動設定

    def test_word_without_reading(self):
        """読みなしの単語のテスト"""
        word = Word(surface="Test")

        assert word.surface == "Test"
        assert word.reading is None


class TestWordEntry:
    """WordEntryクラスのテスト"""

    def test_entry_creation(self):
        """エントリー作成のテスト"""
        word = Word(surface="エモい", reading="エモイ")
        entry = WordEntry(
            word=word,
            pos=PartOfSpeech.ADJECTIVE,
            source=WordSource.MANUAL,
            frequency=10
        )

        assert entry.word.surface == "エモい"
        assert entry.pos == PartOfSpeech.ADJECTIVE
        assert entry.frequency == 10

    def test_to_mecab_csv(self):
        """MeCab CSV変換のテスト"""
        word = Word(surface="テスト", reading="テスト")
        entry = WordEntry(word=word, pos=PartOfSpeech.NOUN)

        csv = entry.to_mecab_csv()
        parts = csv.split(",")

        assert parts[0] == "テスト"  # 表層形
        assert parts[4] == "名詞"    # 品詞

    def test_to_dict(self):
        """辞書変換のテスト"""
        word = Word(surface="変換テスト", reading="ヘンカンテスト")
        entry = WordEntry(
            word=word,
            pos=PartOfSpeech.NOUN,
            source=WordSource.WIKIPEDIA,
            category="IT"
        )

        data = entry.to_dict()

        assert data["surface"] == "変換テスト"
        assert data["reading"] == "ヘンカンテスト"
        assert data["pos"] == "名詞"
        assert data["source"] == "wikipedia"
        assert data["category"] == "IT"

    def test_from_dict(self):
        """辞書から復元のテスト"""
        data = {
            "surface": "復元テスト",
            "reading": "フクゲンテスト",
            "pos": "名詞",
            "pos_detail": ["一般", "*", "*"],
            "source": "manual",
            "frequency": 5
        }

        entry = WordEntry.from_dict(data)

        assert entry.word.surface == "復元テスト"
        assert entry.word.reading == "フクゲンテスト"
        assert entry.pos == PartOfSpeech.NOUN
        assert entry.frequency == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
