"""
クローラーの基底クラス
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """クローラーの基底クラス"""

    def __init__(self, delay: float = 1.0, timeout: int = 10):
        """
        初期化

        Args:
            delay: リクエスト間の遅延(秒)
            timeout: タイムアウト時間(秒)
        """
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "NeoDict/0.1.0 (Japanese Dictionary Crawler)"
        })

    def fetch(self, url: str) -> Optional[BeautifulSoup]:
        """
        URLからコンテンツを取得

        Args:
            url: 取得先URL

        Returns:
            BeautifulSoupオブジェクト(失敗時はNone)
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            time.sleep(self.delay)
            return BeautifulSoup(response.content, "lxml")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    @abstractmethod
    def crawl(self, **kwargs) -> List[Dict]:
        """
        クロール実行

        Returns:
            収集した単語のリスト
        """
        pass

    def extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """
        HTML要素からテキストを抽出

        Args:
            soup: BeautifulSoupオブジェクト
            selector: CSSセレクター

        Returns:
            抽出したテキスト
        """
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else ""
