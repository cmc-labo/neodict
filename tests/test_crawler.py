"""
クローラーのテスト
"""

import pytest
import sys
from pathlib import Path

# パスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from crawler import WordExtractor


class TestWordExtractor:
    """WordExtractorクラスのテスト"""

    @pytest.fixture
    def extractor(self):
        """エクストラクターのインスタンスを作成"""
        return WordExtractor()

    def test_extract_katakana_words(self, extractor):
        """カタカナ語抽出のテスト"""
        text = "ChatGPTはオープンエーアイが開発したチャットボットです。"
        words = extractor.extract_katakana_words(text)

        assert "オープンエーアイ" in words
        assert "チャットボット" in words

    def test_extract_alphanum_words(self, extractor):
        """英数字混じり語抽出のテスト"""
        text = "iPhone15とChatGPTを使って作業しました。"
        words = extractor.extract_alphanum_words(text)

        assert "iPhone15" in words
        assert "ChatGPT" in words

    def test_extract_proper_nouns(self, extractor):
        """固有名詞抽出のテスト"""
        text = "トヨタが新型プリウスを発表しました。"
        words = extractor.extract_proper_nouns(text)

        assert "トヨタ" in words
        assert "プリウス" in words

    def test_extract_all(self, extractor):
        """全抽出のテスト"""
        text = """
        ChatGPTはオープンエーアイが開発した生成AIです。
        iPhone15とMacBookで作業できます。
        """
        result = extractor.extract_all(text)

        assert "katakana" in result
        assert "alphanum" in result
        assert "proper_nouns" in result

        # カタカナ語
        assert "オープンエーアイ" in result["katakana"]

        # 英数字混じり
        assert "ChatGPT" in result["alphanum"]
        assert "iPhone15" in result["alphanum"]

    def test_count_frequency(self, extractor):
        """頻度カウントのテスト"""
        text = "AIを使ってAIアシスタントを作る。AIは便利です。"
        words = {"AI", "アシスタント"}

        frequency = extractor.count_frequency(text, words)

        assert frequency["AI"] == 3
        assert frequency["アシスタント"] == 1

    def test_exclude_patterns(self, extractor):
        """除外パターンのテスト"""
        text = "123 あ ABC ーーー テスト"
        words = extractor.extract_katakana_words(text)

        # 1文字のカタカナは除外
        assert "あ" not in words

        # 長音符のみは除外
        assert "ーーー" not in words

        # 正しいカタカナ語は抽出
        assert "テスト" in words


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
