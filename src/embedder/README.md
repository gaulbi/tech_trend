# Embedder - Production-Grade RAG Embedding System

A robust Python module for chunking articles, generating embeddings, and storing them in ChromaDB for Retrieval-Augmented Generation (RAG) applications.

## Features

- **Multi-Provider Support**: OpenAI, Voyage AI, Google Gemini, and Sentence Transformers (local)
- **Smart Chunking**: Overlapping text chunks with sentence boundary detection
- **Idempotent Operations**: Skips already-embedded content to save API costs
- **Robust Error Handling**: Exponential backoff retry logic with comprehensive error handling
- **Production Logging**: JSON-formatted logs with rotation and colored console output
- **Type Safety**: Full type hints and Google-style docstrings

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Create a `config.yaml` file:

```yaml
scrape:
  url-scraped-content: data/scraped-content

embedding:
  chunk-size: 1000
  chunk-overlap: 200
  embedding-provider: openai  # openai, voyageai, gemini, sentence-transformers
  embedding-model: text-embedding-3-small
  timeout: 60
  max-retries: 3
  batch-size: 50
  database-path: data/embedding
  ktop: 20
  log: log/embedding
```

## Environment Variables

Create a `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Voyage AI
VOYAGEAI_API_KEY=...

# Google Gemini
GEMINI_API_KEY=...

# Optional: Logging configuration
LOG_LEVEL=INFO
LOG_DIR=log/embedding
LOG_JSON=true
```

## Usage

### Process all categories for today

```bash
python embedder.py
```

### Process specific category

```bash
python embedder.py --category "software_engineering"
```

### Process specific date

```bash
python embedder.py --feed_date "2025-02-01"
```

### Process specific category and date

```bash
python embedder.py --category "software_engineering" --feed_date "2025-02-01"
```

## Input Format

The module expects JSON files in the following structure:

```
data/scraped-content/{FEED_DATE}/{category}/*.json
```

Example: `data/scraped-content/2025-11-21/software_engineering/url-scrape.json`

```json
{
  "feed_date": "2025-11-21",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "Article Title",
      "query_used": "search query",
      "search_link": "https://example.com/article",
      "content": "Full article content..."
    }
  ]
}
```

## Output

### ChromaDB Vector Database

- **Location**: `{embedding.database-path}/`
- **Collection**: `embeddings`
- **ID Format**: `{category}|{FEED_DATE}|{url_hash}|chunk_{index}`

### Document Schema

- **Document**: Text chunk content
- **Metadata**:
  - `url`: Article URL
  - `category`: Article category
  - `embedding_date`: Embedding date (YYYY-MM-DD)
  - `source_file`: Path to source JSON file
  - `chunk_index`: Chunk index (0-based)

## Architecture

### Project Structure

```
.
├── embedder.py              # Main entry point
├── src/
│   └── embedder/            # Package
│       ├── __init__.py
│       ├── config.py        # Configuration loader
│       ├── logger.py        # Logging utilities
│       ├── exceptions.py    # Custom exceptions
│       ├── chunker.py       # Text chunking
│       ├── database.py      # ChromaDB operations
│       ├── processor.py     # Main processing logic
│       └── embeddings/      # Embedding providers
│           ├── __init__.py
│           ├── base.py      # Abstract base class
│           ├── factory.py   # Factory pattern
│           ├── openai_embedder.py
│           ├── voyage_embedder.py
│           ├── gemini_embedder.py
│           └── sentence_transformer.py
├── data/
│   ├── embedding/           # ChromaDB database
│   └── scraped-content/     # Input data
├── log/
│   └── embedding/           # Log files
├── config.yaml              # Configuration
├── .env                     # Environment variables
└── requirements.txt         # Dependencies
```

### Design Patterns

1. **Factory Pattern**: Dynamic creation of embedding providers
2. **Abstract Base Classes**: Consistent interface across providers
3. **Decorator Pattern**: Logging and timing decorators
4. **Repository Pattern**: Database abstraction layer

## Error Handling

The module implements comprehensive error handling:

- **ConfigurationError**: Missing or invalid configuration
- **ValidationError**: Invalid input data format
- **EmbeddingError**: Embedding generation failures
- **DatabaseError**: Database operation failures
- **RetryExhaustedError**: All retry attempts failed

All errors are logged with full stack traces and context.

## Logging

### Log Levels

- **DEBUG**: Skipped articles, detailed operations
- **INFO**: Processing start/end, category completion
- **WARNING**: Non-critical issues
- **ERROR**: Failures with full tracebacks
- **CRITICAL**: System-level failures

### Log Format (JSON)

```json
{
  "timestamp": "2025-11-21T10:30:45.123456",
  "level": "INFO",
  "module": "processor",
  "function": "process_category",
  "line": 42,
  "message": "Processing category: software_engineering",
  "extra_data": {
    "category": "software_engineering",
    "file_count": 5
  }
}
```

### Log Rotation

- File size limit: 10MB
- Backup count: 5 files
- Rotation: Automatic on size limit

## Cost Optimization

### Idempotency

The module checks if embeddings already exist before making API calls:

```python
if self.database.check_exists(url, category, embedding_date):
    # Skip - already embedded
    continue
```

This prevents:
- Duplicate API calls
- Unnecessary costs
- Processing time waste

### Batch Processing

Embeddings are generated in configurable batches:

```yaml
embedding:
  batch-size: 50  # Process 50 texts per API call
```

## Performance

- **Chunking**: ~1000 chunks/second
- **Embedding**: Depends on provider and batch size
- **Database**: ChromaDB with HNSW indexing for fast retrieval

## Code Quality

- **Type Hints**: All functions have complete type annotations
- **Docstrings**: Google-style docstrings for all public functions
- **Max Function Length**: 50 lines (enforced)
- **Max Line Length**: 100 characters
- **No Hardcoded Values**: All configuration externalized

## Testing

The module handles edge cases gracefully:

- Missing configuration files
- Invalid JSON data
- Network failures
- API rate limits
- Empty input directories
- Partial processing failures

## Contributing

When contributing, ensure:

1. All functions have type hints
2. All public functions have docstrings
3. Functions are under 50 lines
4. No hardcoded values
5. Comprehensive error handling
6. Tests for new features

## License

MIT License

## Support

For issues or questions, please open an issue on the repository.