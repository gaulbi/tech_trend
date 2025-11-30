# Article Generator

A production-grade Python application for batch processing technology trends into educational articles using LLMs and RAG.

## Features

- **Batch Processing**: Automatically processes all trends for the current date
- **Idempotency**: Skips already-generated articles to save costs
- **RAG Integration**: Uses ChromaDB for context-aware article generation
- **Multi-Provider Support**: Works with OpenAI, DeepSeek, Claude, and Ollama
- **Flexible Embeddings**: Supports OpenAI, VoyageAI, Gemini, and local sentence-transformers
- **Robust Error Handling**: Exponential backoff, timeouts, and comprehensive logging
- **Clean Architecture**: Factory pattern, type hints, and modular design

---

## ✅ CODE QUALITY EVALUATION (POST-REWRITE)

### CRITICAL Issues - ✅ ALL RESOLVED

1. ✅ **chromadb Import Fixed**
   - Changed from `chromadb.config.Settings` to `chromadb.Settings`
   - Application will now start correctly

2. ✅ **Conditional Imports Implemented**
   - All optional dependencies (anthropic, voyageai, google-generativeai, sentence-transformers) now use lazy imports
   - Imports moved inside `__init__` methods with try-except blocks
   - Clear error messages guide users to install missing packages
   - Application loads successfully even without optional packages

3. ✅ **Optional Dependencies Documented**
   - requirements.txt now clearly marks optional vs required packages
   - Installation guide included with specific commands

### HIGH PRIORITY Issues - ✅ ALL RESOLVED

4. ✅ **Logger Extra Data Fixed**
   - Removed nested `extra={"extra_data": {...}}` pattern
   - Now passes extra fields directly: `extra={"key": "value"}`
   - JSONFormatter updated to properly extract all non-standard fields from record.__dict__
   - Includes `default=str` for JSON serialization of complex types

5. ✅ **ChromaDB Query Syntax Verified**
   - Changed from `{"category": {"$eq": value}}` to `{"category": value}`
   - Simplified syntax is more compatible with ChromaDB v0.4.0+
   - Where clause uses straightforward field matching

### MEDIUM Issues - ✅ ALL RESOLVED

6. ✅ **Trend Validation Added**
   - New `validate_trend()` method checks required fields exist
   - Validates `topic` and `reason` are present and non-empty
   - Logs warnings for invalid trends and skips processing
   - Returns early if validation fails

7. ℹ️ **API Key Validation Timing**
   - Still validated at provider instantiation (acceptable design)
   - Fails fast with clear error messages
   - No change needed - this is appropriate for factory pattern

8. ℹ️ **ValidationError Export**
   - Kept in main script (not exported from package)
   - This is acceptable as it's only used internally
   - External users don't need to catch this exception

---

## ✨ ADDITIONAL IMPROVEMENTS

- **Better Error Messages**: All ImportError messages now include installation instructions
- **Type Safety**: All functions maintain complete type hints
- **JSON Logging**: Fixed to properly capture all extra fields dynamically
- **Code Organization**: Import statements cleaned up (removed unused imports at module level)
- **Regex Import**: Moved `import re` inside `slugify()` function to keep it localized

---

## Project Structure

```
├── article_generator.py              # Main script entry point
├── src/
│   └── article_generator/
│       ├── __init__.py
│       ├── config.py                 # Configuration loader
│       ├── factories.py              # LLM & embedding factories
│       ├── rag_engine.py             # ChromaDB handler
│       └── utils.py                  # Utilities (logger, slugify, etc.)
├── data/
│   ├── embedding/                    # ChromaDB persistence
│   ├── tech-trend-analysis/          # Input JSON files
│   └── tech-trend-article/           # Generated articles
├── prompt/
│   ├── article-system-prompt.md      # System prompt template
│   └── article-user-prompt.md        # User prompt template
├── log/
│   └── article-generator/            # JSON logs
├── .env                              # API keys
├── config.yaml                       # Configuration
└── requirements.txt
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd article-generator
   ```

2. **Install base dependencies**
   ```bash
   pip install pydantic pyyaml python-dotenv openai chromadb
   ```

3. **Install optional providers** (only if needed)
   ```bash
   # For Claude support
   pip install anthropic
   
   # For VoyageAI embeddings
   pip install voyageai
   
   # For Gemini embeddings
   pip install google-generativeai
   
   # For local embeddings
   pip install sentence-transformers torch transformers
   ```

4. **Configure environment variables**
   
   Create a `.env` file:
   ```bash
   OPENAI_API_KEY=sk-...
   DEEPSEEK_API_KEY=sk-...
   CLAUDE_API_KEY=sk-ant-...
   VOYAGEAI_API_KEY=...
   GEMINI_API_KEY=...
   ```

5. **Configure application**
   
   Edit `config.yaml` to match your setup (see Configuration section).

## Configuration

The `config.yaml` file controls all aspects of the application:

