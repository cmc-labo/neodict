"""
辞書更新システム
"""

import logging
from typing import List, Dict, Set
from datetime import datetime
from ..core import NeoDict, WordEntry, Word, PartOfSpeech, WordSource
from ..crawler import WikipediaCrawler, NewsCrawler

logger = logging.getLogger(__name__)


class DictUpdater:
    """辞書の更新を管理"""

    def __init__(
        self,
        dict_instance: NeoDict = None,
        sources: List[str] = None,
        min_frequency: int = 2
    ):
        """
        初期化

        Args:
            dict_instance: 更新対象の辞書
            sources: 更新元のリスト
            min_frequency: 辞書に追加する最小頻度
        """
        self.dict = dict_instance or NeoDict()
        self.sources = sources or ["wikipedia", "news"]
        self.min_frequency = min_frequency

        self.wikipedia_crawler = WikipediaCrawler()
        self.news_crawler = NewsCrawler()

    def update(self, full_update: bool = False) -> Dict:
        """
        辞書を更新

        Args:
            full_update: 全更新を行うか(Falseの場合は差分更新)

        Returns:
            更新結果の統計
        """
        logger.info("Starting dictionary update...")

        start_time = datetime.now()
        collected_words = []

        # 各ソースから単語を収集
        if "wikipedia" in self.sources:
            logger.info("Collecting from Wikipedia...")
            wiki_words = self.wikipedia_crawler.crawl(
                recent_changes=True,
                limit=100
            )
            collected_words.extend(wiki_words)

        if "news" in self.sources:
            logger.info("Collecting from news sources...")
            news_words = self.news_crawler.crawl(
                sources=["nhk", "yahoo"],
                limit=50
            )
            collected_words.extend(news_words)

        # 単語を集計(同じ表層形の頻度を合算)
        word_freq = {}
        word_data = {}

        for word_info in collected_words:
            surface = word_info["surface"]
            freq = word_info.get("frequency", 1)

            if surface in word_freq:
                word_freq[surface] += freq
            else:
                word_freq[surface] = freq
                word_data[surface] = word_info

        # 頻度フィルタリングして辞書に追加
        added_count = 0
        updated_count = 0

        for surface, freq in word_freq.items():
            if freq < self.min_frequency:
                continue

            info = word_data[surface]

            # 既存の単語かチェック
            existing = self.dict.get_word(surface)

            if existing:
                # 既存の場合は頻度を更新
                updated_count += 1
            else:
                # 新規追加
                self.dict.add_word(
                    surface=surface,
                    source=info.get("source", "other"),
                    category=info.get("category"),
                    frequency=freq
                )
                added_count += 1

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        stats = {
            "collected_words": len(collected_words),
            "unique_words": len(word_freq),
            "added": added_count,
            "updated": updated_count,
            "duration_seconds": duration,
            "timestamp": end_time.isoformat()
        }

        logger.info(f"Update completed: {stats}")
        return stats

    def update_from_source(self, source: str, **kwargs) -> int:
        """
        特定のソースから更新

        Args:
            source: ソース名(wikipedia, news等)
            **kwargs: ソース固有のパラメータ

        Returns:
            追加した単語数
        """
        words = []

        if source == "wikipedia":
            words = self.wikipedia_crawler.crawl(**kwargs)
        elif source == "news":
            words = self.news_crawler.crawl(**kwargs)

        count = 0
        for word_info in words:
            self.dict.add_word(
                surface=word_info["surface"],
                source=word_info.get("source", source),
                category=word_info.get("category"),
                frequency=word_info.get("frequency", 1)
            )
            count += 1

        return count

    def cleanup(self, min_frequency: int = 1, max_age_days: int = 365) -> int:
        """
        低頻度語や古い語を削除

        Args:
            min_frequency: この頻度未満の語を削除
            max_age_days: この日数より古い語を削除

        Returns:
            削除した単語数
        """
        logger.info(f"Cleaning up dictionary (freq<{min_frequency}, age>{max_age_days}days)...")

        # TODO: 実装
        # 現在のストレージAPIでは日付フィルタリングが未実装のため、
        # 将来的に実装予定

        return 0

    def get_update_history(self, limit: int = 10) -> List[Dict]:
        """
        更新履歴を取得

        Args:
            limit: 最大取得数

        Returns:
            更新履歴のリスト
        """
        # TODO: 実装
        # バージョン管理テーブルから履歴を取得

        return []
