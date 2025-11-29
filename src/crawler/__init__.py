"""
NeoDict Crawler Module
ウェブから新語・固有表現を収集
"""

from .base import BaseCrawler
from .wikipedia import WikipediaCrawler
from .news import NewsCrawler
from .extractor import WordExtractor

__all__ = ["BaseCrawler", "WikipediaCrawler", "NewsCrawler", "WordExtractor"]
