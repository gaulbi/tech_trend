# Embedder

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture,  production-grade code and embedding for RAG.
**Tasks**: Generate a complete Python module implementation based on this plan.

---

## Module Overview

**Purpose**: Chunk articles, embed text, and store the embedding/chunk/metadata into a ChromaDB vector database. The module should be production-ready with comprehensive error handling, retry logic, and logging.
**Behavior**: Single-run batch processor. Defaults to processing **today's date**, but supports an optional date argument for backfilling.
**Idempotency**: Before embedding an article, check if its metadata.url already exists in the database. If it exists, skip to save API costs.

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
### CLI Argument (Optional)
- Support a `--date` argument (format YYYY-MM-DD).
- If not provided, default to `datetime.date.today().strftime('%Y-%m-%d')`.

#### File Path
`{scrape.url-scraped-content}/{TODAY_DATE}/{category}/*.json`

## Example
If today is 2025-11-21:
`data/scraped-content/2025-11-21/software-engineering-dev/url-scrape.json`
`data/scraped-content/2025-11-21/software-engineering-dev/web-scrape.json`

### JSON Structure
```json
{
  "analysis_date": "2025-11-21",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "...",
      "link": "...",
      "content": "...",
      "search_keywords": ["...", "..."]
    }
  ]
}
```

**Validation**: 
- Invalid JSON → Raise ValidationError and continue with remaining categories.
- No files for today's date → Log WARNING and exit gracefully.

---

## Output

### Vector Database
- Library: chromadb
- Persistence Path: `{embedding.database-path}`

### Database Schema (ChromaDB Metadata & ID)
- ID Format: `{category}|{TARGET_DATE}|{url_hash}|chunk_{chunk_index}` (Use a hash of the URL to ensure uniqueness)
- Document: The text chunk
- Metadata:
 - `url`: trends.link from input file
 - `category`: category from input file
 - `embedding_date`: {TARGET_DATE}
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

## Project Structure

```
.
├── embedder.py              # Main entry point
├── src/
│   └── embedder/            # Package
├── data/
│   └── embedding/           # ChromaDB database
│   └── scraped-content/    # ChromaDB database
├── config.yaml              # Configuration file
```

---

## Code Quality Standards

- **Max function length**: 50 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants

---

## Success Criteria

- Automatically processes only today's date without manual date input
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