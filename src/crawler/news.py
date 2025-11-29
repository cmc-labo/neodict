"""
ニュースサイトからのクローラー
"""

from typing import List, Dict, Optional
import logging
from .base import BaseCrawler
from .extractor import WordExtractor

logger = logging.getLogger(__name__)


class NewsCrawler(BaseCrawler):
    """ニュースサイトからの新語収集"""

    SOURCES = {
        "nhk": "https://www3.nhk.or.jp/news/",
        "yahoo": "https://news.yahoo.co.jp/",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extractor = WordExtractor()

    def crawl(
        self,
        sources: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        ニュースサイトから新語を収集

        Args:
            sources: 収集対象のソース(nhk, yahoo等)
            limit: 最大収集数

        Returns:
            収集した単語のリスト
        """
        if sources is None:
            sources = list(self.SOURCES.keys())

        words = []

        for source in sources:
            if source in self.SOURCES:
                words.extend(self._crawl_source(source, limit=limit))

        return words

    def _crawl_source(self, source: str, limit: int = 50) -> List[Dict]:
        """
        特定のニュースソースから収集

        Args:
            source: ソース名
            limit: 最大収集数

        Returns:
            収集した単語のリスト
        """
        if source == "nhk":
            return self._crawl_nhk(limit)
        elif source == "yahoo":
            return self._crawl_yahoo(limit)

        return []

    def _crawl_nhk(self, limit: int = 50) -> List[Dict]:
        """
        NHKニュースから収集

        Args:
            limit: 最大収集数

        Returns:
            収集した単語のリスト
        """
        logger.info("Crawling NHK News...")

        url = self.SOURCES["nhk"]
        soup = self.fetch(url)

        if not soup:
            return []

        words = []
        articles = soup.select('article.content--list-item')[:limit]

        for article in articles:
            # 見出しとリード文を取得
            title_elem = article.select_one('.content--list-title')
            summary_elem = article.select_one('.content--summary')

            title = title_elem.get_text(strip=True) if title_elem else ""
            summary = summary_elem.get_text(strip=True) if summary_elem else ""

            text = f"{title} {summary}"

            # 新語を抽出
            extracted = self.extractor.extract_all(text)

            for category, word_set in extracted.items():
                frequency = self.extractor.count_frequency(text, word_set)

                for word in word_set:
                    words.append({
                        "surface": word,
                        "source": "news_nhk",
                        "category": f"news_{category}",
                        "frequency": frequency.get(word, 1)
                    })

        logger.info(f"Collected {len(words)} words from NHK News")
        return words

    def _crawl_yahoo(self, limit: int = 50) -> List[Dict]:
        """
        Yahoo!ニュースから収集

        Args:
            limit: 最大収集数

        Returns:
            収集した単語のリスト
        """
        logger.info("Crawling Yahoo! News...")

        url = self.SOURCES["yahoo"]
        soup = self.fetch(url)

        if not soup:
            return []

        words = []
        # トピックスのヘッドラインを収集
        headlines = soup.select('.newsFeed_item_title')[:limit]

        for headline in headlines:
            text = headline.get_text(strip=True)

            # 新語を抽出
            extracted = self.extractor.extract_all(text)

            for category, word_set in extracted.items():
                frequency = self.extractor.count_frequency(text, word_set)

                for word in word_set:
                    words.append({
                        "surface": word,
                        "source": "news_yahoo",
                        "category": f"news_{category}",
                        "frequency": frequency.get(word, 1)
                    })

        logger.info(f"Collected {len(words)} words from Yahoo! News")
        return words

    def crawl_article_content(self, url: str) -> List[Dict]:
        """
        記事本文から新語を抽出

        Args:
            url: 記事URL

        Returns:
            抽出した単語のリスト
        """
        soup = self.fetch(url)

        if not soup:
            return []

        # 記事本文を取得(サイトによってセレクターが異なる)
        content = (
            soup.select_one('article .article-body') or
            soup.select_one('.article-main') or
            soup.select_one('.news-body')
        )

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
                    "source": "news_article",
                    "category": f"article_{category}",
                    "frequency": frequency.get(word, 1)
                })

        return words
