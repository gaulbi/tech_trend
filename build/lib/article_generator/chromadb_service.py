"""
ChromaDB Service Module

Handles similarity search operations with ChromaDB.
"""

import logging
from typing import List, Dict, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings

from src.article_generator.config_loader import Config
from src.article_generator.embedding_client_base import EmbeddingClientFactory

logger = logging.getLogger(__name__)


class ChromaDBService:
    """Service for interacting with ChromaDB."""
    
    def __init__(self, config: Config):
        """
        Initialize ChromaDB service.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.db_path = Path(config.embedding.database_path)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding client
        api_key = self._get_embedding_api_key()
        self.embedding_client = EmbeddingClientFactory.create_client(
            provider=config.embedding.provider,
            model=config.embedding.model,
            api_key=api_key,
            timeout=config.embedding.timeout,
            max_retries=config.embedding.max_retries
        )
        
        logger.info(f"ChromaDB initialized at: {self.db_path}")
    
    def _get_embedding_api_key(self) -> str:
        """Get API key for embedding provider."""
        provider = self.config.embedding.provider.lower()
        
        if provider == 'sentence-transformers':
            return None
        
        api_key = self.config.api_keys.get(provider)
        if not api_key and provider != 'sentence-transformers':
            raise ValueError(
                f"API key not found for embedding provider: {provider}"
            )
        
        return api_key
    
    def similarity_search(
        self,
        query_text: str,
        category: str,
        embedding_date: str,
        k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search in ChromaDB.
        
        Args:
            query_text: Text to search for (from analysis 'reason' field)
            category: Category filter (e.g., "AI / Machine Learning")
            embedding_date: Date filter in YYYY-MM-DD format
            k: Number of results to return
            
        Returns:
            List of matching documents with metadata
            
        Raises:
            Exception: If search fails
        """
        try:
            # Convert category to collection name format
            # IMPORTANT: Replace '/' first, then spaces to avoid triple dashes
            # "AI / Machine Learning" → "ai-machine-learning" (not "ai---machine-learning")
            collection_name = category.lower().replace('/', '-').replace(' ', '-')
            
            logger.info(f"Searching collection: {collection_name}")
            logger.info(f"Category filter: {category}")
            logger.info(f"Date filter: {embedding_date}")
            logger.info(f"Query: {query_text[:100]}...")
            
            # Get or create collection
            try:
                collection = self.client.get_collection(name=collection_name)
                logger.info(f"Collection '{collection_name}' found with {collection.count()} documents")
            except Exception as e:
                logger.warning(f"Collection '{collection_name}' not found: {e}")
                return []
            
            # Generate query embedding
            logger.info("Generating query embedding...")
            query_embedding = self.embedding_client.embed_query_with_retry(query_text)
            
            # Build metadata filter - ChromaDB uses exact matching for metadata
            where_filter = {
                "$and": [
                    {"category": category},
                    {"embedding_date": embedding_date}
                ]
            }
            
            logger.info(f"Using filter: {where_filter}")
            
            # Perform similarity search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where_filter
            )
            
            # Format results
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        'document': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })
            
            logger.info(f"Found {len(documents)} matching documents")
            
            # If no results with date filter, try without date filter
            if len(documents) == 0:
                logger.warning(f"No results with date filter, trying without date...")
                where_filter_no_date = {"category": category}
                
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    where=where_filter_no_date
                )
                
                if results['documents'] and results['documents'][0]:
                    for i, doc in enumerate(results['documents'][0]):
                        documents.append({
                            'document': doc,
                            'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                            'distance': results['distances'][0][i] if results['distances'] else None
                        })
                    logger.info(f"Found {len(documents)} documents without date filter")
            
            return documents
        
        except Exception as e:
            logger.error(f"Similarity search failed: {e}", exc_info=True)
            # Return empty list instead of raising - allows processing to continue
            return []