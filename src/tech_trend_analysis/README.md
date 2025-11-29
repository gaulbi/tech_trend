# Tech Trend Analysis

A Python module that analyzes RSS feeds and generates daily technology trend reports using various LLM providers.

## Features

- **Multi-LLM Support**: OpenAI, DeepSeek, Claude (Anthropic), and Ollama (local)
- **Idempotent Processing**: Skip already-analyzed categories
- **Robust Error Handling**: Retry with exponential backoff, graceful degradation
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Type-Safe**: Full type hints throughout the codebase

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Create `.env` file** with your API keys:
```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# DeepSeek API Key
DEEPSEEK_API_KEY=sk-...

# Claude (Anthropic) API Key
CLAUDE_API_KEY=sk-ant-...

# Ollama does not require an API key
```

3. **Ensure `config.yaml` exists** in the project root (see Configuration section)

## Project Structure

```
.
├── tech-trend-analysis.py              # Main entry point
├── src/
│   └── tech_trend_analysis/            # Package
│       ├── __init__.py
│       ├── main.py                     # Main orchestration
│       ├── config.py                   # Configuration management
│       ├── models.py                   # Data models
│       ├── processor.py                # RSS processing logic
│       ├── logger.py                   # JSON logging
│       ├── exceptions.py               # Custom exceptions
│       └── llm/                        # LLM providers
│           ├── __init__.py
│           ├── base.py                 # Abstract base class
│           ├── factory.py              # Factory pattern
│           ├── openai_client.py
│           ├── deepseek_client.py
│           ├── claude_client.py
│           └── ollama_client.py
├── data/
│   ├── rss/
│   │   └── rss-feed/
│   │       └── {YYYY-MM-DD}/           # Daily RSS feeds
│   └── tech-trend-analysis/            # Analysis output
│       └── {YYYY-MM-DD}/
├── prompt/
│   └── tech-trend-analysis-prompt.md   # LLM prompt template
├── log/
│   └── tech-trend-analysis/            # JSON log directory
├── .env                                # API keys (gitignored)
├── config.yaml                         # Configuration
└── requirements.txt
```

## Configuration

The `config.yaml` file should contain:

```yaml
rss:
  rss-feed: data/rss/rss-feed
tech-trend-analysis:
  prompt: prompt/tech-trend-analysis-prompt.md
  analysis-report: data/tech-trend-analysis
  log: log/tech-trend-analysis
llm:
  server: openai  # openai, deepseek, claude, or ollama
  llm-model: gpt-4-turbo
  timeout: 60
  retry: 3
```

## Usage

Run the analysis:

```bash
python tech-trend-analysis.py
```

The script will:
1. Automatically detect today's date
2. Scan for RSS feed files in `data/rss/rss-feed/{TODAY_DATE}/`
3. Skip already-analyzed categories (idempotent)
4. Generate trend analysis for each category
5. Save results to `data/tech-trend-analysis/{TODAY_DATE}/`
6. Log all operations to `log/tech-trend-analysis/tech-trend-analysis-{TODAY_DATE}.log`

## Input Format

RSS feed files should be in `data/rss/rss-feed/{YYYY-MM-DD}/{category}.json`:

```json
{
  "category": "software_engineering",
  "fetch_date": "2025-11-01",
  "article_count": 2,
  "articles": [
    {
      "title": "DIY NAS: 2026 Edition",
      "link": "https://blog.example.com/..."
    },
    {
      "title": "Penpot: The Open-Source Figma",
      "link": "https://github.com/..."
    }
  ]
}
```

## Output Format

Analysis reports are saved to `data/tech-trend-analysis/{YYYY-MM-DD}/{category}.json`:

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

## Error Handling

- **Network Errors**: 3 retry attempts with exponential backoff (1s, 2s, 4s)
- **Timeout**: 60 seconds per request
- **Validation Errors**: Logged and skipped, processing continues
- **Configuration Errors**: Fatal, exits immediately

## Code Quality

- Maximum function length: 50 lines
- Type hints: Required for all functions
- Docstrings: Google style
- Line length: Max 100 characters
- No hardcoded values

## Logging

All logs are in JSON format (one object per line) in:
`log/tech-trend-analysis/tech-trend-analysis-{YYYY-MM-DD}.log`

Example log entry:
```json
{
  "timestamp": "2025-11-22T10:30:45.123456",
  "level": "INFO",
  "message": "Processing category: software_engineering",
  "module": "main",
  "function": "process_category",
  "line": 123,
  "category": "software_engineering"
}
```

## License

This project is provided as-is for technology trend analysis purposes.