# URL Scraper

Production-grade Python module for scraping and cleaning content from URLs in tech trend analysis files.

## Features

- **Automatic Date Detection**: Processes only today's data automatically
- **Idempotent**: Safe to run multiple times per day
- **Robust Error Handling**: Retry logic with exponential backoff
- **Clean Content Extraction**: Removes HTML tags, scripts, and irrelevant characters
- **JSON Logging**: Structured logging for monitoring and debugging
- **Type-Safe**: Full type hints and validation

## Installation

```bash
# Install dependencies
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

```bash
# Run the scraper for today's date
python url_scraper.py
```

The scraper will:
1. Automatically determine today's date
2. Look for category files in `data/tech-trend-analysis/{TODAY}/`
3. Skip categories that have already been processed
4. Scrape URLs and extract clean content
5. Save results to `data/scraped-content/{TODAY}/{category}/url-scrape.json`

## Input Format

Input files: `data/tech-trend-analysis/{TODAY}/{category}.json`

```json
{
  "analysis_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "AI Agents",
      "reason": "Rising popularity...",
      "links": ["https://example.com/article1"],
      "search_keywords": ["AI", "Agents"]
    }
  ]
}
```

## Output Format

Output files: `data/scraped-content/{TODAY}/{category}/url-scrape.json`

```json
{
  "analysis_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "AI Agents",
      "link": "https://example.com/article1",
      "content": "Extracted readable text...",
      "search_keywords": ["AI", "Agents"]
    }
  ]
}
```

## Logging

Logs are written to: `log/scraped-content/url-scraper-{TODAY}.log`

Format: One JSON object per line

```json
{
  "timestamp": "2025-11-26 10:30:45,123",
  "level": "INFO",
  "message": "Successfully fetched: https://example.com",
  "module": "url_fetcher",
  "function": "fetch",
  "line": 42
}
```

## Error Handling

- **Network Errors**: 3 retries with exponential backoff (1s, 2s, 4s)
- **Timeout**: 60 seconds per request
- **Invalid JSON**: Logs error, continues with other categories
- **No Input Data**: Exits gracefully with warning

## Idempotency

Running the scraper multiple times on the same day will:
- Check if output files already exist
- Skip processing for completed categories
- Only process new or failed categories

## Project Structure

```
.
├── url_scraper.py              # Main entry point
├── requirements.txt            # Python dependencies
├── config.yaml                 # Configuration (create this)
├── src/
│   └── url_scraper/
│       ├── __init__.py
│       ├── scraper.py          # Main scraper logic
│       ├── config.py           # Configuration management
│       ├── logger.py           # Logging utilities
│       ├── url_fetcher.py      # URL fetching with retry
│       ├── content_extractor.py # Content cleaning
│       ├── models.py           # Data models
│       └── exceptions.py       # Custom exceptions
├── data/
│   ├── tech-trend-analysis/
│   │   └── {TODAY}/            # Input files
│   └── scraped-content/
│       └── {TODAY}/            # Output files
└── log/
    └── scraped-content/       # Log files
```

## Code Quality

- **Type Hints**: All functions have type annotations
- **Docstrings**: Google-style docstrings for all public functions
- **Max Function Length**: 50 lines
- **Line Length**: Max 100 characters
- **No Hardcoded Values**: All configuration in config.yaml

## Exit Codes

- `0`: Success (or no data for today)
- `1`: Configuration error or unexpected failure