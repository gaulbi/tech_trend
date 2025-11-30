"""RAG engine using ChromaDB for context retrieval."""

from typing import List

import chromadb
from chromadb import Settings

from .factories import BaseEmbeddingClient


class RAGEngine:
    """Handles RAG operations with ChromaDB."""
    
    def __init__(
        self,
        database_path: str,
        embedding_client: BaseEmbeddingClient,
        collection_name: str = "tech_trends"
    ):
        """Initialize RAG engine.
        
        Args:
            database_path: Path to ChromaDB persistence directory
            embedding_client: Client for generating embeddings
            collection_name: Name of ChromaDB collection
        """
        self.embedding_client = embedding_client
        self.client = chromadb.PersistentClient(
            path=database_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def retrieve_context(
        self,
        query_text: str,
        category: str,
        embedding_date: str,
        top_k: int = 20
    ) -> str:
        """Retrieve relevant context from ChromaDB.
        
        Args:
            query_text: Text to search for (topic + reason)
            category: Category filter
            embedding_date: Date filter (YYYY-MM-DD)
            top_k: Number of results to retrieve
            
        Returns:
            Concatenated context string from retrieved chunks
        """
        # Generate query embedding
        query_embedding = self.embedding_client.embed(query_text)
        
        # Query ChromaDB with filters
        # ChromaDB requires explicit operators in where clause
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "$and": [
                    {"category": {"$eq": category}},
                    {"embedding_date": {"$eq": embedding_date}}
                ]
            }
        )
        
        # Extract and concatenate documents
        if not results["documents"] or not results["documents"][0]:
            return ""
        
        documents = results["documents"][0]
        context = "\n\n".join(documents)
        
        return context
    
    def get_collection_stats(self) -> dict:
        """Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": self.collection.name
        }