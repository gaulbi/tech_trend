"""
ChromaDB database operations.
"""

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import chromadb
from chromadb.config import Settings

from .exceptions import DatabaseError
from .logger import get_logger


logger = get_logger(__name__)


class EmbeddingDatabase:
    """Manages ChromaDB operations for embeddings."""
    
    def __init__(self, database_path: Path, collection_name: str):
        """
        Initialize ChromaDB client.
        
        Args:
            database_path: Path to ChromaDB persistence directory
            
        Raises:
            DatabaseError: If database initialization fails
        """
        try:
            database_path.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=str(database_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create collection without embedding function
            # (we provide embeddings manually)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(
                f"Database initialized at {database_path}",
                extra={
                    'extra_data': {
                        'collection_count': self.collection.count()
                    }
                }
            )
            
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {e}")
    
    def check_exists(
        self,
        url: str,
        category: str,
        embedding_date: str
    ) -> bool:
        """
        Check if embeddings exist for given URL, category, and date.
        
        Args:
            url: Article URL
            category: Article category
            embedding_date: Embedding date
            
        Returns:
            True if embeddings exist, False otherwise
        """
        try:
            # FIXED: Must use $and with explicit $eq operators
            # for multiple conditions in ChromaDB
            results = self.collection.get(
                where={
                    "$and": [
                        {"url": {"$eq": url}},
                        {"category": {"$eq": category}},
                        {"embedding_date": {"$eq": embedding_date}}
                    ]
                },
                limit=1
            )
            
            exists = len(results['ids']) > 0
            
            if exists:
                logger.debug(
                    f"Embeddings exist for URL: {url[:50]}...",
                    extra={
                        'extra_data': {
                            'url': url,
                            'category': category,
                            'embedding_date': embedding_date
                        }
                    }
                )
            
            return exists
            
        except Exception as e:
            logger.warning(f"Error checking existence: {e}")
            return False
    
    def add_embeddings(
        self,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Add embeddings to the database.
        
        Args:
            chunks: List of text chunks
            embeddings: List of embedding vectors
            metadata: Metadata for the embeddings
            
        Raises:
            DatabaseError: If insertion fails
        """
        if len(chunks) != len(embeddings):
            raise DatabaseError(
                f"Chunk count ({len(chunks)}) != "
                f"embedding count ({len(embeddings)})"
            )
        
        try:
            # Generate unique IDs
            url_hash = self._hash_url(metadata['url'])
            ids = [
                f"{metadata['category']}|{metadata['embedding_date']}|"
                f"{url_hash}|chunk_{i}"
                for i in range(len(chunks))
            ]
            
            # Create metadata for each chunk
            # Note: ChromaDB metadata only supports str, int, float, bool
            metadatas = [
                {
                    'url': str(metadata['url']),
                    'category': str(metadata['category']),
                    'embedding_date': str(metadata['embedding_date']),
                    'source_file': str(metadata['source_file']),
                    'chunk_index': int(i)
                }
                for i in range(len(chunks))
            ]
            
            # Add to database with explicit embeddings
            self.collection.add(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.debug(
                f"Added {len(chunks)} chunks to database",
                extra={
                    'extra_data': {
                        'url': metadata['url'][:50],
                        'chunk_count': len(chunks)
                    }
                }
            )
            
        except Exception as e:
            raise DatabaseError(f"Failed to add embeddings: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            total_count = self.collection.count()
            
            return {
                'total_embeddings': total_count,
                'collection_name': self.collection.name
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'total_embeddings': 0,
                'collection_name': 'unknown'
            }
    
    @staticmethod
    def _hash_url(url: str) -> str:
        """
        Generate a hash for a URL.
        
        Args:
            url: URL to hash
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.md5(url.encode()).hexdigest()[:16]