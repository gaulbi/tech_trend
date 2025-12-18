"""
Core deduplication pipeline implementation.
"""
from datetime import date, datetime
from typing import List, Optional

from .config import Config
from .embeddings import EmbeddingFactory, EmbeddingProvider
from .exceptions import ValidationError
from .io_handler import IOHandler
from .logger import get_logger, log_execution
from .models import TechTrend, TrendAnalysis
from .storage import HistoryDatabase


logger = get_logger(__name__)


class Deduplicator:
    """Handles deduplication logic for a single category."""
    
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        history_db: HistoryDatabase,
        target_count: int,
    ):
        """
        Initialize deduplicator.
        
        Args:
            embedding_provider: Provider for generating embeddings
            history_db: History database instance
            target_count: Number of unique trends to return
        """
        self.embedding_provider = embedding_provider
        self.history_db = history_db
        self.target_count = target_count
    
    @log_execution
    def deduplicate(
        self,
        analysis: TrendAnalysis,
    ) -> TrendAnalysis:
        """
        Deduplicate trends from analysis.
        
        Args:
            analysis: Input trend analysis
            
        Returns:
            TrendAnalysis with deduplicated trends
        """
        sorted_trends = analysis.get_sorted_trends()
        selected_trends: List[TechTrend] = []
        
        if not sorted_trends:
            logger.warning(
                f"No trends found in {analysis.category}"
            )
            return TrendAnalysis(
                feed_date=analysis.feed_date,
                category=analysis.category,
                trends=[],
            )
        
        logger.info(
            f"Starting deduplication for {analysis.category} "
            f"({len(sorted_trends)} trends)"
        )
        
        for trend in sorted_trends:
            if len(selected_trends) >= self.target_count:
                break
            
            if self._is_unique(trend, analysis.feed_date):
                selected_trends.append(trend)
                logger.info(
                    f"Selected: '{trend.topic}' "
                    f"(Score: {trend.score})"
                )
            else:
                logger.debug(
                    f"Skipped duplicate: '{trend.topic}'"
                )
        
        logger.info(
            f"Selected {len(selected_trends)} unique trends"
        )
        
        return TrendAnalysis(
            feed_date=analysis.feed_date,
            category=analysis.category,
            trends=selected_trends,
        )
    
    def _is_unique(
        self,
        trend: TechTrend,
        feed_date: str,
    ) -> bool:
        """
        Check if trend is unique.
        
        Args:
            trend: Trend to check
            feed_date: Feed date
            
        Returns:
            True if unique, False if duplicate
        """
        try:
            text = trend.get_embedding_text()
            embedding = self.embedding_provider.generate_embedding(text)
            
            duplicate = self.history_db.check_duplicate(
                trend,
                embedding,
                feed_date,
            )
            
            if duplicate:
                logger.debug(
                    f"Duplicate found: '{trend.topic}' matches "
                    f"{duplicate}"
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(
                f"Error checking uniqueness for '{trend.topic}': {e}",
                exc_info=True,
            )
            # On error, treat as unique to avoid losing potentially 
            # good content
            logger.warning(
                f"Treating '{trend.topic}' as unique due to error"
            )
            return True
    
    @log_execution
    def record_trends(
        self,
        analysis: TrendAnalysis,
    ) -> None:
        """
        Record selected trends to history database.
        
        Args:
            analysis: Analysis with trends to record
        """
        if not analysis.trends:
            logger.warning("No trends to record")
            return
            
        logger.info(
            f"Recording {len(analysis.trends)} trends to history"
        )
        
        for trend in analysis.trends:
            try:
                text = trend.get_embedding_text()
                embedding = self.embedding_provider.generate_embedding(
                    text
                )
                
                self.history_db.add_trend(
                    trend,
                    embedding,
                    analysis.feed_date,
                    analysis.category,
                )
            except Exception as e:
                logger.error(
                    f"Failed to record trend '{trend.topic}': {e}",
                    exc_info=True,
                )
                # Continue with other trends
                continue
        
        logger.info("Completed recording trends")


class DeduplicationPipeline:
    """Main pipeline for running deduplication."""
    
    def __init__(self, config: Config):
        """
        Initialize pipeline.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.io_handler = IOHandler(
            config.analysis_report_path,
            config.dedup_report_path,
            config.org_analysis_report_path,
        )
        self.embedding_provider = EmbeddingFactory.create(
            config.embedding_provider,
            config.embedding_model,
            config.timeout,
            config.max_retries,
        )
        self.history_db = HistoryDatabase(
            config.history_keywords_path,
            config.collection_name,
            config.similarity_threshold,
            config.lookback_days,
        )
        self.deduplicator = Deduplicator(
            self.embedding_provider,
            self.history_db,
            config.target_count,
        )
    
    def _get_feed_date(
        self,
        feed_date: Optional[str],
    ) -> str:
        """
        Get feed date (use provided or today).
        
        Args:
            feed_date: Optional feed date
            
        Returns:
            Feed date in YYYY-MM-DD format
            
        Raises:
            ValueError: If date format is invalid
        """
        if feed_date:
            # Validate date format
            try:
                datetime.strptime(feed_date, "%Y-%m-%d")
                return feed_date
            except ValueError:
                raise ValueError(
                    f"Invalid date format: {feed_date}. "
                    "Expected YYYY-MM-DD"
                )
        return date.today().strftime("%Y-%m-%d")
    
    @log_execution
    def run(
        self,
        feed_date: Optional[str] = None,
        category: Optional[str] = None,
    ) -> None:
        """
        Run deduplication pipeline.
        
        Args:
            feed_date: Optional feed date (default: today)
            category: Optional specific category to process
        """
        feed_date = self._get_feed_date(feed_date)
        logger.info(f"Running pipeline for date: {feed_date}")
        
        if category:
            categories = [category]
        else:
            categories = self.io_handler.get_available_categories(
                feed_date
            )
        
        if not categories:
            logger.warning(f"No categories found for {feed_date}")
            return
        
        for cat in categories:
            try:
                self._process_category(feed_date, cat)
            except ValidationError as e:
                logger.error(
                    f"Validation error for {cat}: {e}. "
                    "Continuing with next category."
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error processing {cat}: {e}",
                    exc_info=True,
                )
                continue
    
    @log_execution
    def _process_category(
        self,
        feed_date: str,
        category: str,
    ) -> None:
        """
        Process a single category.
        
        Args:
            feed_date: Feed date
            category: Category name
        """
        logger.info(f"Processing category: {category}")
        
        # Check idempotency
        if self.io_handler.output_exists(feed_date, category):
            logger.info(
                f"Output already exists for {category}. Skipping..."
            )
            print(f"Skipping {category} - already processed")
            return
        
        # Read input
        analysis = self.io_handler.read_analysis(feed_date, category)
        if not analysis:
            logger.warning(
                f"No input found for {category}"
            )
            return
        
        # Deduplicate
        deduplicated = self.deduplicator.deduplicate(analysis)
        
        # Write output
        self.io_handler.write_analysis(deduplicated)
        
        # Record to history
        self.deduplicator.record_trends(deduplicated)
        
        # Rotate files
        self.io_handler.rotate_files(feed_date, category)
        
        logger.info(f"Completed processing for {category}")
