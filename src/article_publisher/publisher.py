# ==============================================================================
# FILE: src/article_publisher/publisher.py
# ==============================================================================
"""Main article publisher logic."""

import time
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from .config import get_api_key
from .hashnode_client import HashnodeClient
from .markdown_parser import MarkdownParser


class ArticlePublisher:
    """Main article publisher orchestrator."""
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize article publisher.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.parser = MarkdownParser()
        
        # Initialize Hashnode client
        pub_config = config['article-publisher']
        self.client = HashnodeClient(
            api_key=get_api_key(),
            server_url=pub_config['server'],
            header_name=pub_config['api-header'],
            timeout=pub_config['timeout'],
            retry_count=pub_config['retry'],
            logger=logger
        )
        
        self.publication_id = pub_config['publication-id']
        self.rate_limit_delay = pub_config['rate-limit-delay']
        
        # Get timezone
        self.timezone = ZoneInfo(pub_config['timezone'])
    
    def get_today_articles_path(self) -> Path:
        """
        Get path to today's articles directory.
        
        Returns:
            Path to today's articles
        """
        base_path = Path(
            self.config['article-generator']['tech-trend-article']
        )
        # Use date.today() with configured timezone
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        return base_path / today_str
    
    def find_markdown_files(self, directory: Path) -> List[Path]:
        """
        Find all markdown files in directory recursively.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of markdown file paths
        """
        if not directory.exists():
            self.logger.warning(f"Directory not found: {directory}")
            return []
        
        return list(directory.rglob('*.md'))
    
    def publish_today_articles(self) -> Tuple[int, int]:
        """
        Publish all articles from today's directory.
        
        Returns:
            Tuple of (success_count, fail_count)
        """
        articles_dir = self.get_today_articles_path()
        self.logger.info(f"Processing articles from: {articles_dir}")
        self.logger.info(f"Using timezone: {self.timezone}")
        
        md_files = self.find_markdown_files(articles_dir)
        
        if not md_files:
            self.logger.warning("No markdown files found")
            return 0, 0
        
        self.logger.info(f"Found {len(md_files)} markdown files")
        
        success_count = 0
        fail_count = 0
        
        for idx, md_file in enumerate(md_files):
            # Parse article
            result = self.parser.parse_article(md_file, self.logger)
            if not result:
                fail_count += 1
                continue
            
            title, content = result
            
            # Publish to Hashnode
            response = self.client.publish_article(
                title=title,
                content=content,
                publication_id=self.publication_id
            )
            
            if response:
                success_count += 1
            else:
                fail_count += 1
            
            # Rate limiting: add delay between publishes (except last one)
            if idx < len(md_files) - 1 and self.rate_limit_delay > 0:
                self.logger.debug(
                    f"Rate limiting: waiting {self.rate_limit_delay}s"
                )
                time.sleep(self.rate_limit_delay)
        
        return success_count, fail_count