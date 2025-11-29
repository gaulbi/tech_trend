"""
RSS Feed Aggregator Package
A modular RSS feed fetching and organization system
"""

__version__ = "1.0.0"
__author__ = "RSS Aggregator Team"

from config import ConfigManager, AppConfig
from feed_fetcher import FeedFetcher, FeedEntry
from feed_processor import FeedProcessor
from output_writer import OutputWriter
from utils import setup_logging, sanitize_filename

__all__ = [
    "ConfigManager",
    "AppConfig",
    "FeedFetcher",
    "FeedEntry",
    "FeedProcessor",
    "OutputWriter",
    "setup_logging",
    "sanitize_filename",
]