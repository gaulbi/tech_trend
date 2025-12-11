"""
Main processing logic for embedding pipeline.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .chunker import TextChunker
from .config import get_database_path, get_scrape_path
from .database import EmbeddingDatabase
from .embeddings.factory import EmbedderFactory
from .exceptions import ValidationError
from .logger import get_logger, log_execution_time


logger = get_logger(__name__)


class EmbeddingProcessor:
    """Processes scraped articles and generates embeddings."""
    
    def __init__(self, config: Dict[str, Any], feed_date: str):
        """
        Initialize the embedding processor.
        
        Args:
            config: Configuration dictionary
            feed_date: Feed date in YYYY-MM-DD format
        """
        self.config = config
        self.feed_date = feed_date
        
        # Initialize components
        self.chunker = TextChunker(
            chunk_size=config['embedding']['chunk-size'],
            chunk_overlap=config['embedding']['chunk-overlap']
        )
        
        self.embedder = EmbedderFactory.create(config)
        
        self.database = EmbeddingDatabase(
            get_database_path(config)
        )
        
        self.batch_size = config['embedding']['batch-size']
        
        logger.info(
            f"Processor initialized",
            extra={
                'extra_data': {
                    'feed_date': feed_date,
                    'embedding_provider': config['embedding'][
                        'embedding-provider'
                    ],
                    'embedding_model': config['embedding'][
                        'embedding-model'
                    ]
                }
            }
        )
    
    @log_execution_time
    def process_all_categories(self) -> None:
        """Process all categories found in the scrape directory."""
        scrape_path = get_scrape_path(self.config, self.feed_date)
        
        if not scrape_path.exists():
            logger.warning(
                f"No data found for date: {self.feed_date}",
                extra={'extra_data': {'path': str(scrape_path)}}
            )
            return
        
        categories = [
            d.name for d in scrape_path.iterdir() if d.is_dir()
        ]
        
        if not categories:
            logger.warning(
                f"No categories found in {scrape_path}",
                extra={'extra_data': {'path': str(scrape_path)}}
            )
            return
        
        logger.info(
            f"Found {len(categories)} categories to process",
            extra={'extra_data': {'categories': categories}}
        )
        
        for category in categories:
            try:
                self.process_category(category)
            except Exception as e:
                logger.error(
                    f"Failed to process category {category}: {e}",
                    exc_info=True
                )
        
        # Log final database stats
        stats = self.database.get_stats()
        logger.info(
            "All categories processed",
            extra={'extra_data': stats}
        )
    
    @log_execution_time
    def process_category(self, category: str) -> None:
        """
        Process a single category.
        
        Args:
            category: Category name to process
        """
        logger.info(f"Processing category: {category}")
        
        scrape_path = get_scrape_path(self.config, self.feed_date)
        category_path = scrape_path / category
        
        if not category_path.exists():
            logger.warning(f"Category path does not exist: {category_path}")
            return
        
        # Find all JSON files
        json_files = list(category_path.glob("*.json"))
        
        if not json_files:
            logger.warning(
                f"No JSON files found in {category_path}",
                extra={'extra_data': {'path': str(category_path)}}
            )
            return
        
        logger.info(
            f"Found {len(json_files)} JSON files in {category}",
            extra={
                'extra_data': {
                    'category': category,
                    'file_count': len(json_files)
                }
            }
        )
        
        total_processed = 0
        total_skipped = 0
        
        for json_file in json_files:
            try:
                processed, skipped = self._process_file(
                    json_file,
                    category
                )
                total_processed += processed
                total_skipped += skipped
            except ValidationError as e:
                logger.error(
                    f"Validation error in {json_file.name}: {e}"
                )
            except Exception as e:
                logger.error(
                    f"Error processing {json_file.name}: {e}",
                    exc_info=True
                )
        
        logger.info(
            f"Category {category} complete: "
            f"{total_processed} processed, {total_skipped} skipped",
            extra={
                'extra_data': {
                    'category': category,
                    'processed': total_processed,
                    'skipped': total_skipped
                }
            }
        )
    
    def _process_file(
        self,
        file_path: Path,
        category: str
    ) -> Tuple[int, int]:
        """
        Process a single JSON file.
        
        Args:
            file_path: Path to JSON file
            category: Category name
            
        Returns:
            Tuple of (processed_count, skipped_count)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")
        except Exception as e:
            raise ValidationError(f"Error reading file: {e}")
        
        # Validate structure
        if 'trends' not in data:
            raise ValidationError("Missing 'trends' field in JSON")
        
        if not isinstance(data['trends'], list):
            raise ValidationError("'trends' must be a list")
        
        processed = 0
        skipped = 0
        
        for idx, trend in enumerate(data['trends']):
            # Validate trend is a dictionary
            if not isinstance(trend, dict):
                logger.warning(
                    f"Skipping non-dict trend at index {idx}",
                    extra={'extra_data': {'file': str(file_path)}}
                )
                continue
            
            try:
                # Validate required fields
                self._validate_trend(trend)
                
                # Check if already embedded (idempotency)
                url = trend['search_link']
                
                if self.database.check_exists(
                    url,
                    category,
                    self.feed_date
                ):
                    logger.debug(
                        f"Skipping existing: {url[:50]}...",
                        extra={
                            'extra_data': {
                                'url': url,
                                'category': category
                            }
                        }
                    )
                    skipped += 1
                    continue
                
                # Process new trend
                if self._process_trend(trend, category, str(file_path)):
                    processed += 1
                
            except ValidationError as e:
                logger.warning(
                    f"Validation error in trend: {e}",
                    extra={'extra_data': {'trend_index': idx}}
                )
            except Exception as e:
                logger.error(
                    f"Error processing trend: {e}",
                    extra={
                        'extra_data': {
                            'trend': trend.get('topic', 'N/A'),
                            'trend_index': idx
                        }
                    }
                )
        
        return processed, skipped
    
    def _validate_trend(self, trend: Dict[str, Any]) -> None:
        """
        Validate trend structure and required fields.
        
        Args:
            trend: Trend dictionary to validate
            
        Raises:
            ValidationError: If validation fails
        """
        required_fields = {
            'topic': str,
            'query_used': str,
            'search_link': str,
            'content': str
        }
        
        for field, expected_type in required_fields.items():
            if field not in trend:
                raise ValidationError(f"Missing required field: '{field}'")
            
            if not isinstance(trend[field], expected_type):
                raise ValidationError(
                    f"Field '{field}' must be {expected_type.__name__}, "
                    f"got {type(trend[field]).__name__}"
                )
            
            # Check for empty strings
            if expected_type == str and not trend[field].strip():
                raise ValidationError(
                    f"Field '{field}' cannot be empty or whitespace"
                )
    
    def _process_trend(
        self,
        trend: Dict[str, Any],
        category: str,
        source_file: str
    ) -> bool:
        """
        Process a single trend: chunk, embed, and store.
        
        Args:
            trend: Trend dictionary
            category: Category name
            source_file: Source file path
            
        Returns:
            True if successful, False otherwise
        """
        content = trend['content'].strip()
        url = trend['search_link'].strip()
        
        # Chunk text
        chunks = self.chunker.chunk_text(content)
        
        if not chunks:
            logger.debug("Skipping trend: no chunks generated")
            return False
        
        # Generate embeddings in batches
        all_embeddings = []
        
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            
            try:
                embeddings = self.embedder.embed_with_retry(batch)
                all_embeddings.extend(embeddings)
            except Exception as e:
                logger.error(
                    f"Failed to generate embeddings: {e}",
                    extra={'extra_data': {'url': url}}
                )
                return False
        
        # Verify we got all embeddings
        if len(all_embeddings) != len(chunks):
            logger.error(
                f"Embedding count mismatch: "
                f"{len(all_embeddings)} != {len(chunks)}",
                extra={'extra_data': {'url': url}}
            )
            return False
        
        # Store in database
        metadata = {
            'url': url,
            'category': category,
            'embedding_date': self.feed_date,
            'source_file': source_file
        }
        
        try:
            self.database.add_embeddings(chunks, all_embeddings, metadata)
            
            logger.info(
                f"Embedded article: {trend['topic'][:50]}",
                extra={
                    'extra_data': {
                        'url': url[:50],
                        'chunk_count': len(chunks),
                        'category': category
                    }
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Failed to store embeddings: {e}",
                extra={'extra_data': {'url': url}}
            )
            return False