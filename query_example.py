#!/usr/bin/env python3
"""
Example script for querying embedded content from ChromaDB.

IMPORTANT: You must use the SAME embedding model for querying that you used for embedding!

This demonstrates how to search and retrieve embedded content after running the embedder.
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import yaml
import sys
import os

# Add parent directory to path to import embedding clients
sys.path.insert(0, str(Path(__file__).parent))
from src.scrapped_content_embedder.embedding_clients import EmbedderFactory


def load_config() -> Dict[str, Any]:
    """
    Load configuration to get the embedding model used.
    
    Returns:
        Configuration dictionary
    """
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"⚠️  Warning: Could not load config.yaml: {e}")
        return None


def initialize_client(db_path: str = "data/embedding") -> chromadb.PersistentClient:
    """
    Initialize ChromaDB client.
    
    Args:
        db_path: Path to ChromaDB database
        
    Returns:
        ChromaDB client instance
    """
    return chromadb.PersistentClient(
        path=db_path,
        settings=Settings(anonymized_telemetry=False)
    )


def initialize_embedding_client(config: Dict[str, Any]):
    """
    Initialize the same embedding client used for embedding.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Embedding client instance
    """
    embedding_config = config.get("embedding", {})
    provider = embedding_config.get("embedding-provider")
    model = embedding_config.get("embedding-model")
    timeout = embedding_config.get("timeout", 60)
    
    print(f"🔧 Initializing embedding client:")
    print(f"   Provider: {provider}")
    print(f"   Model: {model}")
    
    return EmbedderFactory.create_client(
        provider=provider,
        model_name=model,
        timeout=timeout
    )


def list_collections(client: chromadb.PersistentClient) -> List[str]:
    """
    List all available collections in the database.
    
    Args:
        client: ChromaDB client
        
    Returns:
        List of collection names
    """
    collections = client.list_collections()
    return [col.name for col in collections]


def get_collection_stats(client: chromadb.PersistentClient, collection_name: str) -> Dict[str, Any]:
    """
    Get statistics about a collection.
    
    Args:
        client: ChromaDB client
        collection_name: Name of the collection
        
    Returns:
        Dictionary with collection statistics
    """
    try:
        collection = client.get_collection(collection_name)
        count = collection.count()
        
        # Get sample document to inspect metadata and embedding dimension
        sample = collection.get(limit=1, include=["embeddings", "metadatas"])
        embedding_dim = len(sample["embeddings"][0]) if sample["embeddings"] else None
        
        return {
            "name": collection_name,
            "count": count,
            "embedding_dimension": embedding_dim,
            "sample_metadata": sample["metadatas"][0] if sample["metadatas"] else None
        }
    except Exception as e:
        return {
            "name": collection_name,
            "error": str(e)
        }


def search_collection(
    client: chromadb.PersistentClient,
    embedding_client,
    collection_name: str,
    query_text: str,
    n_results: int = 5,
    filters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Search a collection with the correct embedding model.
    
    Args:
        client: ChromaDB client
        embedding_client: Embedding client (must match the one used for embedding)
        collection_name: Name of the collection to search
        query_text: Search query
        n_results: Number of results to return
        filters: Optional metadata filters
        
    Returns:
        Search results dictionary
    """
    try:
        collection = client.get_collection(collection_name)
        
        # Generate query embedding using the SAME model used for embedding
        print(f"🔍 Generating query embedding...")
        query_embeddings = embedding_client.embed_texts([query_text])
        
        query_params = {
            "query_embeddings": query_embeddings,
            "n_results": n_results
        }
        
        if filters:
            query_params["where"] = filters
        
        results = collection.query(**query_params)
        
        return {
            "success": True,
            "query": query_text,
            "collection": collection_name,
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def print_search_results(search_results: Dict[str, Any]) -> None:
    """
    Pretty print search results.
    
    Args:
        search_results: Results from search_collection
    """
    if not search_results.get("success"):
        print(f"❌ Search failed: {search_results.get('error')}")
        return
    
    print("\n" + "="*80)
    print(f"🔍 Query: {search_results['query']}")
    print(f"📚 Collection: {search_results['collection']}")
    print("="*80 + "\n")
    
    results = search_results["results"]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    
    if not documents:
        print("No results found.")
        return
    
    for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
        print(f"Result #{idx} (Distance: {dist:.4f})")
        print("─" * 80)
        print(f"📄 Topic: {meta.get('topic', 'N/A')}")
        print(f"🔗 URL: {meta.get('url', 'N/A')}")
        print(f"📁 Category: {meta.get('category', 'N/A')}")
        print(f"📅 Date: {meta.get('embedding_date', 'N/A')}")
        print(f"📊 Chunk: {meta.get('chunk_index', 0) + 1} of {meta.get('total_chunks', 1)}")
        print(f"\n💬 Content Preview:")
        print(f"{doc[:300]}{'...' if len(doc) > 300 else ''}")
        print("\n" + "="*80 + "\n")


def main():
    """Main execution for querying examples."""
    print("ChromaDB Query Examples (with Correct Embedding Model)")
    print("="*80)
    
    # Load configuration
    print("\n📋 Loading configuration...")
    config = load_config()
    if not config:
        print("❌ Failed to load config.yaml. Using default settings.")
        return
    
    # Initialize ChromaDB client
    print("\n1️⃣ Connecting to ChromaDB...")
    client = initialize_client()
    print("✅ Connected successfully")
    
    # Initialize embedding client (SAME as used for embedding)
    print("\n2️⃣ Initializing embedding client...")
    try:
        embedding_client = initialize_embedding_client(config)
        print(f"✅ Embedding client initialized (dimension: {embedding_client.get_dimension()})")
    except Exception as e:
        print(f"❌ Failed to initialize embedding client: {e}")
        return
    
    # List collections
    print("\n3️⃣ Available Collections:")
    collections = list_collections(client)
    if collections:
        for col in collections:
            stats = get_collection_stats(client, col)
            if "error" not in stats:
                print(f"   • {col}: {stats['count']} documents (dim: {stats['embedding_dimension']})")
            else:
                print(f"   • {col}: Error - {stats['error']}")
    else:
        print("   No collections found. Run the embedder first!")
        return
    
    # Verify dimension match
    print("\n4️⃣ Verifying Dimension Compatibility...")
    embedding_dim = embedding_client.get_dimension()
    for col in collections:
        stats = get_collection_stats(client, col)
        if "error" not in stats and stats['embedding_dimension']:
            if stats['embedding_dimension'] == embedding_dim:
                print(f"   ✅ {col}: Compatible ({stats['embedding_dimension']} == {embedding_dim})")
            else:
                print(f"   ❌ {col}: INCOMPATIBLE ({stats['embedding_dimension']} != {embedding_dim})")
                print(f"      This collection was embedded with a different model!")
    
    # Example searches
    print("\n5️⃣ Example Searches:")
    print("─" * 80)
    
    example_queries = [
        {
            "query": "Python performance improvements and new features",
            "n_results": 2
        },
        {
            "query": "vector databases for retrieval augmented generation",
            "n_results": 2
        }
    ]
    
    for example in example_queries:
        if collections:
            print(f"\n🔎 Searching '{collections[0]}'...")
            results = search_collection(
                client=client,
                embedding_client=embedding_client,
                collection_name=collections[0],
                query_text=example["query"],
                n_results=example["n_results"]
            )
            print_search_results(results)
    
    # Example with filters
    print("\n6️⃣ Filtered Search Example:")
    print("─" * 80)
    print("Searching for content from today only...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    if collections:
        filtered_results = search_collection(
            client=client,
            embedding_client=embedding_client,
            collection_name=collections[0],
            query_text="best practices and architecture",
            n_results=3,
            filters={"embedding_date": today}
        )
        print_search_results(filtered_results)
    
    print("\n✅ Query examples completed!")


if __name__ == "__main__":
    main()