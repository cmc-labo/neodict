"""
単語データモデル
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class PartOfSpeech(Enum):
    """品詞"""
    NOUN = "名詞"
    VERB = "動詞"
    ADJECTIVE = "形容詞"
    ADVERB = "副詞"
    PARTICLE = "助詞"
    AUXILIARY = "助動詞"
    CONJUNCTION = "接続詞"
    INTERJECTION = "感動詞"
    SYMBOL = "記号"
    UNKNOWN = "未知語"


class WordSource(Enum):
    """語彙の収集元"""
    WIKIPEDIA = "wikipedia"
    NEWS = "news"
    TWITTER = "twitter"
    MANUAL = "manual"
    HATENA = "hatena"
    OTHER = "other"


@dataclass
class Word:
    """単語の基本情報"""
    surface: str  # 表層形
    reading: Optional[str] = None  # 読み
    pronunciation: Optional[str] = None  # 発音

    def __post_init__(self):
        if self.pronunciation is None and self.reading is not None:
            self.pronunciation = self.reading


@dataclass
class WordEntry:
    """辞書エントリー(拡張情報を含む)"""
    word: Word
    pos: PartOfSpeech = PartOfSpeech.UNKNOWN
    pos_detail1: str = "*"
    pos_detail2: str = "*"
    pos_detail3: str = "*"
    conjugation_type: str = "*"
    conjugation_form: str = "*"
    base_form: Optional[str] = None

    # メタ情報
    frequency: int = 0  # 出現頻度
    source: WordSource = WordSource.OTHER
    category: Optional[str] = None  # カテゴリ(IT、芸能、スポーツなど)
    added_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    # MeCab用コスト(低いほど優先度高)
    cost: int = 6000
    left_context_id: int = 1285
    right_context_id: int = 1285

    def __post_init__(self):
        if self.base_form is None:
            self.base_form = self.word.surface

    def to_mecab_csv(self) -> str:
        """MeCab辞書形式のCSV行を生成"""
        reading = self.word.reading or self.word.surface
        pronunciation = self.word.pronunciation or reading

        return ",".join([
            self.word.surface,
            str(self.left_context_id),
            str(self.right_context_id),
            str(self.cost),
            self.pos.value,
            self.pos_detail1,
            self.pos_detail2,
            self.pos_detail3,
            self.conjugation_type,
            self.conjugation_form,
            self.base_form,
            reading,
            pronunciation
        ])

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "surface": self.word.surface,
            "reading": self.word.reading,
            "pronunciation": self.word.pronunciation,
            "pos": self.pos.value,
            "pos_detail": [self.pos_detail1, self.pos_detail2, self.pos_detail3],
            "conjugation": {
                "type": self.conjugation_type,
                "form": self.conjugation_form
            },
            "base_form": self.base_form,
            "frequency": self.frequency,
            "source": self.source.value,
            "category": self.category,
            "added_date": self.added_date.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WordEntry":
        """辞書形式から生成"""
        word = Word(
            surface=data["surface"],
            reading=data.get("reading"),
            pronunciation=data.get("pronunciation")
        )

        return cls(
            word=word,
            pos=PartOfSpeech(data.get("pos", "未知語")),
            pos_detail1=data.get("pos_detail", ["*", "*", "*"])[0],
            pos_detail2=data.get("pos_detail", ["*", "*", "*"])[1],
            pos_detail3=data.get("pos_detail", ["*", "*", "*"])[2],
            conjugation_type=data.get("conjugation", {}).get("type", "*"),
            conjugation_form=data.get("conjugation", {}).get("form", "*"),
            base_form=data.get("base_form"),
            frequency=data.get("frequency", 0),
            source=WordSource(data.get("source", "other")),
            category=data.get("category"),
            added_date=datetime.fromisoformat(data.get("added_date", datetime.now().isoformat())),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        )