```yaml
llm:
  server: openai                              # openai, deepseek, claude, ollama
  llm-model: gpt-4o
  timeout: 60
  retry: 3

tech-trend-analysis:
  analysis-report: data/tech-trend-analysis

article-generator:
  system-prompt: prompt/article-system-prompt.md
  user-prompt: prompt/article-user-prompt.md
  tech-trend-article: data/tech-trend-article
  log: log/article-generator

embedding:
  embedding-provider: openai                  # openai, voyageai, gemini, sentence-transformers
  embedding-model: text-embedding-3-small
  timeout: 60
  max-retries: 3
  database-path: data/embedding
  ktop: 20
```

## Usage

### Basic Usage

Run the article generator:

```bash
python article_generator.py
```

The script will:
1. Scan for JSON files in `data/tech-trend-analysis/{TODAY_DATE}/`
2. Process each trend in each category
3. Skip trends that already have generated articles
4. Use RAG to retrieve relevant context
5. Generate articles using configured LLM
6. Save articles to `data/tech-trend-article/{TODAY_DATE}/{category}/{slug}.md`

### Input Format

Place JSON files in `data/tech-trend-analysis/{YYYY-MM-DD}/`:

```json
{
  "analysis_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "Agentic AI Patterns",
      "reason": "Rising popularity in enterprise automation...",
      "links": ["https://example.com"],
      "search_keywords": "AI Agents, Automation"
    }
  ]
}
```

### Prompt Templates

Create two prompt files:

**prompt/article-system-prompt.md**:
```markdown
You are an expert technical writer specializing in technology trends.
Your task is to create comprehensive, educational articles.
```

**prompt/article-user-prompt.md**:
```markdown
Write an educational article about the following trend.

## Context
{{context}}

## Topic Details
Keywords: {{search_keywords}}
Reason: {{reason}}

Please write a comprehensive article...
```

Variables `{{context}}`, `{{search_keywords}}`, and `{{reason}}` are automatically injected.

## Logging

Logs are written in JSON format to:
```
log/article-generator/article-generator-{YYYY-MM-DD}.log
```

Each log entry includes:
- Timestamp
- Log level (INFO, WARNING, ERROR)
- Message
- Module, function, and line number
- Additional context (file paths, counts, errors)

Example log entry:
```json
{
  "timestamp": "2025-11-29 10:30:45,123",
  "level": "INFO",
  "message": "Article generated successfully: Agentic AI Patterns",
  "module": "article_generator",
  "function": "process_trend",
  "line": 234,
  "output_path": "data/tech-trend-article/2025-11-29/software_engineering/agentic-ai-patterns.md",
  "category": "software_engineering"
}
```

## Error Handling

The application implements robust error handling:

- **Network Errors**: 3 retry attempts with exponential backoff (1s, 2s, 4s)
- **Timeouts**: 60-second timeout for all API calls
- **Validation Errors**: Malformed JSON files are logged and skipped
- **Missing Configuration**: Application exits with clear error message
- **File Errors**: Individual trends that fail are logged but don't stop processing
- **Missing Dependencies**: Clear ImportError messages with installation instructions

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

The codebase follows strict quality standards:
- Maximum function length: 50 lines
- Type hints on all functions
- Google-style docstrings
- Maximum line length: 100 characters
- No hardcoded values

### Adding New LLM Providers

1. Create a new client class in `factories.py`:
   ```python
   class NewProviderLLMClient(BaseLLMClient):
       def __init__(self, model: str, timeout: int, max_retries: int):
           super().__init__(model, timeout, max_retries)
           # Initialize your client
       
       def generate(self, system_prompt: str, user_prompt: str) -> str:
           # Implement generation logic
           pass
   ```

2. Register in `LLMFactory`:
   ```python
   providers = {
       "newprovider": NewProviderLLMClient,
       # ... existing providers
   }
   ```

3. Update `.env` and configuration

### Adding New Embedding Providers

Follow the same pattern as LLM providers, implementing `BaseEmbeddingClient`.

## Troubleshooting

### ChromaDB Collection Empty

Ensure embeddings are populated before running article generation:
```python
from src.article_generator import RAGEngine
engine = RAGEngine("data/embedding", embedding_client)
stats = engine.get_collection_stats()
print(stats)  # Should show total_documents > 0
```

### API Key Errors

Verify all required API keys are in `.env`:
```bash
cat .env | grep API_KEY
```

### Memory Issues with Sentence Transformers

For local embeddings, consider using a smaller model:
```yaml
embedding:
  embedding-provider: sentence-transformers
  embedding-model: all-MiniLM-L6-v2  # Smaller, faster model
```

### Missing Optional Dependencies

If you see an ImportError, install the required package:
```bash
# Error: "anthropic package required for Claude"
pip install anthropic

# Error: "voyageai package required for VoyageAI"
pip install voyageai

# Error: "google-generativeai package required for Gemini"
pip install google-generativeai

# Error: "sentence-transformers package required"
pip install sentence-transformers torch transformers
```

## License

MIT License