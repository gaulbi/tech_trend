# Python Module Generation Prompt: Embed Scrapped Content with Embedding Model

You are an expert Python developer specializing in clean architecture, production-grade code, and embedding to vector database. Generate a complete, well-structured Python module with the following specifications:

---

## Module Overview

**Name**: Scrapped Content Embedder  
**Purpose**: Embed today's scrapped contents from Web using an embedding model to vector database. The module should be production-ready with comprehensive error handling, retry logic, and logging.

---

## Core Requirements

### 1. Multi-Embedding Model Provider Support
- Support multiple Embedding model providers: **OpenAI**, **Voyage AI**, **Gemini**, and **Sentence Transformers** (local)
- Use a **Factory Pattern** to create appropriate embedding clients
- All embedding clients must inherit from an **Abstract Base Class**
- Implement **exponential backoff retry logic** (3 retries: 1s, 3s, 5s delays)
- Configure **timeout** for all API calls (default: 60 seconds)
- Load API keys from **`.env` file** using `python-dotenv`

### 2. Database Schema in ChromaDB

```json
{
    # Document ID (unique identifier)
    "id": "domain-com_abc123_chunk_0",
    
    # Original text chunk
    "document": "This is the actual text content of the chunk...",
    
    # Embedding vector
    "embedding": [0.123, -0.456, 0.789, ...],  # 384 dimensions for all-MiniLM-L6-v2
    
    # Metadata (searchable/filterable)
    "metadata": {
        "url": "https://example.com/article",
        "source_file": "domain-com_abc123.json",
        "category": "Software Engineering Dev",
        "one_word_category": "software-engineering-dev",
        "embedding_date": "2025-11-21", 
        "chunk_index": 0,
        "total_chunks": 5
    }
}
```

### 3. Configuration Management
All settings must be loaded from `config.yaml`:

**Example**
```yaml
scrap:
  url-scrapped-content: data/scrapped-content #scrapped_content_base_path
embedding:
  chunk-size: 1000
  chunk-overlap: 200
  embedding-provider: openai
  embedding-model: text-embedding-3-small
  timeout: 60
  database-path: data/embedding #embedding_base_path
```


### 4. Scrappd Content

#### File Path
```
{scrapped_content_base_path}/{YYYY-MM-DD}/{category}/url-scrap.json
{scrapped_content_base_path}/{YYYY-MM-DD}/{category}/web-scrap.json
```

**Example**: 
If the execution date is `2025-11-21` and category is `Software Engineering Dev`, content file paths are below.
`data/scrapped-content/2025-11-21/software-engineering-dev/url-scrap.json`
`data/scrapped-content/2025-11-21/software-engineering-dev/web-scrap.json`

#### Content Schema
Use `content` property for chunking and embedding.

**Example**
```json
{
  "analysis_timestamp": "2025-11-22T08:02:55.816247",
  "source_file": "ai-chips-ai-hardware-infrastructure.json",
  "category": "AI Chips / AI Hardware / Infrastructure",
  "trends": [
    {
      "topic": "Intel’s Panther Lake CPUs and 18A process ramp in Oregon",
      "link": "https://www.tomshardware.com/pc-components/cpus/the-panther-stalks-intels-panther-lake-cpus-set-to-take-off-in-oregon-company-reveals-and-cutting-edge-18a-process-is-on-track",
      "content": "The Panther stalks: Intel’s Panther Lake CPUs set to take off in Oregon, company reveals, and ...,
      "scrape_timestamp": "2025-11-22T15:35:58.679586",
      "error": null
    }
  ]
}
```

### 5. Processing Logic
- Read **Today's** scrapped content file**s** from scrapped_content_base_path. 
- Chunk all content files in scrapped_content_base_path. If it's possible, use opensource python package instead of create logic by yourself. (such as langchan or LlamaIndex)
- Create database using a catatory into ChromaDB. If catatory is `Software Engineering Dev`, database name is `software-engieering-dev`.
- Insert/Update vector embedding to the created database in embedding_base_path.
- **Continue processing** remaining feeds even if one fails (error isolation)
- Generate detailed summary report at completion

---

## Project Structure

```
.
├── scrapped_content_embedder.py              # Main entry point
├── src/
│   └── scrapped_content_embedder/            # Package
├── data/
│   └── embedding/                      # ChromaDB database
├── .env                                # API keys (gitignored)
├── config.yaml                         # Configuration file
```

---

## Technical Requirements

### Code Quality Standards
1. **Clean Architecture**: Separation of concerns (config, clients, business logic)
2. **SOLID Principles**: Single responsibility, dependency injection, abstractions
3. **Type Hints**: Comprehensive type annotations throughout
4. **Docstrings**: Every class, method, and function documented
5. **Error Handling**: Try-catch blocks with specific exception handling
6. **Logging**: Structured logging using Python's `logging` module
7. **DRY Principle**: No code duplication

### Production-Grade Features
1. **Retry Logic**: Exponential backoff for all LLM API calls
2. **Timeout Handling**: Configurable timeouts to prevent hanging
3. **Graceful Degradation**: Continue processing if one feed fails
4. **Comprehensive Logging**: INFO level for progress, ERROR for failures
5. **API Key Management**: Load from `.env` file with validation
6. **JSON Parsing Safety**: Handle malformed LLM responses gracefully
7. **Directory Auto-Creation**: Create output directories as needed

### Error Handling Requirements
- Handle JSON parsing errors in feed files
- Handle JSON parsing errors in LLM responses
- Handle network failures and timeouts
- Log all errors with context (filename, operation, error details)
- Generate error summary in final report

---

## Environment Setup (.env file)

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# DeepSeek API Key
DEEPSEEK_API_KEY=sk-...

# Claude (Anthropic) API Key
CLAUDE_API_KEY=sk-ant-...

# Ollama does not require an API key
```

---
