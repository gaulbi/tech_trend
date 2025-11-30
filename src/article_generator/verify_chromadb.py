#!/usr/bin/env python3
"""
ChromaDB Verification Script
Verify embeddings exist with correct category and date filters
"""

import chromadb
from chromadb import Settings
from datetime import date
from collections import defaultdict
import json


def verify_chromadb(
    database_path: str = "data/embedding",
    collection_name: str = "tech_trends",
    target_date: str = None,
    target_category: str = None
):
    """Verify ChromaDB contents and test category/date filters.
    
    Args:
        database_path: Path to ChromaDB persistence directory
        collection_name: Name of the collection to verify
        target_date: Date to check (YYYY-MM-DD), defaults to today
        target_category: Specific category to check (optional)
    """
    if target_date is None:
        target_date = date.today().strftime('%Y-%m-%d')
    
    print("=" * 70)
    print("ChromaDB Verification Script")
    print("=" * 70)
    print(f"Database Path: {database_path}")
    print(f"Collection: {collection_name}")
    print(f"Target Date: {target_date}")
    if target_category:
        print(f"Target Category: {target_category}")
    print("=" * 70)
    print()
    
    # Connect to ChromaDB
    try:
        client = chromadb.PersistentClient(
            path=database_path,
            settings=Settings(anonymized_telemetry=False)
        )
        print("✅ Connected to ChromaDB")
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}")
        return
    
    # List all collections
    try:
        collections = client.list_collections()
        print(f"\n📚 Available collections ({len(collections)}):")
        for col in collections:
            print(f"  - {col.name} (count: {col.count()})")
    except Exception as e:
        print(f"⚠️  Could not list collections: {e}")
    
    # Get collection
    try:
        collection = client.get_collection(name=collection_name)
        print(f"\n✅ Opened collection: {collection_name}")
    except Exception as e:
        print(f"\n❌ Collection '{collection_name}' not found: {e}")
        return
    
    print()
    print("-" * 70)
    print("COLLECTION STATISTICS")
    print("-" * 70)
    
    # Get total count
    total_count = collection.count()
    print(f"Total documents: {total_count}")
    
    if total_count == 0:
        print("\n❌ Collection is EMPTY. You need to run embedding pipeline first.")
        return
    
    print()
    print("-" * 70)
    print("SAMPLE METADATA (First 3 Documents)")
    print("-" * 70)
    
    # Get sample documents to inspect metadata structure
    try:
        sample = collection.get(limit=3, include=["metadatas", "documents"])
        
        if sample['metadatas']:
            for idx, metadata in enumerate(sample['metadatas'], 1):
                print(f"\n📄 Document {idx}:")
                print(f"   Metadata: {json.dumps(metadata, indent=6)}")
                doc_text = sample['documents'][idx-1][:150]
                print(f"   Content: {doc_text}...")
        else:
            print("⚠️  No metadata found")
    except Exception as e:
        print(f"❌ Error fetching samples: {e}")
    
    print()
    print("-" * 70)
    print("METADATA FIELD ANALYSIS")
    print("-" * 70)
    
    # Analyze what metadata fields exist
    try:
        all_metadata = collection.get(include=["metadatas"])
        
        if all_metadata['metadatas']:
            # Collect all unique field names
            all_fields = set()
            for meta in all_metadata['metadatas']:
                if meta:
                    all_fields.update(meta.keys())
            
            print(f"\n📋 Metadata fields found: {sorted(all_fields)}")
            
            # Check for required fields
            required_fields = ['category', 'embedding_date']
            print("\n✅ Required field check:")
            for field in required_fields:
                if field in all_fields:
                    print(f"   ✅ '{field}' - EXISTS")
                else:
                    print(f"   ❌ '{field}' - MISSING")
                    print(f"      This will cause RAG queries to fail!")
        else:
            print("⚠️  No metadata found in collection")
    except Exception as e:
        print(f"❌ Error analyzing metadata: {e}")
        return
    
    print()
    print("-" * 70)
    print("CATEGORY BREAKDOWN")
    print("-" * 70)
    
    # Count documents by category
    category_counts = defaultdict(int)
    for meta in all_metadata['metadatas']:
        if meta:
            category = meta.get('category', 'UNKNOWN')
            category_counts[category] += 1
    
    print(f"\n📊 Documents per category ({len(category_counts)} categories):")
    for category, count in sorted(category_counts.items()):
        marker = "⭐" if category == target_category else "  "
        print(f"   {marker} '{category}': {count} documents")
    
    print()
    print("-" * 70)
    print("DATE BREAKDOWN")
    print("-" * 70)
    
    # Count documents by date
    date_counts = defaultdict(int)
    for meta in all_metadata['metadatas']:
        if meta:
            emb_date = meta.get('embedding_date', 'UNKNOWN')
            date_counts[emb_date] += 1
    
    print(f"\n📅 Documents per date ({len(date_counts)} dates):")
    for emb_date, count in sorted(date_counts.items()):
        marker = "⭐" if emb_date == target_date else "  "
        print(f"   {marker} '{emb_date}': {count} documents")
    
    print()
    print("-" * 70)
    print("CATEGORY + DATE MATRIX")
    print("-" * 70)
    
    # Build matrix of category x date
    matrix = defaultdict(lambda: defaultdict(int))
    for meta in all_metadata['metadatas']:
        if meta:
            cat = meta.get('category', 'UNKNOWN')
            dt = meta.get('embedding_date', 'UNKNOWN')
            matrix[cat][dt] += 1
    
    print(f"\n📊 Document count by category and date:")
    print(f"\n{'Category':<30} | Date       | Count")
    print("-" * 70)
    
    for category in sorted(matrix.keys()):
        for dt in sorted(matrix[category].keys()):
            count = matrix[category][dt]
            marker = "⭐" if (category == target_category and dt == target_date) else "  "
            print(f"{marker} {category:<28} | {dt} | {count}")
    
    print()
    print("-" * 70)
    print(f"FILTER TEST: DATE={target_date}")
    if target_category:
        print(f"             CATEGORY={target_category}")
    print("-" * 70)
    
    # Determine which categories to test
    categories_to_test = [target_category] if target_category else sorted(category_counts.keys())
    
    print(f"\n🧪 Testing filters (showing first 3 results per test):\n")
    
    for category in categories_to_test:
        print(f"Testing: category='{category}' AND date='{target_date}'")
        print("-" * 70)
        
        try:
            # Test with actual get() using where filter
            filtered_results = collection.get(
                where={
                    "$and": [
                        {"category": {"$eq": category}},
                        {"embedding_date": {"$eq": target_date}}
                    ]
                },
                limit=3,
                include=["metadatas", "documents"]
            )
            
            result_count = len(filtered_results['ids']) if filtered_results['ids'] else 0
            
            if result_count > 0:
                print(f"✅ Found {result_count} documents (showing up to 3)")
                for idx, (doc_id, metadata, doc) in enumerate(zip(
                    filtered_results['ids'][:3],
                    filtered_results['metadatas'][:3],
                    filtered_results['documents'][:3]
                ), 1):
                    print(f"\n   Result {idx}:")
                    print(f"      ID: {doc_id}")
                    print(f"      Category: {metadata.get('category')}")
                    print(f"      Date: {metadata.get('embedding_date')}")
                    print(f"      Content: {doc[:100]}...")
            else:
                print(f"⚠️  Found 0 documents")
                
                # Debug: Try just category
                cat_only = collection.get(
                    where={"category": {"$eq": category}},
                    limit=1,
                    include=["metadatas"]
                )
                
                if cat_only['ids']:
                    print(f"   ℹ️  Category '{category}' exists in collection")
                    # Show what dates are available for this category
                    dates_for_cat = set()
                    for meta in all_metadata['metadatas']:
                        if meta and meta.get('category') == category:
                            dates_for_cat.add(meta.get('embedding_date'))
                    print(f"   ℹ️  Available dates for '{category}': {sorted(dates_for_cat)}")
                else:
                    print(f"   ❌ Category '{category}' not found in collection at all")
        
        except Exception as e:
            print(f"❌ Query failed: {e}")
            print(f"   Error type: {type(e).__name__}")
        
        print()
    
    print()
    print("-" * 70)
    print("ACTUAL QUERY SIMULATION (Like article_generator.py)")
    print("-" * 70)
    
    # Simulate the actual query from article_generator
    if target_category:
        print(f"\n🔬 Simulating RAG query:")
        print(f"   Category: '{target_category}'")
        print(f"   Date: '{target_date}'")
        print(f"   Top K: 20")
        
        try:
            # Need to create a dummy embedding for query
            # First, check embedding dimension
            sample_data = collection.get(limit=1, include=["embeddings"])
            if sample_data['embeddings'] and sample_data['embeddings'][0]:
                embedding_dim = len(sample_data['embeddings'][0])
                print(f"   Embedding dimension: {embedding_dim}")
                
                # Create dummy query embedding
                dummy_embedding = [0.0] * embedding_dim
                
                # Execute query exactly like rag_engine.py does
                results = collection.query(
                    query_embeddings=[dummy_embedding],
                    n_results=20,
                    where={
                        "$and": [
                            {"category": {"$eq": target_category}},
                            {"embedding_date": {"$eq": target_date}}
                        ]
                    },
                    include=["metadatas", "documents", "distances"]
                )
                
                if results['documents'] and results['documents'][0]:
                    doc_count = len(results['documents'][0])
                    print(f"\n✅ Query returned {doc_count} results")
                    
                    print("\nTop 3 results:")
                    for idx in range(min(3, doc_count)):
                        print(f"\n   Result {idx + 1}:")
                        print(f"      Distance: {results['distances'][0][idx]:.4f}")
                        print(f"      Category: {results['metadatas'][0][idx].get('category')}")
                        print(f"      Date: {results['metadatas'][0][idx].get('embedding_date')}")
                        print(f"      Content: {results['documents'][0][idx][:100]}...")
                else:
                    print(f"\n⚠️  Query returned 0 results")
                    print(f"\n   This is why you're seeing:")
                    print(f"   'WARNING - No context retrieved from RAG for trend'")
            else:
                print("   ⚠️  No embeddings found in collection")
        
        except Exception as e:
            print(f"\n❌ Query simulation failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            print(f"   Traceback:\n{traceback.format_exc()}")
    
    print()
    print("-" * 70)
    print("RECOMMENDATIONS")
    print("-" * 70)
    
    # Provide specific recommendations
    if target_date not in date_counts or date_counts[target_date] == 0:
        print(f"\n⚠️  No embeddings found for date: {target_date}")
        print(f"\n   Available dates in collection:")
        for dt, count in sorted(date_counts.items()):
            print(f"      - {dt} ({count} docs)")
        print(f"\n   💡 Solutions:")
        print(f"      1. Run embedding pipeline for {target_date}")
        print(f"      2. Use an existing date from the list above")
    else:
        print(f"\n✅ Embeddings exist for {target_date} ({date_counts[target_date]} docs)")
    
    if target_category:
        if target_category not in category_counts:
            print(f"\n⚠️  Category '{target_category}' not found in collection")
            print(f"\n   Available categories:")
            for cat in sorted(category_counts.keys()):
                print(f"      - '{cat}'")
        else:
            print(f"\n✅ Category '{target_category}' exists ({category_counts[target_category]} docs)")
            
            # Check if combination exists
            if matrix[target_category].get(target_date, 0) == 0:
                print(f"\n⚠️  No documents with category='{target_category}' AND date='{target_date}'")
                print(f"\n   Dates available for category '{target_category}':")
                for dt in sorted(matrix[target_category].keys()):
                    print(f"      - {dt} ({matrix[target_category][dt]} docs)")
            else:
                count = matrix[target_category][target_date]
                print(f"\n✅ Found {count} docs with category='{target_category}' AND date='{target_date}'")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify ChromaDB embeddings and test filters"
    )
    parser.add_argument(
        "--database-path",
        default="data/embedding",
        help="Path to ChromaDB database (default: data/embedding)"
    )
    parser.add_argument(
        "--collection",
        default="tech_trends",
        help="Collection name (default: tech_trends)"
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Date to check in YYYY-MM-DD format (default: today)"
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Specific category to check (optional)"
    )
    
    args = parser.parse_args()
    
    verify_chromadb(
        database_path=args.database_path,
        collection_name=args.collection,
        target_date=args.date,
        target_category=args.category
    )