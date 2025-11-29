# Tech Trend Analysis

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Tasks**: Generate a complete Python module implementation based on this plan.

---

## Module Overview

**Purpose**: Send RSS topics to an LLM and generate daily technology trend analysis reports.  
**Behavior**: Single-run batch processor for **today's date only**  with idempotent behavior (skip already-analyzed trend categories).

---

## Configuration

### File: `./config.yaml`
```yaml
rss:
  rss-feed: data/rss/rss-feed
tech-trend-analysis:
  prompt: prompt/tech-trend-analysis-prompt.md
  analysis-report: data/tech-trend-analysis
  log: log/tech-trend-analysis
llm:
  server: openai
  llm-model: gpt-5.1
  timeout: 60
  retry: 3
```

**Validation**: Missing config.yaml → Raise `ConfigurationError` and exit

---

## Input: RSS Feed

### File Path
`{rss.rss-feed}/{TODAY_DATE}/{category}.json`

**TODAY_DATE**: Automatically determined using `datetime.date.today().strftime('%Y-%m-%d')`

### Example
If today is 2025-11-01
`data/rss/rss-feed/2025-11-01/software_engineering.json`

### Format:
```json
{
  "category": "software_engineering",
  "fetch_date": "2025-11-01",
  "article_count": 2,
  "articles": [
    { "title": "DIY NAS: 2026 Edition", "link": "https://blog...." },
    { "title": "Penpot: The Open-Source Figma", "link": "https://github...." }
  ]
}
```

**Validation**: Invalid JSON → Raise `ValidationError` and continue processing remaining categories.

---

## Output

### File Path Format
`{tech-trend-analysis.analysis-report}/{TODAY_DATE}/{category}.json`

### Example
If today is 2025-11-21:
`data/tech-trend-analysis/2025-11-21/software_engineering.json`

### JSON Structure
```json
{
  "analysis_date": "2025-11-22",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "...",
      "reason": "...",
      "links": ["..."],
      "search_keywords": "..."
    }
  ]
}
```

---

## Date Processing Logic
- **Automatic Date Detection**: Module automatically determines today's date at runtime
- **Input Directory**: Only scan `{rss.rss-feed}/{TODAY_DATE}/` for category JSON files
- **Output Directory**: Write all results to `{tech-trend-analysis.analysis-report}/{TODAY_DATE}/{category}/`
- **No Historical Processing**: Ignore all data from previous dates

---

## Multi-LLM Provider Support
- Support multiple LLM providers: **OpenAI**, **DeepSeek**, **Claude (Anthropic)**, and **Ollama** (local)
- Use a **Factory Pattern** to create appropriate LLM clients
- All LLM clients must inherit from an **Abstract Base Class**
- Load API keys from **`.env` file**

---

## Error Handling

### Network Errors
- **Timeout**: 60s
- **Retry**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Action**: Log ERROR, skip feed, continue

### File/Parsing Errors
- Missing config.yaml: Raise `ConfigurationError`
- Malformed RSS feed JSON: Raise `ValidationError`, continue with other categories

### Graceful Degradation
- Partial category failure: Continue with other categories
- All RSS feeds fail in category: Create empty output file

---

## Logging

### Format: JSON (one object per line)
**File**: `{tech-trend-analysis.log}/tech-trend-analysis-{TODAY_DATE}.log`

---

## Project Structure

```
.
├── tech-trend-analysis.py              # Main entry point
├── src/
│   └── tech_trend_analysis/            # Package
├── data/
│   ├── rss/                            
│   │      └── {TODAY_DATE}/            # Only process this directory
│   └── tech-trend-analysis/            # Analysis results (output) folder
│          └── {TODAY_DATE}/            # Only write to this directory
├── prompt/                             # LLM prompt template folder
├── .env                                # API keys (gitignored)
├── config.yaml                         # Configuration file
```

### Entry Point
```bash
python tech-trend-analysis.py
```
---

## Idempotency

**Before fetching each category**: Check if file exists at `{tech-trend-analysis.analysis-report}/{TODAY_DATE}/{category}.json`
- **If exists**: Log INFO, print "Skipping...", don't fetch
- **If not exists**: Send prompt from {tech-trend-analysis.prompt} folder to LLM

---

## Code Quality Standards

- **Max function length**: 50 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants

---
## Success Criteria

- All valid LLM response retrieved successfully
- Invalid LLM response don't stop execution
- Idempotent: Running twice produces same results
- All code has type hints and docstrings

---
## Implementation Notes

### DO NOT GENERATE
- `config.yaml` (provided at runtime)
- Test files

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