"""
メイン辞書クラス
"""

from pathlib import Path
from typing import List, Optional, Dict
from .word import WordEntry, Word, PartOfSpeech, WordSource
from .storage import DictStorage
import fugashi


class NeoDict:
    """NeoDict メイン辞書クラス"""

    def __init__(self, db_path: str = "~/.neodict/dict.db"):
        """
        辞書を初期化

        Args:
            db_path: データベースファイルのパス
        """
        self.storage = DictStorage(db_path)
        try:
            self.tagger = fugashi.Tagger()
        except Exception:
            self.tagger = None

    def add_word(
        self,
        surface: str,
        pos: str = "名詞",
        reading: Optional[str] = None,
        source: str = "manual",
        category: Optional[str] = None,
        **kwargs
    ) -> int:
        """
        単語を追加

        Args:
            surface: 表層形(単語そのもの)
            pos: 品詞
            reading: 読み
            source: 収集元
            category: カテゴリ
            **kwargs: その他のオプション

        Returns:
            追加された単語のID
        """
        word = Word(surface=surface, reading=reading)

        entry = WordEntry(
            word=word,
            pos=PartOfSpeech(pos),
            source=WordSource(source),
            category=category,
            frequency=kwargs.get("frequency", 0)
        )

        return self.storage.add_word(entry)

    def suggest_reading(self, surface: str) -> Optional[str]:
        """
        単語の読みを推定

        Args:
            surface: 表層形

        Returns:
            推定された読み(カタカナ)
        """
        if not self.tagger:
            return None

        words = []
        for word in self.tagger(surface):
            # UniDic形式を想定 (2番目のフィールドが読み)
            # 生データにアクセスするには word.feature
            if word.feature.kana:
                words.append(word.feature.kana)
            else:
                # 読みがない場合は表層形をそのまま利用(英数字等)
                words.append(word.surface)

        return "".join(words)

    def search(self, query: str, fuzzy: bool = False, limit: int = 100) -> List[Dict]:
        """
        単語を検索

        Args:
            query: 検索クエリ
            fuzzy: あいまい検索を有効にするか
            limit: 最大結果数

        Returns:
            検索結果のリスト
        """
        entries = self.storage.search_words(query, fuzzy=fuzzy, limit=limit)
        return [entry.to_dict() for entry in entries]

    def get_word(self, surface: str) -> Optional[Dict]:
        """
        単語を取得

        Args:
            surface: 表層形

        Returns:
            単語情報(存在しない場合はNone)
        """
        entry = self.storage.get_word(surface)
        return entry.to_dict() if entry else None

    def remove_word(self, surface: str) -> int:
        """
        単語を削除

        Args:
            surface: 削除する単語

        Returns:
            削除された行数
        """
        return self.storage.delete_word(surface)

    def get_stats(self) -> Dict:
        """
        辞書の統計情報を取得

        Returns:
            統計情報の辞書
        """
        return self.storage.get_stats()

    def export_mecab(self, output_path: str):
        """
        MeCab形式で辞書をエクスポート

        Args:
            output_path: 出力先ディレクトリ
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        csv_path = output_dir / "neodict.csv"

        entries = self.storage.get_all_words()

        with open(csv_path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(entry.to_mecab_csv() + "\n")

        print(f"MeCab辞書を出力しました: {csv_path}")
        print(f"総単語数: {len(entries)}")

    def export_json(self, output_path: str):
        """
        JSON形式で辞書をエクスポート

        Args:
            output_path: 出力ファイルパス
        """
        import json

        entries = self.storage.get_all_words()
        data = {
            "version": "0.1.0",
            "word_count": len(entries),
            "words": [entry.to_dict() for entry in entries]
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"JSON辞書を出力しました: {output_path}")
        print(f"総単語数: {len(entries)}")

    def export_sudachi(self, output_path: str):
        """
        Sudachi形式で辞書をエクスポート

        Args:
            output_path: 出力先ディレクトリ
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        csv_path = output_dir / "neodict_sudachi.csv"
        entries = self.storage.get_all_words()

        with open(csv_path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(entry.to_sudachi_csv() + "\n")

        print(f"Sudachi辞書を出力しました: {csv_path}")
        print(f"総単語数: {len(entries)}")

    def export_janome(self, output_path: str):
        """
        Janome形式で辞書をエクスポート

        Args:
            output_path: 出力先ディレクトリ
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        csv_path = output_dir / "neodict_janome.csv"
        entries = self.storage.get_all_words()

        with open(csv_path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(entry.to_janome_csv() + "\n")

        print(f"Janome辞書を出力しました: {csv_path}")
        print(f"総単語数: {len(entries)}")

    def import_words(self, entries: List[WordEntry]) -> int:
        """
        複数の単語を一括インポート

        Args:
            entries: WordEntryのリスト

        Returns:
            インポートした単語数
        """
        count = 0
        for entry in entries:
            self.storage.add_word(entry)
            count += 1

        return count
