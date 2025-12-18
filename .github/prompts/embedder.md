# Embedder

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture,  production-grade code and embedding for RAG.
**Tasks**: Generate a complete Python module implementation based on this plan.

---

## Module Overview

**Purpose**: Chunk articles, embed text, and store the embedding/chunk/metadata into a ChromaDB vector database. The module should be production-ready with comprehensive error handling, retry logic, and logging.

### Feed Date
- If `--feed_date` argument is not specified in command, use today's date as the feed date.
- In this case, determine today's date using `datetime.date.today().strftime('%Y-%m-%d')`

---

## Configuration

### File: `./config.yaml`
```yaml
scrape:
  url-scraped-content: data/scraped-content   # base input folder
embedding:
  chunk-size: 1000
  chunk-overlap: 200
  embedding-provider: openai                  # openai, voyageai, gemini, sentence-transformers
  embedding-model: text-embedding-3-small
  timeout: 60
  max-retries: 3
  batch-size: 50                              # Number of texts to embed in one API call
  database-path: data/embedding               # base embedding folder
  ktop: 20
  log: log/embedding
```

**Validation**: Missing config.yaml → Raise `ConfigurationError` and exit

---

## Input

### File Path
`{scrape.url-scraped-content}/{FEED_DATE}/{category}/*.json`

## Example
If a feed date is 2025-11-21 and a category is software_engineering:
`data/scraped-content/2025-11-21/software_engineering/url-scrape.json`
`data/scraped-content/2025-11-21/software_engineering/web-scrape.json`

### JSON Structure
```json
{
  "feed_date": "2025-11-21",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "...",
      "query_used": "...",
      "search_link": "...",
      "content": "...",
    }
  ]
}
```

**Validation**: Invalid JSON → Raise `ValidationError` and continue processing remaining categories.

---

## Output

### Vector Database
- Library: chromadb
- Persistence Path: `{embedding.database-path}`

### Database Schema (ChromaDB Metadata & ID)
- ID Format: `{category}|{FEED_DATE}|{url_hash}|chunk_{chunk_index}` (Use a hash of the URL to ensure uniqueness)
- Document: The text chunk
- Metadata:
 - `url`: trends.search_link from input file
 - `category`: category from input file
 - `embedding_date`: {FEED_DATE}
 - `source_file`: Full path to input JSON
 - `chunk_index`: Integer

---

## Multi-Embedding Model Provider Support
- Support multiple Embedding model providers: **OpenAI**, **Voyage AI**, **Gemini**, and **Sentence Transformers** (local)
- Use a **Factory Pattern** to create appropriate embedding clients
- All embedding clients must inherit from an **Abstract Base Class**
- Implement **exponential backoff retry logic** (3 retries: 1s, 3s, 5s delays)
- Configure **timeout** for all API calls (default: 60 seconds)
- Load API keys from **`.env` file**

---

## Logging
```json
{
  "timestamp": "ISO format",
  "level": "ERROR",
  "module": "module_name",
  "function": "function_name", 
  "line": 42,
  "message": "Error message",
  "traceback": "full traceback for errors"
}
```
1. Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
2. Console output with colors for different levels
3. Rotating file handler with 10MB limit keeping 5 backup files
4. JSON formatting option for structured logging
5. Function decorator to auto-log calls with timing
6. Error logging helper that captures stack traces
7. Configurable via environment variables or config file
8. Include example usage showing:
   - Basic logging
   - Function tracing
   - Error handling with context
   - Conditional debug logging

### Levels
- **INFO**: Fetch start/end, category completion
- **ERROR**: Network/parsing failures
- **DEBUG**: Skipped articles

### Rotation
- Daily rotation, keep 30 days

---

## Project Structure

```
.
├── embedder.py              # Main entry point
├── src/
│   └── embedder/            # Package
├── data/
│   └── embedding/           # ChromaDB database
│   └── scraped-content/
│       └── {FEED_DATE}/      # Only write to this directory
├── config.yaml              # Configuration file
```

- DO NOT implement any logic in `wiki-search.py`. It's only for entry point.

### Entry Point
```bash
python embedder.py

python embedder.py --category "software_engineering"

python embedder.py --feed_date "2025-02-01"

python embedder.py --category "software_engineering" --feed_date "2025-02-01"
```
**category** and **feed_date** are optional input parameters.

---

## Code Quality Standards

- **Max function length**: 50 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants

---

## Success Criteria

- Read, chunk, embed and store successfully for today's categories
- Cost-Saving Idempotency: Checks if `metadata.url`, `metadata.category` and `embedding_date` exist in DB before calling Embedding API.
- All code has type hints and docstrings
- Graceful handling when no input data exists for today

---

## Implementation Notes

### DO NOT GENERATE
- `config.yaml` (provided at runtime)
- Test files

## Environment Setup (.env file)

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Voyage AI
VOYAGEAI_API_KEY=...

# Gemini API Key
GEMINI_API_KEY=...
```

---