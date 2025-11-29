# Tech Trend Article Generator

A production-grade Python module for generating technology trend articles using Large Language Models (LLMs) and ChromaDB for semantic search.

## Features

- **Multi-Provider LLM Support**: OpenAI, DeepSeek, Claude (Anthropic), and Ollama (local)
- **Multi-Provider Embeddings**: OpenAI, Voyage AI, Gemini, and Sentence Transformers (local)
- **Clean Architecture**: SOLID principles, Factory pattern, Abstract base classes
- **Production-Ready**: Comprehensive error handling, retry logic, logging
- **Error Isolation**: Continues processing remaining files even if one fails
- **Semantic Search**: ChromaDB integration for context retrieval
- **Configurable**: YAML-based configuration management

## Project Structure

```
.
├── article_generator.py              # Main entry point
├── src/
│   └── article_generator/            # Package
│       ├── __init__.py
│       ├── config_loader.py          # Configuration management
│       ├── article_service.py        # Main business logic
│       ├── chromadb_service.py       # ChromaDB operations
│       ├── prompt_service.py         # Prompt management
│       ├── llm_client_base.py        # LLM base class & factory
│       ├── llm_clients.py            # LLM implementations
│       ├── embedding_client_base.py  # Embedding base class & factory
│       ├── embedding_clients.py      # Embedding implementations
│       └── report_generator.py       # Summary reports
├── config.yaml                       # Configuration file
├── .env                              # API keys (gitignored)
├── .env.example                      # Environment template
├── requirements.txt                  # Dependencies
└── README.md                         # This file
```

## Revisions Made

### Critical Fixes:
1. ✅ **Added `src/__init__.py`** - Package structure now complete
2. ✅ **Fixed ChromaDB query** - Corrected metadata filter syntax with `$and` operator
3. ✅ **Fixed date extraction** - Now correctly extracts from parent directory
4. ✅ **Improved error isolation** - Returns empty list on search failure to continue processing
5. ✅ **Enhanced prompt merging** - System and user prompts properly combined per spec

### Improvements:
- Better logging with success/failure indicators (✓/✗)
- Fallback logic when date filter returns no results
- More detailed error messages
- Validation script to verify implementation

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd article-generator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Configure application**
   ```bash
   # Edit config.yaml to match your setup
   ```

6. **Validate installation** (optional)
   ```bash
   python validate_implementation.py
   ```

## Configuration

### config.yaml

```yaml
llm:
  server: openai              # LLM provider
  llm-model: gpt-4            # Model name
  timeout: 60                 # Timeout in seconds

tech-trend-analysis:
  analysis-report: data/tech-trend-analysis

article-generator:
  system-prompt: prompt/article-system-prompt.md
  user-prompt: prompt/article-user-prompt.md
  tech-trend-article: data/tech-trend-article

embedding:
  chunk-size: 1000
  chunk-overlap: 200
  embedding-provider: openai
  embedding-model: text-embedding-3-small
  timeout: 60
  max-retries: 3
  batch-size: 50
  database-path: data/embedding
  ktop: 20
```

### .env

```bash
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...
VOYAGE_API_KEY=...
GEMINI_API_KEY=...
```

## Usage

### Basic Usage

```bash
python article_generator.py
```

### Expected Directory Structure

```
data/
├── tech-trend-analysis/
│   └── 2025-11-21/
│       └── ai-machine-learning.json
├── embedding/
│   └── chroma.sqlite3
└── tech-trend-article/
    └── 2025-11-21/
        └── ai-machine-learning.md

prompt/
├── article-system-prompt.md
└── article-user-prompt.md
```

### Analysis File Format

```json
{
  "analysis_timestamp": "2025-11-22T08:02:45.474628",
  "source_file": "ai-machine-learning.json",
  "category": "AI / Machine Learning",
  "trends": [
    {
      "topic": "Google Gemini 3 launch",
      "reason": "Google's release of Gemini 3...",
      "category": "AI / Machine Learning",
      "links": ["https://example.com/article"],
      "search_keywords": ["Google Gemini 3"]
    }
  ]
}
```

## Features in Detail

### LLM Providers

#### OpenAI
```yaml
llm:
  server: openai
  llm-model: gpt-4
```

#### DeepSeek
```yaml
llm:
  server: deepseek
  llm-model: deepseek-chat
```

#### Claude (Anthropic)
```yaml
llm:
  server: claude
  llm-model: claude-3-opus-20240229
```

#### Ollama (Local)
```yaml
llm:
  server: ollama
  llm-model: llama2
```

### Embedding Providers

#### OpenAI
```yaml
embedding:
  embedding-provider: openai
  embedding-model: text-embedding-3-small
```

#### Voyage AI
```yaml
embedding:
  embedding-provider: voyage
  embedding-model: voyage-2
```

#### Gemini
```yaml
embedding:
  embedding-provider: gemini
  embedding-model: models/embedding-001
```

#### Sentence Transformers (Local)
```yaml
embedding:
  embedding-provider: sentence-transformers
  embedding-model: all-MiniLM-L6-v2
```

### Error Handling

The system includes comprehensive error handling:

- **Retry Logic**: Exponential backoff (1s, 3s, 5s delays)
- **Timeout Handling**: Configurable timeouts for all API calls
- **Error Isolation**: Continues processing if one file fails
- **Graceful Degradation**: Logs errors and generates summary report

### Logging

Logs are written to:
- `stdout` (console)
- `article_generator.log` (file)

Log levels:
- `INFO`: Progress updates
- `WARNING`: Non-critical issues
- `ERROR`: Failures with stack traces

## Example Output

```
================================================================================
ARTICLE GENERATION SUMMARY REPORT
================================================================================
Total Files Processed: 3
Successful: 2
Failed: 1

SUCCESSFUL GENERATIONS:
--------------------------------------------------------------------------------
✓ ai-machine-learning.json (AI / Machine Learning)
  Output: data/tech-trend-article/2025-11-21/ai-machine-learning.md
  Trends: 1

✓ software-engineering-dev.json (Software Engineering Dev)
  Output: data/tech-trend-article/2025-11-21/software-engineering-dev.md
  Trends: 1

FAILED GENERATIONS:
--------------------------------------------------------------------------------
✗ cloud-infrastructure.json (Cloud Infrastructure)
  Error: Similarity search failed: Collection not found

STATISTICS:
--------------------------------------------------------------------------------
Success Rate: 66.7%
Total Trends Processed: 2
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
```

### Type Checking
```bash
mypy src/
```

## Troubleshooting

### ChromaDB Collection Not Found
- Ensure ChromaDB is populated with embeddings
- Check collection naming matches category format

### API Key Errors
- Verify API keys in `.env` file
- Check key has proper permissions

### Timeout Errors
- Increase timeout in `config.yaml`
- Check network connectivity

## License

MIT License

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues and questions, please open a GitHub issue.