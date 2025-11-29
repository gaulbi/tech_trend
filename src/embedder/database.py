"""ChromaDB database operations with idempotency checks."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

import chromadb
from chromadb.config import Settings

from .exceptions import DatabaseError

logger = logging.getLogger(__name__)


class ChromaDatabase:
    """ChromaDB wrapper with idempotency support."""

    COLLECTION_NAME = "embeddings"

    def __init__(self, database_path: str) -> None:
        """
        Initialize ChromaDB client.

        Args:
            database_path: Path to ChromaDB storage directory.

        Raises:
            DatabaseError: If initialization fails.
        """
        try:
            Path(database_path).mkdir(parents=True, exist_ok=True)

            self.client = chromadb.PersistentClient(
                path=database_path,
                settings=Settings(anonymized_telemetry=False),
            )

            self.collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )

            logger.info(f"Connected to ChromaDB at {database_path}")
        except Exception as e:
            raise DatabaseError(
                f"Failed to initialize ChromaDB: {e}"
            ) from e

    def url_exists(
        self, url: str, category: str, embedding_date: str
    ) -> bool:
        """
        Check if URL already exists in database.

        Args:
            url: Article URL to check.
            category: Article category.
            embedding_date: Target date for embeddings.

        Returns:
            True if URL exists for this date/category combination.
        """
        try:
            results = self.collection.get(
                where={
                    "$and": [
                        {"url": url},
                        {"category": category},
                        {"embedding_date": embedding_date},
                    ]
                },
                limit=1,
            )
            return len(results["ids"]) > 0
        except Exception as e:
            logger.warning(f"Error checking URL existence: {e}")
            return False

    def add_chunks(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, str]],
    ) -> None:
        """
        Add document chunks to database.

        Args:
            ids: List of unique chunk IDs.
            documents: List of text chunks.
            embeddings: List of embedding vectors.
            metadatas: List of metadata dictionaries.

        Raises:
            DatabaseError: If insertion fails.
        """
        if not ids:
            return

        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            logger.debug(f"Added {len(ids)} chunks to database")
        except Exception as e:
            raise DatabaseError(f"Failed to add chunks: {e}") from e

    def get_existing_urls(
        self, category: str, embedding_date: str
    ) -> Set[str]:
        """
        Get all URLs already processed for a category and date.

        Args:
            category: Article category.
            embedding_date: Target date.

        Returns:
            Set of URLs already in database.
        """
        try:
            results = self.collection.get(
                where={
                    "$and": [
                        {"category": category},
                        {"embedding_date": embedding_date},
                    ]
                }
            )

            urls = set()
            if results and results["metadatas"]:
                urls = {meta["url"] for meta in results["metadatas"]}

            return urls
        except Exception as e:
            logger.warning(f"Error fetching existing URLs: {e}")
            return set()

    def get_collection_count(self) -> int:
        """
        Get total number of documents in collection.

        Returns:
            Document count.
        """
        try:
            return self.collection.count()
        except Exception:
            return 0