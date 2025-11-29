# Python Module Generation Prompt: Generate Tech Trend Article with LLM

You are an expert Python developer specializing in clean architecture, production-grade code, and LLM integration. Generate a complete, well-structured Python module with the following specifications:

---

## Module Overview

**Name**: Article Generator  
**Purpose**: Generate today's technology trend articles using Large Language Models (LLM) to educate readers in technology fields. The module should be production-ready with comprehensive error handling, retry logic, and logging. Read **Process** and follow it.

---

## Process
1. Read metadata from analysis files and perform similarity search against ChromaDB- Refer **Similarity Search**
2. Craft Prompt with Context
3. Pass prompt and context to LLM to generate an article.
4. **Continue processing** remaining feeds even if one fails (error isolation)
5. Generate detailed summary report at completion

---

## Detail Instructions

### Similarity Search
- Read Technical Trend Analysis files. (find file path in **File Path Structure**)
- Retrieve top N (ktop in config.yaml) chunks by 
  - Similarity search: reason property in analysis file.
  - File Path: {catagory} - ChromaDB Schema:`category`
  - File Path: {YYYY-MM-DD} - ChromaDB Schema:`one_word_category`

### Craft Prompt with Context
- Read a system prompt and a user prompt in system_prompt_base_path and user_prompt_base_path) 
- Replace {{context}} with the list of chunks retrieved from **Similarity Search**
- Replace {{{{keywords}}}} with a reason property in analysis file.
- Merge system prompt and user prompt. 

## Generate Tech Trend Article
- Pass the prompt with context generated from **Craft Prompt with Context**
- Store the response from LLM in md file. **Tech Trend Article**

## Reference
### Configuration Management
All settings must be loaded from `config.yaml`:

**Example**
```yaml
llm:
  server: openai
  llm-model: gpt-5.1
  timeout: 60
tech-trend-analysis:
  analysis-report: data/tech-trend-analysis     # tech_trend_analysis_base_path
article-generator:
  system-prompt: prompt/article-system-prompt.md   # system_prompt_base_path
  user-prompt: prompt/article-user-prompt.md      # user_prompt_base_path
  tech-trend-article: data/tech-trend-article   # tech_trend_article_output_base_path
embedding:
  chunk-size: 1000
  chunk-overlap: 200
  embedding-provider: openai  
  embedding-model: text-embedding-3-small
  timeout: 60
  max-retries: 3
  batch-size: 50  
  database-path: data/embedding                 # embedding_base_path
  ktop: 20
```

### Tech Trend Article
```
{tech_trend_article_output_base_path}/{YYYY-MM-DD}/{category}.md
```

**File Path Example**: 
If the execution date is `2025-11-21` and category is `Software Engineering Dev`, analysis file path is below.
`data/tech-trend-article/2025-11-21/software-engineering-dev.md`

### ChromaDB Schema
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

### Analysis Schema

```json
{
  "analysis_timestamp": "2025-11-22T08:02:45.474628",
  "source_file": "ai-machine-learning.json",
  "category": "AI / Machine Learning",
  "trends": [
    {
      "topic": "Google Gemini 3 launch and early developer adoption",
      "reason": "Google’s release of Gemini 3, including its new 'vibe‑coded' response style and built‑in agent, is a ...",
      "category": "AI / Machine Learning",
      "links": [
        "https://www.technologyreview.com/2025/11/18/1128065/googles-gemini-3/"
      ],
      "search_keywords": [
        "Google Gemini 3 launch"
      ]
    }
  ]
}
```

---

## IMPORTANT
- Support multiple LLM providers: **OpenAI**, **DeepSeek**, **Claude (Anthropic)**, and **Ollama** (local)
- Use a **Factory Pattern** to create appropriate LLM clients
- All LLM clients must inherit from an **Abstract Base Class**
- Support multiple Embedding model providers: **OpenAI**, **Voyage AI**, **Gemini**, and **Sentence Transformers** (local)
- Use a **Factory Pattern** to create appropriate embedding clients
- All embedding clients must inherit from an **Abstract Base Class**
- Implement **exponential backoff retry logic** (3 retries: 1s, 3s, 5s delays)
- Configure **timeout** for all API calls (default: 60 seconds)
- Load API keys from **`.env` file** using `python-dotenv`

---

## Project Structure

```
.
├── article_generator.py              # Main entry point
├── src/
│   └── article_generator/            # Package
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