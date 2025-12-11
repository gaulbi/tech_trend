# URL Scraper

A production-grade Python module for scraping and cleaning web content from tech trend analysis reports.

## Features

- ✅ Robust URL scraping with retry logic and exponential backoff
- ✅ Clean content extraction using readability-lxml and BeautifulSoup
- ✅ Comprehensive JSON logging with colored console output
- ✅ Idempotent processing (safe to run multiple times)
- ✅ Type hints and docstrings throughout
- ✅ Clean architecture with separation of concerns

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
```

## Usage

### Process all categories for today
```bash
python url-scraper.py
```

### Process specific category
```bash
python url-scraper.py --category "software_engineering"
```

### Process specific feed date
```bash
python url-scraper.py --feed_date "2025-02-01"
```

### Process specific category and date
```bash
python url-scraper.py --category "software_engineering" --feed_date "2025-02-01"
```

## Project Structure

```
.
├── url-scraper.py              # Entry point
├── src/
│   └── url_scraper/
│       ├── __init__.py         # Package initialization
│       ├── main.py             # Main entry logic
│       ├── config.py           # Configuration management
│       ├── logger.py           # Logging utilities
│       ├── processor.py        # Main processing logic
│       ├── models.py           # Data models
│       ├── scraper.py          # URL scraping logic
│       └── validator.py        # Validation utilities
├── data/
│   ├── tech-trend-analysis/    # Input directory
│   └── scraped-content/        # Output directory
├── log/                        # Log files
├── config.yaml                 # Configuration file
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Input Format

Input files are located at:
```
data/tech-trend-analysis/{FEED_DATE}/{category}.json
```

Example input structure:
```json
{
  "feed_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "AI Model Evolution",
      "reason": "Significant advancements",
      "score": 10,
      "links": ["https://example.com/article1", "https://example.com/article2"],
      "search_keywords": ["AI models", "machine learning"]
    }
  ]
}
```

## Output Format

Output files are saved at:
```
data/scraped-content/{FEED_DATE}/{category}/url-scrape.json
```

Example output structure:
```json
{
  "feed_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "AI Model Evolution",
      "query_used": "",
      "search_link": "https://example.com/article1",
      "content": "Cleaned article content..."
    }
  ]
}
```

## Logging

Logs are written to:
```
log/scraped-content/url-scraper-{FEED_DATE}.log
```

Log format (JSON):
```json
{
  "timestamp": "2025-11-26T10:30:45.123456",
  "level": "INFO",
  "module": "processor",
  "function": "process_category",
  "line": 42,
  "message": "Processing category: software_engineering"
}
```

## Error Handling

- **Network errors**: 3 retries with exponential backoff (1s, 2s, 4s)
- **Timeout**: 60 seconds (configurable)
- **Invalid JSON**: Logs error and continues with remaining categories
- **Missing files**: Logs warning and exits gracefully

## Idempotency

The scraper checks for existing output files before processing. If an output file already exists for a category and feed date, it will skip processing and log:

```
Skipping {category} (already processed for {FEED_DATE})
```

## Code Quality

- Maximum function length: 50 lines
- Type hints on all function signatures
- Google-style docstrings
- Maximum line length: 100 characters
- No hardcoded values (uses config or constants)