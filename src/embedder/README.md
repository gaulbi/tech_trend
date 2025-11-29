# Embedder - Production RAG Embedding Pipeline

A production-grade Python module for chunking articles, generating embeddings, and storing them in ChromaDB with multi-provider support and idempotency.

## Features

- ✨ **Multi-Provider Support**: OpenAI, Voyage AI, Gemini, and Sentence Transformers
- 🔄 **Idempotency**: Automatically skips already-embedded articles to save costs
- 🛡️ **Robust Error Handling**: Exponential backoff, retry logic, and comprehensive validation
- 📊 **Batch Processing**: Efficient API usage with configurable batch sizes
- 🎯 **Type-Safe**: Full type hints and Google-style docstrings
- 📝 **Production-Ready**: Logging, monitoring, and graceful error handling

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create `.env` File

```bash
# OpenAI (if using OpenAI provider)
OPENAI_API_KEY=sk-...

# Voyage AI (if using Voyage provider)
VOYAGEAI_API_KEY=...

# Gemini (if using Gemini provider)
GEMINI_API_KEY=...
```

### 3. Ensure `config.yaml` Exists

Place your `config.yaml` in the project root (see Configuration section below).

## Usage

### Process Today's Articles

```bash
python embedder.py
```

### Process Specific Date (Backfill)

```bash
python embedder.py --date 2025-11-21
```

## Configuration

Example `config.yaml`:

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

## Input Format

Expected directory structure:

```
data/scraped-content/
└── 2025-11-21/
    ├── software-engineering-dev/
    │   ├── url-scrape.json
    │   └── web-scrape.json
    └── ai-ml/
        └── trends.json
```

JSON structure:

```json
{
  "analysis_date": "2025-11-21",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "Topic Name",
      "link": "https://example.com/article",
      "content": "Article content here...",
      "search_keywords": ["keyword1", "keyword2"]
    }
  ]
}
```

## Output

### ChromaDB Structure

- **Database Path**: `data/embedding/`
- **Collection**: `embeddings`
- **ID Format**: `{category}|{date}|{url_hash}|chunk_{index}`
- **Metadata**:
  - `url`: Article URL
  - `category`: Article category
  - `embedding_date`: Processing date
  - `source_file`: Source JSON file path
  - `chunk_index`: Chunk number

### Logs

Logs are stored in `log/embedding/embedder_YYYYMMDD_HHMMSS.log`

## Supported Embedding Providers

### OpenAI
```yaml
embedding-provider: openai
embedding-model: text-embedding-3-small  # or text-embedding-3-large
```

### Voyage AI
```yaml
embedding-provider: voyageai
embedding-model: voyage-large-2  # or voyage-code-2
```

### Google Gemini
```yaml
embedding-provider: gemini
embedding-model: models/text-embedding-004
```

### Sentence Transformers (Local)
```yaml
embedding-provider: sentence-transformers
embedding-model: all-MiniLM-L6-v2  # No API key needed
```

## Idempotency

The embedder automatically checks if an article (by URL, category, and date) has already been processed. If found, it skips embedding to save API costs and processing time.

## Error Handling

- **Exponential Backoff**: 1s, 3s, 5s delays between retries
- **Timeout**: Configurable timeout for all API calls
- **Validation**: Comprehensive input validation with detailed error messages
- **Graceful Degradation**: Continues processing remaining files on individual failures

## Architecture

```
embedder.py                 # CLI entry point
src/embedder/
├── config.py              # Configuration management
├── chunker.py             # Text chunking with overlap
├── database.py            # ChromaDB operations
├── processor.py           # Main orchestration
├── utils.py               # Helper functions
├── exceptions.py          # Custom exceptions
└── embedders/
    ├── base.py            # Abstract base class
    ├── factory.py         # Provider factory
    ├── openai_embedder.py
    ├── voyage_embedder.py
    ├── gemini_embedder.py
    └── sentence_transformer.py
```

## Development

### Code Quality Standards

- Maximum function length: 50 lines
- Type hints required for all functions
- Google-style docstrings
- Maximum line length: 100 characters
- No hardcoded values

### Adding New Providers

1. Create a new embedder class inheriting from `BaseEmbedder`
2. Implement `_embed_batch()` and `get_dimension()` methods
3. Register in `EmbedderFactory._providers`

Example:

```python
from .base import BaseEmbedder

class CustomEmbedder(BaseEmbedder):
    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Your implementation
        pass
    
    def get_dimension(self) -> int:
        return 768
```

## Troubleshooting

### "Configuration file not found"
Ensure `config.yaml` exists in the project root.

### "API key not found"
Check that your `.env` file contains the required API key for your chosen provider.

### "No categories found for date"
Verify that data exists at `{scraped_content_path}/{date}/` with category subdirectories.

### Rate Limiting
Reduce `batch-size` in config.yaml if hitting API rate limits.

## License

MIT License