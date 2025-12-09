# Wikipedia Search Module

A production-grade Python module for searching Wikipedia based on tech trend keywords, extracting and cleaning content, and storing results.

## Features

- ✅ **Automatic Date Processing**: Processes only today's date automatically
- ✅ **Idempotent**: Safe to run multiple times - skips already processed categories
- ✅ **Robust Error Handling**: Retry logic with exponential backoff
- ✅ **Comprehensive Logging**: JSON-formatted logs with timestamps
- ✅ **Content Cleaning**: Removes citations, references, and unwanted sections
- ✅ **Production-Ready**: Type hints, docstrings, and clean architecture

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `config.yaml` file in the project root:

```yaml
tech-trend-analysis:
  analysis-report: data/tech-trend-analysis

scrape:
  url-scraped-content: data/scraped-content
  timeout: 60
  log: log/scraped-content
  max-search-results: 5
```

## Usage

```bash
python wiki_search.py
```

The module will:
1. Automatically detect today's date
2. Look for category files in `data/tech-trend-analysis/{TODAY}/`
3. Search Wikipedia for each keyword
4. Clean and save results to `data/scraped-content/{TODAY}/{category}/wiki-search.json`
5. Skip categories that have already been processed

## Input Format

Input files: `data/tech-trend-analysis/{YYYY-MM-DD}/{category}.json`

```json
{
  "analysis_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "AI Development",
      "reason": "Growing importance",
      "links": ["..."],
      "search_keywords": [
        "frontier-class AI models",
        "AI capability diffusion"
      ]
    }
  ]
}
```

## Output Format

Output files: `data/scraped-content/{YYYY-MM-DD}/{category}/wiki-search.json`

```json
{
  "analysis_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "AI Development",
      "search_keywords": "frontier-class AI models",
      "link": "https://en.wikipedia.org/wiki/...",
      "content": "Cleaned Wikipedia content..."
    }
  ]
}
```

## Logging

Logs are written to: `log/scraped-content/wiki-search-{YYYY-MM-DD}.log`

Each log entry is a JSON object:
```json
{"timestamp": "2025-11-26 10:30:45", "level": "INFO", "message": "Processing category", "category": "software_engineering"}
```

## Error Handling

- **Missing config.yaml**: Raises `ConfigurationError` and exits
- **Invalid JSON**: Logs error and continues with next category
- **No input files for today**: Logs warning and exits gracefully (code 0)
- **Network errors**: Retries 3 times with exponential backoff
- **Page not found**: Logs warning and continues with next result

## Project Structure

```
.
├── wiki_search.py              # Main entry point (lightweight)
├── src/
│   └── wiki_search/            # Package
│       ├── __init__.py         # Package initialization
│       ├── orchestrator.py     # Main workflow orchestration
│       ├── config.py           # Configuration management
│       ├── logger.py           # Logging setup
│       ├── file_handler.py     # File I/O operations
│       ├── wikipedia_client.py # Wikipedia API client
│       ├── processor.py        # Category processing logic
│       ├── content_cleaner.py  # Content cleaning utilities
│       └── exceptions.py       # Custom exceptions
├── data/
│   ├── tech-trend-analysis/
│   │   └── {YYYY-MM-DD}/      # Input directory
│   └── scraped-content/
│       └── {YYYY-MM-DD}/      # Output directory
├── log/
│   └── scraped-content/       # Log files
├── config.yaml                 # Configuration
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Module Responsibilities

- **orchestrator.py**: Coordinates the entire workflow, initializes components
- **config.py**: Loads and validates configuration
- **logger.py**: Sets up JSON logging
- **file_handler.py**: Handles file I/O operations (read/write/validate)
- **wikipedia_client.py**: Manages Wikipedia API calls with retry logic
- **processor.py**: Processes categories and keywords
- **content_cleaner.py**: Cleans Wikipedia content
- **exceptions.py**: Custom exception definitions

## Code Quality

- **Type hints**: All functions have complete type annotations
- **Docstrings**: Google-style docstrings for all public functions
- **Max line length**: 100 characters
- **Max function length**: 50 lines
- **No hardcoded values**: All configuration externalized

## Exit Codes

- `0`: Success or no input files for today
- `1`: Configuration error or unexpected fatal error