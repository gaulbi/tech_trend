"""RAG retrieval using ChromaDB with corrected filter syntax."""
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.errors import ChromaError
from ..clients.base import BaseEmbeddingClient
from ..exceptions import RAGError


class RAGRetriever:
    """RAG retriever using ChromaDB with comprehensive error handling."""
    
    def __init__(
        self,
        embedding_client: BaseEmbeddingClient,
        database_path: str,
        collection_name: str,
        logger: Optional[Any] = None
    ):
        """
        Initialize RAG retriever.
        
        Args:
            embedding_client: Embedding client
            database_path: Path to ChromaDB database
            collection_name: Collection name
            logger: Optional logger instance
            
        Raises:
            RAGError: If ChromaDB initialization fails
        """
        self.embedding_client = embedding_client
        self.logger = logger
        
        db_path = Path(database_path)
        db_path.mkdir(parents=True, exist_ok=True)
        
        try:
            self.client = chromadb.PersistentClient(path=str(db_path))
            self.collection = self.client.get_or_create_collection(
                name=collection_name
            )
            
            # Validate collection has data
            count = self.collection.count()
            if self.logger:
                self.logger.info(
                    f"ChromaDB collection '{collection_name}' loaded "
                    f"with {count} documents"
                )
            
            if count == 0:
                if self.logger:
                    self.logger.warning(
                        f"ChromaDB collection '{collection_name}' is empty. "
                        f"RAG retrieval will return no results."
                    )
        
        except ChromaError as e:
            raise RAGError(
                f"Failed to initialize ChromaDB: {str(e)}. "
                f"Check if database is locked or corrupted."
            )
        except Exception as e:
            raise RAGError(f"Unexpected error initializing ChromaDB: {str(e)}")
    
    def retrieve(
        self,
        search_keywords: List[str],
        category: str,
        feed_date: str,
        k_top: int = 20
    ) -> str:
        """
        Retrieve relevant chunks with comprehensive error handling.
        
        Args:
            search_keywords: Keywords to search
            category: Category filter
            feed_date: Feed date filter
            k_top: Number of results to retrieve
            
        Returns:
            Aggregated context string (empty if no results)
            
        Raises:
            RAGError: If retrieval fails critically
        """
        if not search_keywords:
            if self.logger:
                self.logger.warning("No search keywords provided for RAG")
            return ""
        
        try:
            # Generate embeddings for each keyword
            embeddings = []
            for keyword in search_keywords:
                try:
                    emb = self.embedding_client.embed_single(keyword)
                    embeddings.append(emb)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(
                            f"Failed to embed keyword '{keyword}': {str(e)}"
                        )
            
            if not embeddings:
                if self.logger:
                    self.logger.warning(
                        "All keyword embeddings failed, returning empty context"
                    )
                return ""
            
            # Average embeddings
            query_embedding = np.mean(embeddings, axis=0).tolist()
            
            # CORRECTED: ChromaDB filter syntax with $and operator
            where_filter = {
                "$and": [
                    {"category": {"$eq": category}},
                    {"embedding_date": {"$eq": feed_date}}
                ]
            }
            
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k_top,
                    where=where_filter
                )
            except Exception as e:
                # Fallback 1: Try with simplified filter
                if self.logger:
                    self.logger.warning(
                        f"Filtered query with $and failed ({str(e)}), "
                        f"trying simplified filter"
                    )
                
                try:
                    # Try just category filter
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=k_top,
                        where={"category": {"$eq": category}}
                    )
                except Exception as e2:
                    # Fallback 2: Try without any filters
                    if self.logger:
                        self.logger.warning(
                            f"Category filter failed ({str(e2)}), "
                            f"trying without filters"
                        )
                    
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=k_top
                    )
            
            # Validate and aggregate documents
            if not results or not results.get('documents'):
                if self.logger:
                    self.logger.warning(
                        f"No RAG results found for category='{category}', "
                        f"feed_date='{feed_date}'"
                    )
                return ""
            
            documents = results['documents'][0] if results['documents'] else []
            
            if not documents:
                if self.logger:
                    self.logger.warning(
                        f"Empty RAG results for category='{category}', "
                        f"feed_date='{feed_date}'"
                    )
                return ""
            
            # Filter by metadata if query didn't do it
            if results.get('metadatas') and results['metadatas'][0]:
                filtered_docs = []
                for doc, metadata in zip(
                    documents,
                    results['metadatas'][0]
                ):
                    # Check if metadata matches our filters
                    if (metadata.get('category') == category and 
                        metadata.get('embedding_date') == feed_date):
                        filtered_docs.append(doc)
                
                if filtered_docs:
                    documents = filtered_docs
                    if self.logger:
                        self.logger.debug(
                            f"Filtered to {len(documents)} docs matching criteria"
                        )
                else:
                    if self.logger:
                        self.logger.warning(
                            f"No documents matched filters after retrieval. "
                            f"Using unfiltered results ({len(documents)} docs)."
                        )
            
            context = '\n\n'.join(documents)
            
            if self.logger:
                self.logger.info(
                    f"RAG retrieved {len(documents)} chunks "
                    f"({len(context)} chars)"
                )
            
            return context
        
        except RAGError:
            raise
        except Exception as e:
            raise RAGError(f"Retrieval failed: {str(e)}")
    
    def validate_schema(self) -> Dict[str, Any]:
        """
        Validate ChromaDB collection schema.
        
        Returns:
            Schema information including sample metadata
            
        Raises:
            RAGError: If validation fails
        """
        try:
            count = self.collection.count()
            
            if count == 0:
                return {
                    "count": 0,
                    "status": "empty",
                    "message": "Collection is empty"
                }
            
            # Get sample to check metadata
            sample = self.collection.get(limit=1, include=['metadatas'])
            
            metadata_fields = set()
            if sample.get('metadatas'):
                for meta in sample['metadatas']:
                    if meta:
                        metadata_fields.update(meta.keys())
            
            required_fields = {'category', 'embedding_date'}
            missing_fields = required_fields - metadata_fields
            
            return {
                "count": count,
                "metadata_fields": list(metadata_fields),
                "missing_required_fields": list(missing_fields),
                "status": "valid" if not missing_fields else "invalid"
            }
        
        except Exception as e:
            raise RAGError(f"Schema validation failed: {str(e)}")