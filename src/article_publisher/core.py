"""Core article publisher logic."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .config import get_api_key
from .hashnode import HashnodeClient
from .loader import (
    load_article,
    load_image_mapping,
    find_articles
)
from .processor import process_article_content, validate_processed_content
from .storage import (
    check_already_published,
    save_publish_result
)
from .models import PublishResult
from .exceptions import (
    ArticleNotFoundError,
    ImageMappingError,
    PublishError
)
from .logger import get_logger

logger = get_logger(__name__)


class ArticlePublisher:
    """Main article publisher class."""
    
    def __init__(self, config: Dict[str, Any], feed_date: str):
        """
        Initialize article publisher.
        
        Args:
            config: Configuration dictionary
            feed_date: Feed date in YYYY-MM-DD format
        """
        self.config = config
        self.feed_date = feed_date
        
        # Extract configuration
        pub_config = config["article-publisher"]
        self.timeout = pub_config["timeout"]
        self.max_retries = pub_config["retry"]
        self.api_header = pub_config["api-header"]
        self.server_url = pub_config["server"]
        self.publication_id = pub_config["publication-id"]
        self.published_base = pub_config["published-article"]
        
        self.article_base = config["article-generator"]["tech-trend-article"]
        self.image_mapping_base = config["image-generator"]["url-mapping-path"]
        
        # Initialize Hashnode client
        api_key = get_api_key()
        self.client = HashnodeClient(
            server_url=self.server_url,
            api_key=api_key,
            api_header=self.api_header,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
    
    def publish_all(self) -> None:
        """Publish all articles for the feed date."""
        articles = find_articles(
            self.article_base,
            self.feed_date
        )
        
        if not articles:
            logger.warning(
                f"No articles found for {self.feed_date}",
                extra={"feed_date": self.feed_date}
            )
            return
        
        logger.info(
            f"Found {len(articles)} articles to process",
            extra={"count": len(articles)}
        )
        
        for category, article_path in articles:
            self._publish_article(category, article_path, check_idempotency=True)
    
    def publish_category(self, category: str) -> None:
        """
        Publish all articles in a specific category.
        
        Args:
            category: Category name
        """
        articles = find_articles(
            self.article_base,
            self.feed_date,
            category=category
        )
        
        if not articles:
            logger.warning(
                f"No articles found for category {category}",
                extra={"category": category}
            )
            return
        
        logger.info(
            f"Found {len(articles)} articles in {category}",
            extra={"category": category, "count": len(articles)}
        )
        
        for cat, article_path in articles:
            self._publish_article(cat, article_path, check_idempotency=True)
    
    def publish_single_article(
        self,
        category: str,
        file_name: str
    ) -> None:
        """
        Publish a single specific article.
        
        Args:
            category: Category name
            file_name: Article file name
        """
        article_path = (
            Path(self.article_base) /
            self.feed_date /
            category /
            file_name
        )
        
        if not article_path.exists():
            logger.error(
                f"Article not found: {article_path}",
                extra={"category": category, "file_name": file_name}
            )
            print(f"Error: Article not found: {article_path}")
            return
        
        self._publish_article(
            category,
            article_path,
            check_idempotency=False
        )
    
    def _publish_article(
        self,
        category: str,
        article_path: Path,
        check_idempotency: bool = True
    ) -> None:
        """
        Publish a single article with full process.
        
        Args:
            category: Article category
            article_path: Path to article file
            check_idempotency: Whether to check if already published
        """
        file_name = article_path.name
        
        try:
            # Check idempotency
            if check_idempotency:
                if check_already_published(
                    self.published_base,
                    self.feed_date,
                    category,
                    file_name
                ):
                    logger.info(
                        f"Skipping already published: {file_name}",
                        extra={"category": category, "file_name": file_name}
                    )
                    print(f"Skipping publishing `{file_name}` - already published")
                    return
            
            # Load article
            logger.info(
                f"Loading article: {file_name}",
                extra={"category": category, "file_name": file_name}
            )
            article = load_article(article_path, category)
            
            # Load image mapping
            image_mapping = None
            try:
                mapping_path = self._get_mapping_path(category, file_name)
                image_mapping = load_image_mapping(mapping_path)
                logger.debug(
                    f"Loaded image mapping: {mapping_path}",
                    extra={"file_name": file_name}
                )
            except ImageMappingError as e:
                logger.warning(
                    f"Image mapping not found: {e}",
                    extra={"file_name": file_name}
                )
            
            # Process content
            processed_content = process_article_content(
                article,
                image_mapping
            )
            
            # Validate content
            if not validate_processed_content(processed_content):
                raise PublishError(
                    f"Content validation failed for {file_name}"
                )
            
            # Publish to Hashnode
            logger.info(
                f"Publishing to Hashnode: {article.title}",
                extra={"category": category, "file_name": file_name}
            )
            
            response = self.client.publish_article(
                title=article.title,
                content=processed_content,
                publication_id=self.publication_id,
                tags=[]
            )
            
            # Check response
            if response.is_success:
                article_url = response.get_url() or ""
                status = "Success"
                
                logger.info(
                    f"Successfully published: {article.title}",
                    extra={
                        "category": category,
                        "file_name": file_name,
                        "url": article_url
                    }
                )
                print(f"✓ Published: {article.title}")
            else:
                article_url = ""
                status = "Fail"
                
                logger.error(
                    f"Failed to publish: {article.title}",
                    extra={
                        "category": category,
                        "file_name": file_name,
                        "errors": response.errors
                    }
                )
                print(f"✗ Failed: {article.title}")
            
            # Save result
            result = PublishResult(
                feed_date=self.feed_date,
                title=article.title,
                published_datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                category=category,
                article_url=article_url,
                status=status
            )
            
            save_publish_result(
                self.published_base,
                self.feed_date,
                category,
                file_name,
                result
            )
            
        except ArticleNotFoundError as e:
            logger.error(
                f"Article not found: {e}",
                extra={"category": category, "file_name": file_name}
            )
            print(f"✗ Error: {e}")
            
        except Exception as e:
            logger.error(
                f"Failed to publish article: {e}",
                exc_info=True,
                extra={"category": category, "file_name": file_name}
            )
            print(f"✗ Error publishing {file_name}: {e}")
    
    def _get_mapping_path(self, category: str, file_name: str) -> Path:
        """
        Get path to image URL mapping file.
        
        Args:
            category: Article category
            file_name: Article file name (with .md extension)
            
        Returns:
            Path to mapping file
        """
        json_file_name = file_name.replace('.md', '.json')
        
        return (
            Path(self.image_mapping_base) /
            self.feed_date /
            category /
            json_file_name
        )
