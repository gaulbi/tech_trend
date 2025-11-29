# Scraped Content Embedder

A production-grade Python module for embedding scraped web content into ChromaDB using multiple embedding provider options.

## Features

- ✅ **Multi-Provider Support**: OpenAI, Voyage AI, Gemini, and local Sentence Transformers
- ✅ **Factory Pattern**: Clean abstraction for embedding clients
- ✅ **Retry Logic**: Exponential backoff (1s, 3s, 5s) for API calls
- ✅ **Error Isolation**: Continues processing if individual files fail
- ✅ **Comprehensive Logging**: Structured logging for all operations
- ✅ **ChromaDB Integration**: Persistent vector storage with metadata
- ✅ **Smart Chunking**: Uses LangChain's RecursiveCharacterTextSplitter
- ✅ **Type Hints**: Full type annotations throughout
- ✅ **Production-Ready**: Timeout handling, graceful degradation, detailed reporting

## Project Structure

```
.
├── scrapped_content_embedder.py              # Main entry point
├── src/
│   └── scrapped_content_embedder/            # Package
│       ├── __init__.py
│       ├── config.py                         # Configuration management
│       ├── embedding_clients.py              # Embedding provider clients
│       └── embedder.py                       # Main embedder logic
├── data/
│   ├── scraped-content/                     # Input scraped content
│   │   └── YYYY-MM-DD/
│   │       └── category-name/
│   │           ├── url-scrape.json
│   │           └── web-scrape.json
│   └── embedding/                            # ChromaDB database
├── config.yaml                               # Configuration file
├── .env                                      # API keys (gitignored)
├── .env.example                              # Example env file
├── requirements.txt                          # Dependencies
└── README.md                                 # This file
```

## Installation

### 1. Clone or create the project structure

```bash
mkdir scraped-content-embedder
cd scraped-content-embedder
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```bash
OPENAI_API_KEY=sk-...
VOYAGE_API_KEY=pa-...
GOOGLE_API_KEY=AIza...
```

### 4. Configure settings

Edit `config.yaml` to match your setup:

```yaml
scrape:
  url-scraped-content: data/scraped-content

embedding:
  chunk-size: 1000
  chunk-overlap: 200
  embedding-provider: sentence-transformers  # or openai, voyage, gemini
  embedding-model: all-MiniLM-L6-v2
  timeout: 60
  database-path: data/embedding
```

## Usage

### Basic Usage

Run the embedder to process today's scraped content:

```bash
python scrapped_content_embedder.py
```

### Expected Input Format

The embedder expects scraped content in the following structure:

```
data/scraped-content/
└── 2025-11-23/
    ├── software-engineering-dev/
    │   ├── url-scrape.json
    │   └── web-scrape.json
    └── ai-chips-ai-hardware-infrastructure/
        ├── url-scrape.json
        └── web-scrape.json
```

Each JSON file should follow this schema:

```json
{
  "analysis_timestamp": "2025-11-22T08:02:55.816247",
  "source_file": "category-file.json",
  "category": "Software Engineering Dev",
  "trends": [
    {
      "topic": "Article title or topic",
      "link": "https://example.com/article",
      "content": "Full article content to be embedded...",
      "scrape_timestamp": "2025-11-22T15:35:58.679586",
      "error": null
    }
  ]
}
```

### Output

The embedder creates ChromaDB collections named after categories (normalized):

- `software-engineering-dev`
- `ai-chips-ai-hardware-infrastructure`

Each document in ChromaDB contains:

```json
{
  "id": "software-engineering-dev_file-name_chunk_0",
  "document": "Chunked text content...",
  "embedding": [0.123, -0.456, ...],
  "metadata": {
    "url": "https://example.com/article",
    "source_file": "file-name.json",
    "category": "Software Engineering Dev",
    "one_word_category": "software-engineering-dev",
    "embedding_date": "2025-11-23",
    "chunk_index": 0,
    "total_chunks": 5,
    "topic": "Article title"
  }
}
```

## Embedding Providers

### OpenAI

```yaml
embedding-provider: openai
embedding-model: text-embedding-3-small  # or text-embedding-3-large
```

Requires: `OPENAI_API_KEY`

### Voyage AI

```yaml
embedding-provider: voyage
embedding-model: voyage-2  # or voyage-large-2, voyage-code-2
```

Requires: `VOYAGE_API_KEY`

### Google Gemini

```yaml
embedding-provider: gemini
embedding-model: models/embedding-001
```

Requires: `GOOGLE_API_KEY`

### Sentence Transformers (Local)

```yaml
embedding-provider: sentence-transformers
embedding-model: all-MiniLM-L6-v2  # or any HuggingFace model
```

No API key required - runs locally!

## Querying ChromaDB

Example code to query the embedded content:

```python
import chromadb

# Connect to database
client = chromadb.PersistentClient(path="data/embedding")

# Get collection
collection = client.get_collection("software-engineering-dev")

# Query
results = collection.query(
    query_texts=["What are the latest developments in Python?"],
    n_results=5,
    where={"embedding_date": "2025-11-23"}
)

# Print results
for doc, metadata, distance in zip(
    results['documents'][0],
    results['metadatas'][0],
    results['distances'][0]
):
    print(f"Topic: {metadata['topic']}")
    print(f"URL: {metadata['url']}")
    print(f"Distance: {distance}")
    print(f"Content: {doc[:200]}...")
    print("-" * 80)
```

## Error Handling

The embedder includes comprehensive error handling:

- **JSON Parsing Errors**: Logs and continues with other files
- **Network Failures**: Retries with exponential backoff (1s, 3s, 5s)
- **Timeout Handling**: Configurable timeout for all API calls
- **File Errors**: Continues processing remaining files
- **API Errors**: Detailed logging with context

## Logging

Logs are written to both console and `embedder.log`:

```
2025-11-23 10:00:00 - root - INFO - Starting Scraped Content Embedder
2025-11-23 10:00:01 - root - INFO - Configuration loaded - Provider: sentence-transformers
2025-11-23 10:00:02 - ScrapedContentEmbedder - INFO - ChromaDB initialized at data/embedding
2025-11-23 10:00:03 - ScrapedContentEmbedder - INFO - Processing content from: data/scraped-content/2025-11-23
2025-11-23 10:00:04 - ScrapedContentEmbedder - INFO - Processing category: software-engineering-dev
2025-11-23 10:00:05 - ScrapedContentEmbedder - INFO - Embedded 3 chunks from trend: New Python 3.13 Features
```

## Performance Considerations

- **Batch Processing**: Embeddings are generated in batches per trend
- **Local Option**: Use Sentence Transformers for unlimited, free embeddings
- **Chunking**: Configurable chunk size/overlap for optimal retrieval
- **Upsert**: Updates existing documents instead of duplicating

## Troubleshooting

### "No content directory found for today"

Make sure your scraped content follows the expected directory structure:
```
data/scraped-content/YYYY-MM-DD/category-name/*.json
```

### "API key not found"

Ensure your `.env` file exists and contains the required API key for your chosen provider.

### Import errors

Install all dependencies:
```bash
pip install -r requirements.txt
```

### ChromaDB errors

Ensure the database path is writable and you have sufficient disk space.

## License

MIT License - feel free to use in your projects!

## Contributing

Contributions welcome! Please ensure:
- Type hints on all functions
- Docstrings for all classes/methods
- Error handling with specific exceptions
- Logging for important operations
- Tests for new features

## Support

For issues or questions, please open an issue on GitHub.