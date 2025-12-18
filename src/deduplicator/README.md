# Semantic Deduplicator

A production-grade Python module for filtering tech trend keywords using semantic similarity and vector search to prevent duplicate article generation.

## Features

- **Multi-Provider Embedding Support**: OpenAI, Voyage AI, Gemini, and Sentence Transformers
- **Semantic Deduplication**: Uses cosine similarity with configurable threshold
- **Persistent History**: ChromaDB vector database for trend history
- **Idempotent Processing**: Automatically skips already processed categories
- **Robust Error Handling**: Exponential backoff retry logic with comprehensive logging
- **Production-Ready**: Type hints, docstrings, structured logging, and clean architecture

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your API keys
```

## Configuration

Create a `config.yaml` file (see project documentation for full schema):

```yaml
deduplication:
  history-keywords: data/history_keywords
  collection-name: history_keywords
  dedup-analysis-report: data/dedup-tech-trend-analysis
  similarity-threshold: 0.85
  lookback-days: 7
  target-count: 1
  log: log/deduplication
  embedding-provider: openai
  embedding-model: text-embedding-3-small
  timeout: 60
  max-retries: 3

tech-trend-analysis:
  analysis-report: data/tech-trend-analysis
```

## Usage

```bash
# Process all categories for today
python deduplicator.py

# Process specific date
python deduplicator.py --feed_date "2025-02-01"

# Process specific category
python deduplicator.py --category "software_engineering"

# Process specific date and category
python deduplicator.py --feed_date "2025-02-01" --category "software_engineering"
```

## Architecture

```
src/deduplicator/
├── __init__.py           # Package initialization
├── core.py               # Main pipeline logic
├── config.py             # Configuration management
├── exceptions.py         # Custom exceptions
├── logger.py             # Logging utilities
├── models.py             # Data models
├── storage.py            # ChromaDB integration
├── io_handler.py         # File I/O operations
└── embeddings/           # Embedding providers
    ├── __init__.py
    ├── base.py           # Abstract base class & factory
    ├── openai_provider.py
    ├── voyageai_provider.py
    ├── gemini_provider.py
    └── sentence_transformers_provider.py
```

## How It Works

1. **Input**: Reads trend analysis JSON files from `data/tech-trend-analysis/{date}/{category}.json`
2. **Deduplication**:
   - Sorts trends by impact score
   - Generates embeddings for each trend
   - Queries ChromaDB for similar trends within lookback period
   - Selects unique trends based on similarity threshold
3. **Output**: Writes deduplicated trends to `data/dedup-tech-trend-analysis/{date}/{category}.json`
4. **History**: Records selected trends to ChromaDB for future comparisons

## Embedding Providers

### OpenAI
```bash
export OPENAI_API_KEY=sk-...
```

### Voyage AI
```bash
export VOYAGEAI_API_KEY=...
```

### Gemini
```bash
export GEMINI_API_KEY=...
```

### Sentence Transformers (Local)
No API key needed - runs locally.

## Logging

Logs are written to `log/deduplication/` with:
- Daily rotation (30-day retention)
- JSON format for file logs
- Colored console output
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Error Handling

- **ConfigurationError**: Missing or invalid configuration
- **ValidationError**: Invalid input JSON (processing continues for other categories)
- **EmbeddingError**: API failures with exponential backoff retry
- **DatabaseError**: ChromaDB operation failures

## Idempotency

The system automatically skips categories that have already been processed for a given date, ensuring safe re-runs without duplicating work.

## Code Quality

- Type hints on all functions
- Google-style docstrings
- Max function length: 50 lines
- Max line length: 100 characters
- Clean architecture with separation of concerns
- Factory pattern for embedding providers
- Abstract base classes for extensibility
