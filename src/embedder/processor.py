"""Main processing orchestration for embedding pipeline."""

import logging
from pathlib import Path
from typing import Dict, List

from .chunker import TextChunker
from .config import Config
from .database import ChromaDatabase
from .embedders.factory import EmbedderFactory
from .exceptions import ValidationError
from .utils import (
    batch_list,
    find_category_directories,
    hash_url,
    load_json_file,
    validate_trend_item,
)

logger = logging.getLogger(__name__)


class EmbeddingProcessor:
    """Orchestrates the embedding pipeline."""

    def __init__(self, config: Config, target_date: str) -> None:
        """
        Initialize embedding processor.

        Args:
            config: Configuration object.
            target_date: Date to process in YYYY-MM-DD format.
        """
        self.config = config
        self.target_date = target_date

        # Initialize components
        self.chunker = TextChunker(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )

        self.embedder = EmbedderFactory.create(
            provider=config.embedding_provider,
            model=config.embedding_model,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

        self.database = ChromaDatabase(config.database_path, config.collection_name)

        logger.info(
            f"Initialized processor with {config.embedding_provider} "
            f"model {config.embedding_model}"
        )

    def process(self) -> Dict[str, int]:
        """
        Process all categories for the target date.

        Returns:
            Dictionary with success, skipped, and failed counts.
        """
        base_path = Path(self.config.scraped_content_path)
        categories = find_category_directories(base_path, self.target_date)

        if not categories:
            logger.warning(
                f"No categories found for date {self.target_date}"
            )
            return {"success": 0, "skipped": 0, "failed": 0}

        logger.info(f"Found {len(categories)} categories to process")

        stats = {"success": 0, "skipped": 0, "failed": 0}

        for category_dir in categories:
            category_stats = self._process_category(category_dir)
            for key in stats:
                stats[key] += category_stats[key]

        return stats

    def _process_category(self, category_dir: Path) -> Dict[str, int]:
        """
        Process all JSON files in a category directory.

        Args:
            category_dir: Path to category directory.

        Returns:
            Processing statistics.
        """
        category_name = category_dir.name
        logger.info(f"Processing category: {category_name}")

        stats = {"success": 0, "skipped": 0, "failed": 0}
        json_files = list(category_dir.glob("*.json"))

        if not json_files:
            logger.warning(f"No JSON files in {category_dir}")
            return stats

        for json_file in json_files:
            file_stats = self._process_file(json_file, category_name)
            for key in stats:
                stats[key] += file_stats[key]

        logger.info(
            f"Category {category_name} complete: "
            f"Success={stats['success']}, "
            f"Skipped={stats['skipped']}, "
            f"Failed={stats['failed']}"
        )

        return stats

    def _process_file(
        self, file_path: Path, category: str
    ) -> Dict[str, int]:
        """
        Process a single JSON file.

        Args:
            file_path: Path to JSON file.
            category: Category name.

        Returns:
            Processing statistics.
        """
        stats = {"success": 0, "skipped": 0, "failed": 0}

        try:
            data = load_json_file(file_path)
        except ValidationError as e:
            logger.error(f"Validation error in {file_path}: {e}")
            stats["failed"] += 1
            return stats

        for trend in data["trends"]:
            if not validate_trend_item(trend, file_path):
                stats["failed"] += 1
                continue

            url = trend["link"]

            # Check idempotency
            if self.database.url_exists(
                url, category, self.target_date
            ):
                logger.debug(f"Skipping existing URL: {url}")
                stats["skipped"] += 1
                continue

            # Process the article
            try:
                self._process_article(trend, category, file_path)
                stats["success"] += 1
            except Exception as e:
                logger.error(f"Failed to process {url}: {e}")
                stats["failed"] += 1

        return stats

    def _process_article(
        self, trend: Dict, category: str, source_file: Path
    ) -> None:
        """
        Process a single article: chunk, embed, and store.

        Args:
            trend: Trend data dictionary.
            category: Category name.
            source_file: Source JSON file path.
        """
        url = trend["link"]
        content = trend["content"]

        # Chunk the content
        chunks = self.chunker.chunk(content)
        if not chunks:
            logger.warning(f"No chunks generated for {url}")
            return

        # Process in batches
        batch_size = self.config.batch_size
        for batch_idx, chunk_batch in enumerate(
            batch_list(chunks, batch_size)
        ):
            self._process_chunk_batch(
                chunk_batch, batch_idx, url, category, source_file
            )

        logger.info(
            f"Processed {len(chunks)} chunks for {url}"
        )

    def _process_chunk_batch(
        self,
        chunks: List[str],
        batch_start_idx: int,
        url: str,
        category: str,
        source_file: Path,
    ) -> None:
        """
        Process a batch of chunks: embed and store.

        Args:
            chunks: List of text chunks.
            batch_start_idx: Starting index for this batch.
            url: Article URL.
            category: Category name.
            source_file: Source file path.
        """
        # Generate embeddings
        embeddings = self.embedder.embed(chunks)

        # Prepare data for database
        url_hash = hash_url(url)
        batch_size = self.config.batch_size

        ids = []
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_idx = batch_start_idx * batch_size + i
            chunk_id = (
                f"{category}|{self.target_date}|"
                f"{url_hash}|chunk_{chunk_idx}"
            )
            ids.append(chunk_id)

            metadata = {
                "url": url,
                "category": category,
                "embedding_date": self.target_date,
                "source_file": str(source_file),
                "chunk_index": str(chunk_idx),
            }
            metadatas.append(metadata)

        # Store in database
        self.database.add_chunks(ids, chunks, embeddings, metadatas)