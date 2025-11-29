"""
Wikipedia日本語版からのクローラー
"""

from typing import List, Dict, Optional
import logging
from .base import BaseCrawler
from .extractor import WordExtractor

logger = logging.getLogger(__name__)


class WikipediaCrawler(BaseCrawler):
    """Wikipedia日本語版からの新語収集"""

    BASE_URL = "https://ja.wikipedia.org"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extractor = WordExtractor()

    def crawl(
        self,
        categories: Optional[List[str]] = None,
        recent_changes: bool = True,
        limit: int = 100
    ) -> List[Dict]:
        """
        Wikipediaから新語を収集

        Args:
            categories: 収集対象のカテゴリ
            recent_changes: 最近の更新から収集するか
            limit: 最大収集数

        Returns:
            収集した単語のリスト
        """
        words = []

        if recent_changes:
            words.extend(self._crawl_recent_changes(limit=limit))

        if categories:
            for category in categories:
                words.extend(self._crawl_category(category, limit=limit))

        return words

    def _crawl_recent_changes(self, limit: int = 100) -> List[Dict]:
        """
        最近の更新ページから新語を収集

        Args:
            limit: 最大収集数

        Returns:
            収集した単語のリスト
        """
        logger.info("Crawling Wikipedia recent changes...")

        url = f"{self.BASE_URL}/wiki/Special:RecentChanges"
        soup = self.fetch(url)

        if not soup:
            return []

        words = []
        # 新規ページのタイトルを収集
        for link in soup.select('.mw-changeslist-line a.mw-changeslist-title')[:limit]:
            title = link.get_text(strip=True)
            if title:
                words.append({
                    "surface": title,
                    "source": "wikipedia",
                    "category": "recent_changes",
                    "frequency": 1
                })

        logger.info(f"Collected {len(words)} words from recent changes")
        return words

    def _crawl_category(self, category: str, limit: int = 100) -> List[Dict]:
        """
        特定カテゴリから記事タイトルを収集

        Args:
            category: カテゴリ名
            limit: 最大収集数

        Returns:
            収集した単語のリスト
        """
        logger.info(f"Crawling Wikipedia category: {category}")

        url = f"{self.BASE_URL}/wiki/Category:{category}"
        soup = self.fetch(url)

        if not soup:
            return []

        words = []
        # カテゴリ内のページタイトルを収集
        for link in soup.select('#mw-pages a')[:limit]:
            title = link.get_text(strip=True)
            if title:
                words.append({
                    "surface": title,
                    "source": "wikipedia",
                    "category": category,
                    "frequency": 1
                })

        logger.info(f"Collected {len(words)} words from category: {category}")
        return words

    def crawl_article(self, title: str) -> List[Dict]:
        """
        特定の記事から新語を抽出

        Args:
            title: 記事タイトル

        Returns:
            抽出した単語のリスト
        """
        url = f"{self.BASE_URL}/wiki/{title}"
        soup = self.fetch(url)

        if not soup:
            return []

        # 記事本文を取得
        content = soup.select_one('#mw-content-text .mw-parser-output')
        if not content:
            return []

        text = content.get_text()

        # 新語を抽出
        extracted = self.extractor.extract_all(text)

        words = []
        for category, word_set in extracted.items():
            frequency = self.extractor.count_frequency(text, word_set)

            for word in word_set:
                words.append({
                    "surface": word,
                    "source": "wikipedia",
                    "category": f"article_{category}",
                    "frequency": frequency.get(word, 1)
                })

        return words

    def get_trending_articles(self, limit: int = 50) -> List[str]:
        """
        トレンド記事のタイトルを取得

        Args:
            limit: 最大取得数

        Returns:
            記事タイトルのリスト
        """
        # Wikipedia APIを使用してトレンド記事を取得
        api_url = f"{self.BASE_URL}/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "mostviewed",
            "pvimdays": 1,
            "pvimlimit": limit
        }

        try:
            response = self.session.get(api_url, params=params, timeout=self.timeout)
            data = response.json()

            if "query" in data and "mostviewed" in data["query"]:
                return [item["title"] for item in data["query"]["mostviewed"]]

        except Exception as e:
            logger.error(f"Error fetching trending articles: {e}")

        return []
