# ============================================================================
# README.md
# ============================================================================
# Article Generator

Production-grade Python application for generating technology trend articles 
using Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG).

## Features

- **Multi-Provider LLM Support**: OpenAI, DeepSeek, Claude, Ollama
- **Flexible Embedding**: OpenAI, VoyageAI, Gemini, SentenceTransformers
- **RAG with ChromaDB**: Vector-based context retrieval
- **Advanced Logging**: JSON structured logging with color console output
- **Resilient Network Calls**: Exponential backoff and timeout handling
- **Clean Architecture**: Factory pattern, dependency injection

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env` and add API keys
2. Configure `config.yaml` with your settings

## Usage

```bash
# Process all categories for today
python article-generator.py

# Process specific category
python article-generator.py --category software_engineering

# Process specific date
python article-generator.py --feed_date 2025-02-01

# Process top N trends (by score)
python article-generator.py --cnt 5

# Overwrite existing articles
python article-generator.py --overwrite

# Combine options
python article-generator.py --category ai --feed_date 2025-02-01 --cnt 3
```

## Project Structure

```
├── article-generator.py          # Entry point
├── src/
│   └── article_generator/
│       ├── __init__.py
│       ├── cli.py                # CLI interface
│       ├── config.py             # Configuration management
│       ├── exceptions.py         # Custom exceptions
│       ├── logger.py             # Advanced logging
│       ├── processor.py          # Main processor
│       ├── clients/
│       │   ├── base.py           # Abstract base classes
│       │   ├── llm_clients.py    # LLM implementations
│       │   ├── embedding_clients.py
│       │   └── factories.py      # Factory pattern
│       ├── rag/
│       │   └── retriever.py      # RAG retriever
│       └── utils/
│           └── text_utils.py     # Text utilities
├── data/
│   ├── embedding/                # ChromaDB database
│   ├── tech-trend-analysis/      # Input data
│   └── tech-trend-article/       # Generated articles
├── prompt/
│   ├── article-system-prompt.md
│   └── article-user-prompt.md
├── log/                          # Log files
├── config.yaml
├── .env
└── requirements.txt
```

## Logging

Logs are written to:
- **Console**: Colored output for easy reading
- **File**: JSON structured logs in `log/article-generator-{date}.log`

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Error Handling

- Network timeouts: 60 seconds
- Retry logic: 3 attempts with exponential backoff
- All errors logged with full traceback
- Processing continues even if individual trends fail

## License

MIT License