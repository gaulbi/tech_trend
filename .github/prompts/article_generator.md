# Article Generator

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture, production-grade code, RAG, and GenAI.
**Tasks**: Generate a complete Python module implementation based on this plan.

---

## Module Overview

**Purpose**: Create technology trends into educational articles using LLMs and RAG.

### Feed Date
- If `--feed_date` argument is not specified in command, use today's date as the feed date.
- In this case, determine today's date using `datetime.date.today().strftime('%Y-%m-%d')`

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
  analysis-report: data/tech-trend-analysis    #Base input folder
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
rag:
  ktop: 20
```

**Validation**: Missing config.yaml → Raise `ConfigurationError` and exit

---

## Process Workflow

1. **Discovery**: Scan the folder {tech-trend-analysis.analysis-report}/{FEED_DATE}/ for all *.json files
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

---

## Input Data

### File Path
`{tech-trend-analysis.analysis-report}/{FEED_DATE}/{category}.json`

### Example
If a feed date is _2025-11-26_ and a category is software_engineering, 
`data/tech-trend-analysis/2025-11-26/software_engineering.json`

### JSON Schema
```json
{
  "feed_date": "2025-11-22",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "...",
      "reason": "...",
      "score": 10,
      "links": ["..."],
      "search_keywords": ["..."]
    }
  ]
}
```

### RAG Strategy (ChromaDB)
**Goal**: Find relevant chunks for a specific trend.

**Query Vector**: embed each keyword in `{trend.search_keywords}` separately and aggregate vectors.

**Filters (Where Clause)**:
- `category`: Must match the input file's category.
- `embedding_date`: Must match {FEED_DATE}. 
- `Retrieval`: Get top `{rag.ktop}` chunks. Format them into a single string (separated by newlines) for prompt injection.

### Embeddings & LLM (Factory Pattern)
**Architecture**:
- **Abstract Base Classes**: `BaseLLMClient`, `BaseEmbeddingClient`.
- **Factories**: `LLMFactory`, `EmbeddingFactory`.
- **Providers**:
 - LLM: OpenAI, DeepSeek, Claude, Ollama.
 - Embedding: OpenAI, VoyageAI, Gemini, SentenceTransformers (local).
- **Resilience**: Implement exponential backoff (1s, 2s, 4s) and timeouts (60s) for all network calls.
- Auth: Load API keys from `.env`.

### Prompt Engineering
**System Prompt**: Read from file. 

**User Prompt**: Read from file. 

**Injection Keys**:
- `{{context}}`: The aggregated text from ChromaDB chunks.
- `{{search_keywords}}`: String list from `{trend.search_keywords}`.
- `{{reason}}`: The text from `{trend.reason}`.

## Output

### File Path
`{article-generator.tech-trend-article}/{FEED_DATE}/{category}/{slugified_topic}.md `

### Example
If a feed date is _2025-11-26_, a category is software_engineering and a slugified topic is serverless-computing, 
`data/tech-trend-article/2025-11-26/software_engineering/serverless-computing.md`

### 5. Output Management
**Path**: 

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
- **Action**: Log ERROR, skip trend, continue

### File/Parsing Errors
- Missing config.yaml: Raise `ConfigurationError`

---

## Logging

### Format: JSON (one object per line)
**File**: `{article-generator.log}/article-generator-{FEED_DATE}.log`

### Log Format
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
3. JSON formatting option for structured logging
4. Function decorator to auto-log calls with timing
5. Error logging helper that captures stack traces
6. Configurable via environment variables or config file
7. Include example usage showing:
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
├── article-generator.py              # Main Orchestrator (Script Entry Point)
├── src/
│   └── article_generator
├── data/
│   └── embedding/                    # ChromaDB persistence
│   └── tech-trend-analysis/          # Input
│   └── tech-trend-article/           # Output
├── prompt/
├── .env
├── config.yaml
```

- DO NOT implement any logic in `article-generator.py`. It's only for entry point.

### Entry Point
```bash
python article-generator.py

python article-generator.py --category "software_engineering"

python article-generator.py --feed_date "2025-02-01"

python article-generator.py --cnt 1

python article-generator.py --overwrite 

python article-generator.py --category "software_engineering" --feed_date "2025-02-01" --cnt 1
```

- **category**, **cnt**, and **feed_date** are optional input parameters.
- If `cnt` is specified, process that number of trends sorted by descending score. For example, if `--cnt` is _2_, the **two highest-score topics** are selected to generate two articles..
- If `overwrite` flag is set, ignore `If file exists -> SKIP` rule. 


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