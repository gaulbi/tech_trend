#!/usr/bin/env python3
"""
Generate example test data for the Scraped Content Embedder.

This script creates sample scraped content files to test the embedder.
"""

import json
from datetime import datetime
from pathlib import Path


def create_sample_data():
    """Create sample scraped content for testing."""
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create directory structure
    base_path = Path("data/scraped-content") / today
    
    # Sample category 1: Software Engineering Dev
    category1_path = base_path / "software-engineering-dev"
    category1_path.mkdir(parents=True, exist_ok=True)
    
    sample_data_1 = {
        "analysis_timestamp": datetime.now().isoformat(),
        "source_file": "software-engineering-dev.json",
        "category": "Software Engineering Dev",
        "trends": [
            {
                "topic": "Python 3.13 New Features and Performance Improvements",
                "link": "https://example.com/python-3-13-features",
                "content": """Python 3.13 introduces several exciting new features and performance improvements. 
                The new version includes better error messages with more context, improved performance for dictionary operations, 
                and enhanced type hinting capabilities. The GIL (Global Interpreter Lock) has been made optional in experimental mode, 
                which could significantly improve multi-threaded performance for CPU-bound tasks. 
                
                Additionally, the new version includes improvements to the asyncio module, making it easier to work with 
                asynchronous code. The pattern matching feature introduced in Python 3.10 has been refined with better 
                performance and more intuitive syntax. Developers should also note the deprecation of several older APIs 
                and the introduction of new standard library modules for common tasks like JSON handling and HTTP requests.""",
                "scrape_timestamp": datetime.now().isoformat(),
                "error": None
            },
            {
                "topic": "Best Practices for Microservices Architecture in 2025",
                "link": "https://example.com/microservices-best-practices",
                "content": """Microservices architecture continues to evolve in 2025 with new best practices emerging. 
                Service mesh technologies like Istio and Linkerd have become standard for managing service-to-service communication. 
                Observability is now considered a first-class citizen, with distributed tracing and metrics collection 
                built into every service from day one.
                
                Container orchestration with Kubernetes has matured, with focus shifting to GitOps practices and 
                declarative infrastructure management. Teams are adopting event-driven architectures more frequently, 
                using message brokers like Kafka and RabbitMQ to decouple services. API gateway patterns have evolved 
                to include rate limiting, authentication, and transformation capabilities at the edge.
                
                Security best practices now emphasize zero-trust architectures, mutual TLS between services, and 
                regular security scanning of container images. Development teams are also focusing on resilience patterns 
                like circuit breakers, bulkheads, and retry mechanisms to handle failures gracefully.""",
                "scrape_timestamp": datetime.now().isoformat(),
                "error": None
            },
            {
                "topic": "GraphQL vs REST: Modern API Design Considerations",
                "link": "https://example.com/graphql-vs-rest",
                "content": """The debate between GraphQL and REST APIs continues in 2025, but the landscape has evolved. 
                GraphQL offers powerful query capabilities and reduces over-fetching, making it ideal for complex data requirements. 
                REST APIs remain simpler to implement and cache, with better tooling support in many ecosystems.
                
                Modern best practices suggest using GraphQL for client-facing APIs where flexibility is crucial, 
                and REST for internal service-to-service communication where simplicity and caching are priorities. 
                Hybrid approaches are also gaining traction, with companies exposing both REST and GraphQL endpoints 
                for different use cases. The key is understanding your specific requirements and choosing the right tool 
                for the job rather than following trends blindly.""",
                "scrape_timestamp": datetime.now().isoformat(),
                "error": None
            }
        ]
    }
    
    with open(category1_path / "url-scrape.json", "w") as f:
        json.dump(sample_data_1, f, indent=2)
    
    # Sample category 2: AI and Machine Learning
    category2_path = base_path / "ai-machine-learning"
    category2_path.mkdir(parents=True, exist_ok=True)
    
    sample_data_2 = {
        "analysis_timestamp": datetime.now().isoformat(),
        "source_file": "ai-machine-learning.json",
        "category": "AI Machine Learning",
        "trends": [
            {
                "topic": "Large Language Models: Scaling Laws and Efficiency",
                "link": "https://example.com/llm-scaling",
                "content": """Recent research in large language models has revealed important insights about scaling laws. 
                While larger models generally perform better, the relationship between model size and performance is not linear. 
                Researchers are now focusing on efficiency improvements through techniques like mixture of experts, 
                sparse attention mechanisms, and better training data curation.
                
                The trend is shifting from pure scale to smarter architectures that can achieve similar performance 
                with fewer parameters. This includes approaches like knowledge distillation, where smaller models 
                learn from larger ones, and retrieval-augmented generation, which allows models to access external 
                knowledge bases. Energy efficiency has become a major concern, with new metrics being developed 
                to measure the environmental impact of training and deploying large models.""",
                "scrape_timestamp": datetime.now().isoformat(),
                "error": None
            },
            {
                "topic": "Vector Databases for RAG Applications",
                "link": "https://example.com/vector-databases-rag",
                "content": """Vector databases have become essential infrastructure for Retrieval-Augmented Generation applications. 
                Popular options include ChromaDB, Pinecone, Weaviate, and Qdrant, each with different strengths. 
                ChromaDB is excellent for local development and prototyping, while Pinecone offers managed cloud services 
                with high performance at scale.
                
                Key considerations when choosing a vector database include query performance, scalability, 
                filtering capabilities, and integration with existing infrastructure. Embedding quality is crucial, 
                with newer models like OpenAI's text-embedding-3 and Cohere's embeddings showing significant improvements. 
                Hybrid search combining vector similarity with traditional keyword search is becoming the standard approach 
                for production RAG systems.""",
                "scrape_timestamp": datetime.now().isoformat(),
                "error": None
            }
        ]
    }
    
    with open(category2_path / "web-scrape.json", "w") as f:
        json.dump(sample_data_2, f, indent=2)
    
    print(f"✅ Sample data created in: {base_path}")
    print(f"   - {category1_path / 'url-scrape.json'}")
    print(f"   - {category2_path / 'web-scrape.json'}")
    print(f"\nYou can now run: python scrapped_content_embedder.py")


if __name__ == "__main__":
    create_sample_data()