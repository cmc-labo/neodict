"""
辞書データの永続化ストレージ
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from .word import WordEntry, Word, PartOfSpeech, WordSource


class DictStorage:
    """SQLiteベースの辞書ストレージ"""

    def __init__(self, db_path: str = "~/.neodict/dict.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """データベースの初期化"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 単語テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    surface TEXT NOT NULL UNIQUE,
                    reading TEXT,
                    pronunciation TEXT,
                    pos TEXT NOT NULL,
                    pos_detail1 TEXT,
                    pos_detail2 TEXT,
                    pos_detail3 TEXT,
                    conjugation_type TEXT,
                    conjugation_form TEXT,
                    base_form TEXT,
                    frequency INTEGER DEFAULT 0,
                    source TEXT,
                    category TEXT,
                    cost INTEGER DEFAULT 6000,
                    left_context_id INTEGER DEFAULT 1285,
                    right_context_id INTEGER DEFAULT 1285,
                    added_date TIMESTAMP,
                    last_updated TIMESTAMP
                )
            """)

            # インデックス作成
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_surface ON words(surface)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reading ON words(reading)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pos ON words(pos)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_frequency ON words(frequency DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON words(source)")

            # バージョン管理テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_date TIMESTAMP,
                    word_count INTEGER,
                    description TEXT
                )
            """)

            conn.commit()

    def add_word(self, entry: WordEntry) -> int:
        """単語を追加"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO words (
                        surface, reading, pronunciation, pos,
                        pos_detail1, pos_detail2, pos_detail3,
                        conjugation_type, conjugation_form, base_form,
                        frequency, source, category,
                        cost, left_context_id, right_context_id,
                        added_date, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.word.surface,
                    entry.word.reading,
                    entry.word.pronunciation,
                    entry.pos.value,
                    entry.pos_detail1,
                    entry.pos_detail2,
                    entry.pos_detail3,
                    entry.conjugation_type,
                    entry.conjugation_form,
                    entry.base_form,
                    entry.frequency,
                    entry.source.value,
                    entry.category,
                    entry.cost,
                    entry.left_context_id,
                    entry.right_context_id,
                    entry.added_date,
                    entry.last_updated
                ))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # 重複の場合は更新
                return self.update_word(entry)

    def update_word(self, entry: WordEntry) -> int:
        """単語を更新"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE words SET
                    reading = ?,
                    pronunciation = ?,
                    pos = ?,
                    pos_detail1 = ?,
                    pos_detail2 = ?,
                    pos_detail3 = ?,
                    conjugation_type = ?,
                    conjugation_form = ?,
                    base_form = ?,
                    frequency = ?,
                    source = ?,
                    category = ?,
                    cost = ?,
                    left_context_id = ?,
                    right_context_id = ?,
                    last_updated = ?
                WHERE surface = ?
            """, (
                entry.word.reading,
                entry.word.pronunciation,
                entry.pos.value,
                entry.pos_detail1,
                entry.pos_detail2,
                entry.pos_detail3,
                entry.conjugation_type,
                entry.conjugation_form,
                entry.base_form,
                entry.frequency,
                entry.source.value,
                entry.category,
                entry.cost,
                entry.left_context_id,
                entry.right_context_id,
                datetime.now(),
                entry.word.surface
            ))
            conn.commit()
            return cursor.rowcount

    def get_word(self, surface: str) -> Optional[WordEntry]:
        """単語を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM words WHERE surface = ?", (surface,))
            row = cursor.fetchone()

            if row:
                return self._row_to_entry(row)
            return None

    def search_words(self, query: str, fuzzy: bool = False, limit: int = 100) -> List[WordEntry]:
        """単語を検索"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if fuzzy:
                cursor.execute(
                    "SELECT * FROM words WHERE surface LIKE ? OR reading LIKE ? LIMIT ?",
                    (f"%{query}%", f"%{query}%", limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM words WHERE surface = ? OR reading = ? LIMIT ?",
                    (query, query, limit)
                )

            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def get_all_words(self, limit: Optional[int] = None) -> List[WordEntry]:
        """全単語を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if limit:
                cursor.execute("SELECT * FROM words ORDER BY frequency DESC LIMIT ?", (limit,))
            else:
                cursor.execute("SELECT * FROM words ORDER BY frequency DESC")

            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def delete_word(self, surface: str) -> int:
        """単語を削除"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM words WHERE surface = ?", (surface,))
            conn.commit()
            return cursor.rowcount

    def get_stats(self) -> Dict:
        """統計情報を取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM words")
            total_words = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT pos) FROM words")
            unique_pos = cursor.fetchone()[0]

            cursor.execute("SELECT source, COUNT(*) FROM words GROUP BY source")
            sources = dict(cursor.fetchall())

            cursor.execute("SELECT pos, COUNT(*) FROM words GROUP BY pos ORDER BY COUNT(*) DESC")
            pos_distribution = dict(cursor.fetchall())

            return {
                "total_words": total_words,
                "unique_pos": unique_pos,
                "sources": sources,
                "pos_distribution": pos_distribution
            }

    def _row_to_entry(self, row: sqlite3.Row) -> WordEntry:
        """SQLite行をWordEntryに変換"""
        word = Word(
            surface=row["surface"],
            reading=row["reading"],
            pronunciation=row["pronunciation"]
        )

        return WordEntry(
            word=word,
            pos=PartOfSpeech(row["pos"]),
            pos_detail1=row["pos_detail1"] or "*",
            pos_detail2=row["pos_detail2"] or "*",
            pos_detail3=row["pos_detail3"] or "*",
            conjugation_type=row["conjugation_type"] or "*",
            conjugation_form=row["conjugation_form"] or "*",
            base_form=row["base_form"],
            frequency=row["frequency"],
            source=WordSource(row["source"]),
            category=row["category"],
            cost=row["cost"],
            left_context_id=row["left_context_id"],
            right_context_id=row["right_context_id"],
            added_date=datetime.fromisoformat(row["added_date"]) if row["added_date"] else datetime.now(),
            last_updated=datetime.fromisoformat(row["last_updated"]) if row["last_updated"] else datetime.now()
        )
