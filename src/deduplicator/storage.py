"""
Vector database storage using ChromaDB.
"""
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.config import Settings

from .exceptions import DatabaseError
from .logger import get_logger
from .models import TechTrend, DuplicateMatch


logger = get_logger(__name__)


class HistoryDatabase:
    """ChromaDB-based history storage for tech trends."""
    
    def __init__(
        self,
        persist_path: Path,
        collection_name: str,
        similarity_threshold: float,
        lookback_days: int,
    ):
        """
        Initialize history database.
        
        Args:
            persist_path: Path for ChromaDB persistence
            collection_name: Name of the collection
            similarity_threshold: Cosine similarity threshold
            lookback_days: Number of days to look back
        """
        self.persist_path = persist_path
        self.collection_name = collection_name
        self.similarity_threshold = similarity_threshold
        self.lookback_days = lookback_days
        
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            self.persist_path.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=str(self.persist_path),
                settings=Settings(anonymized_telemetry=False),
            )
            
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            
            logger.info(
                f"Initialized ChromaDB at {self.persist_path}"
            )
            
        except Exception as e:
            raise DatabaseError(
                f"Failed to initialize database: {e}"
            )
    
    def _generate_id(
        self,
        date: str,
        category: str,
        topic: str,
    ) -> str:
        """
        Generate deterministic ID for a trend.
        
        Args:
            date: Feed date
            category: Category name
            topic: Topic string
            
        Returns:
            Unique ID string
        """
        topic_hash = hashlib.md5(
            topic.encode("utf-8")
        ).hexdigest()[:8]
        return f"{date}|{category}|{topic_hash}"
    
    def _date_to_timestamp(self, date_str: str) -> int:
        """
        Convert date string to Unix timestamp.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            Unix timestamp as integer
        """
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return int(dt.timestamp())
    
    def _get_cutoff_timestamp(self, reference_date: str) -> int:
        """
        Calculate cutoff timestamp for lookback period.
        
        Args:
            reference_date: Reference date (YYYY-MM-DD)
            
        Returns:
            Cutoff timestamp as integer
        """
        ref_dt = datetime.strptime(reference_date, "%Y-%m-%d")
        cutoff_dt = ref_dt - timedelta(days=self.lookback_days)
        return int(cutoff_dt.timestamp())
    
    def check_duplicate(
        self,
        trend: TechTrend,
        embedding: List[float],
        feed_date: str,
    ) -> Optional[DuplicateMatch]:
        """
        Check if trend is duplicate.
        
        Args:
            trend: Tech trend to check
            embedding: Embedding vector
            feed_date: Feed date for lookback calculation
            
        Returns:
            DuplicateMatch if duplicate found, None otherwise
        """
        try:
            cutoff_timestamp = self._get_cutoff_timestamp(feed_date)
            
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=1,
                where={"date_timestamp": {"$gt": cutoff_timestamp}},
            )
            
            # Check if results are empty
            if (not results["ids"] or 
                not results["ids"][0] or 
                not results["distances"] or
                not results["distances"][0]):
                return None
            
            # ChromaDB returns cosine distance (0 = identical, 2 = opposite)
            # Convert to similarity (1 = identical, 0 = completely different)
            distance = results["distances"][0][0]
            similarity = 1 - (distance / 2)
            
            if similarity > self.similarity_threshold:
                metadata = results["metadatas"][0][0]
                return DuplicateMatch(
                    matched_topic=metadata["topic"],
                    matched_date=metadata["date"],
                    similarity_score=similarity,
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking duplicate: {e}", exc_info=True)
            raise DatabaseError(f"Failed to check duplicate: {e}")
    
    def add_trend(
        self,
        trend: TechTrend,
        embedding: List[float],
        feed_date: str,
        category: str,
    ) -> None:
        """
        Add trend to history database.
        
        Args:
            trend: Tech trend to add
            embedding: Embedding vector
            feed_date: Feed date
            category: Category name
        """
        try:
            trend_id = self._generate_id(
                feed_date,
                category,
                trend.topic,
            )
            
            document = trend.get_embedding_text()
            keywords = ", ".join(trend.search_keywords)
            date_timestamp = self._date_to_timestamp(feed_date)
            
            metadata = {
                "topic": trend.topic,
                "date": feed_date,  # Keep human-readable format
                "date_timestamp": date_timestamp,  # For filtering
                "keywords": keywords,
                "category": category,
            }
            
            self.collection.add(
                ids=[trend_id],
                documents=[document],
                embeddings=[embedding],
                metadatas=[metadata],
            )
            
            logger.debug(
                f"Added trend to history: {trend.topic} ({trend_id})"
            )
            
        except Exception as e:
            logger.error(f"Error adding trend: {e}", exc_info=True)
            raise DatabaseError(f"Failed to add trend: {e}")
    
    def get_stats(self) -> dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with count and sample data
        """
        try:
            count = self.collection.count()
            return {"total_trends": count}
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_trends": 0, "error": str(e)}
