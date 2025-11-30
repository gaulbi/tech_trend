# Article Generator

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture, production-grade code, RAG, and GenAI.
**Tasks**: Generate a complete Python module implementation based on this plan.

---

## Module Overview

**Purpose**: Batch process **today's** technology trends into educational articles using LLMs and RAG.
**Execution**: The script scans the input directory for all JSON files associated with **today's date**, iterates through every trend, and generates unique articles.
**Idempotency**: Before processing a specific trend, check if the corresponding output file already exists. If yes, skip to save costs.

---
## Configuration

### File: `./config.yaml`
```yaml
llm:
  server: openai
  llm-model: gpt-5.1
  timeout: 60
  retry: 3
tech-trend-analysis:
  analysis-report: data/tech-trend-analysis         # tech_trend_analysis_base_path
article-generator:
  system-prompt: prompt/article-system-prompt.md    # system_prompt_base_path
  user-prompt: prompt/article-user-prompt.md        # user_prompt_base_path
  tech-trend-article: data/tech-trend-article       # base output folder
  log: log/article-generator
embedding:
  embedding-provider: openai                        # openai, voyageai, gemini, sentence-transformers
  embedding-model: text-embedding-3-small
  timeout: 60
  max-retries: 3
  database-path: data/embedding
  ktop: 20
```

**Validation**: Missing config.yaml → Raise `ConfigurationError` and exit

---

## Process Workflow

1. **Discovery**: Scan the folder {tech-trend-analysis.analysis-report}/{TODAY_DATE}/ for all *.json files
2. **File Iteration**: For each JSON file (representing a Category):
- Load the JSON content.
- Extract the category string.
- Iterate through the trends list.
3. **Trend Processing (The Loop)**: For each trend object:
- **Path Check**: Construct the output path. If file exists -> SKIP.
- **RAG Retrieval**: Query ChromaDB using the trend's details.
- **Prompting**: Load templates and inject context/trend data.
- **Generation**: Call LLM API.
- **Persist**: Save response to disk.

## Process Details

### 1. Input Data
**Source**: {tech-trend-analysis.analysis-report}/{TODAY_DATE}/*.json 

**TODAY_DATE**: datetime.date.today().strftime('%Y-%m-%d')

**JSON Schema**:
```json
{
  "analysis_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "Agentic AI Patterns",
      "reason": "Rising popularity in enterprise automation...",
      "links": ["..."],
      "search_keywords": "AI Agents, Automation"
    }
  ]
}
```

### 2. RAG Strategy (ChromaDB)
**Goal**: Find relevant chunks for a specific trend.

**Query Vector**: Embed the string "{trend.topic}: {trend.reason}".

**Filters (Where Clause)**:
- `category`: Must match the input file's category.
- `embedding_date`: Must match {TODAY_DATE}. 
- `Retrieval`: Get top `ktop` chunks. Format them into a single string (separated by newlines) for prompt injection.

### 3. Embeddings & LLM (Factory Pattern)
**Architecture**:
- **Abstract Base Classes**: `BaseLLMClient`, `BaseEmbeddingClient`.
- **Factories**: `LLMFactory`, `EmbeddingFactory`.
- **Providers**:
 - LLM: OpenAI, DeepSeek, Claude, Ollama.
 - Embedding: OpenAI, VoyageAI, Gemini, SentenceTransformers (local).
- **Resilience**: Implement exponential backoff (1s, 2s, 4s) and timeouts (60s) for all network calls.
- Auth: Load API keys from `.env`.

### 4. Prompt Engineering
**System Prompt**: Read from file. 

**User Prompt**: Read from file. 

**Injection Keys**:
- `{{context}}`: The aggregated text from ChromaDB chunks.
- `{{search_keywords}}`: Comma-separated string from `{trend.search_keywords}`.
- `{{reason}}`: The text from `{trend.reason}`.

### 5. Output Management
**Path**: `{article-generator.tech-trend-article}/{TODAY_DATE}/{category}/{slugified_topic}.md `

**Slug Logic**:
- Convert `{trend.topic}` to lowercase.
- Replace spaces with hyphens.
- Remove non-alphanumeric characters (except hyphens).
- Example: "Agentic AI Patterns!" -> "agentic-ai-patterns"

---

## Error Handling

### Network Errors
- **Timeout**: 60s
- **Retry**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Action**: Log ERROR, skip feed, continue

### File/Parsing Errors
- Missing config.yaml: Raise `ConfigurationError`
- Malformed RSS feed JSON: Raise `ValidationError`, continue with other categories

---

## Logging

### Format: JSON (one object per line)
**File**: `{article-generator.log}/article-generator-{TODAY_DATE}.log`

---

## Project Structure

```
├── article_generator.py              # Main Orchestrator (Script Entry Point)
├── src/
│   └── article_generator/
│       ├── __init__.py
│       ├── config.py                 # Config Loader & Pydantic Models
│       ├── factories.py              # LLM/Embedding Factories & Abstract Classes
│       ├── rag_engine.py             # ChromaDB Handler
│       └── utils.py                  # Logger, Slugify, Date Helpers
├── data/
│   └── embedding/                    # ChromaDB persistence
│   └── tech-trend-analysis/          # Input
│   └── tech-trend-article/           # Output
├── prompt/
├── .env
├── config.yaml
```

---

## Code Quality Standards

- **Max function length**: 50 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants

---

## Environment Setup (.env file)

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# DeepSeek API Key
DEEPSEEK_API_KEY=sk-...

# Claude (Anthropic) API Key
CLAUDE_API_KEY=sk-ant-...

# Voyage AI
VOYAGEAI_API_KEY=...

# Gemini API Key
GEMINI_API_KEY=...
```

---