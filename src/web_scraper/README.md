# Web Scraper for Tech Trend Analysis

A production-grade Python module for scraping and cleaning web content based on tech trend analysis data.

## Features

- ✅ **Multi-Provider Support**: ScraperAPI, ScrapingBee, ZenRows
- ✅ **Automatic Date Detection**: Processes only today's data
- ✅ **Idempotent Execution**: Safe to run multiple times per day
- ✅ **Robust Error Handling**: Retry logic with exponential backoff
- ✅ **Content Cleaning**: Extracts readable text from HTML
- ✅ **Type-Safe**: Full type hints throughout
- ✅ **Production-Ready**: Comprehensive logging and error handling

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Add at least one API key
SCRAPERAPI_KEY=your_scraperapi_key_here
SCRAPINGBEE_KEY=your_scrapingbee_key_here
ZENROWS_KEY=your_zenrows_key_here
```

**Note**: The module will use the first available API key in this order:
1. ScraperAPI
2. ScrapingBee
3. ZenRows

### 3. Verify Configuration

Ensure `config.yaml` exists in the project root:

```yaml
tech-trend-analysis:
  analysis-report: data/tech-trend-analysis
scrape:
  url-scraped-content: data/scraped-content
  timeout: 60
```

## Usage

### Basic Execution

```bash
python web_scraper.py
```

### What It Does

1. **Detects Today's Date**: Automatically determines the current date
2. **Finds Input Files**: Scans `data/tech-trend-analysis/{TODAY_DATE}/` for JSON files
3. **Checks for Existing Output**: Skips categories already processed today
4. **Scrapes Content**: Fetches and cleans web content for each trend
5. **Saves Results**: Writes to `data/scraped-content/{TODAY_DATE}/{category}/web-scrape.json`

### Example Workflow

If today is **2025-11-28** and you have:

```
data/tech-trend-analysis/2025-11-28/
├── software_engineering.json
├── ai_ml.json
└── cloud_computing.json
```

Running `python web_scraper.py` will:
- Process each category file
- Scrape URLs from the trends
- Save cleaned content to:
  - `data/scraped-content/2025-11-28/software_engineering/web-scrape.json`
  - `data/scraped-content/2025-11-28/ai_ml/web-scrape.json`
  - `data/scraped-content/2025-11-28/cloud_computing/web-scrape.json`

Running it again the same day will skip all categories (idempotent).

## Project Structure

```
.
├── web_scraper.py              # Main entry point
├── src/
│   └── web_scraper/
│       ├── __init__.py
│       ├── config.py           # Configuration management
│       ├── exceptions.py       # Custom exceptions
│       ├── models.py           # Data models
│       ├── scraper_base.py     # Abstract base class
│       ├── scraper_clients.py  # Scraper implementations
│       ├── scraper_factory.py  # Factory pattern
│       ├── content_cleaner.py  # HTML cleaning
│       ├── file_handler.py     # File I/O operations
│       └── orchestrator.py     # Main workflow logic
├── data/
│   ├── tech-trend-analysis/
│   │   └── {YYYY-MM-DD}/       # Input: Daily trend analysis
│   └── scraped-content/
│       └── {YYYY-MM-DD}/       # Output: Scraped content
├── .env                        # API keys (create this)
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
└── web_scraper.log            # Application logs
```

## Input Format

**Path**: `data/tech-trend-analysis/{TODAY_DATE}/{category}.json`

```json
{
  "analysis_date": "2025-11-28",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "Rust Programming Language",
      "reason": "Growing adoption in systems programming",
      "links": [
        "https://example.com/rust-adoption",
        "https://example.com/rust-trends"
      ],
      "search_keywords": ["rust", "systems programming"]
    }
  ]
}
```

## Output Format

**Path**: `data/scraped-content/{TODAY_DATE}/{category}/web-scrape.json`

```json
{
  "analysis_date": "2025-11-28",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "Rust Programming Language",
      "link": "https://example.com/rust-adoption",
      "content": "Cleaned and readable text content...",
      "search_keywords": ["rust", "systems programming"]
    }
  ]
}
```

## Error Handling

### Network Errors
- **Timeout**: 60 seconds (configurable)
- **Retry Logic**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Action**: Logs error, skips failed URL, continues with next

### File Errors
- **Missing config.yaml**: Raises `ConfigurationError`, exits with code 1
- **Malformed JSON**: Raises `ValidationError`, logs error, continues with next category
- **No input files for today**: Logs warning, exits gracefully with code 0

### API Key Errors
- **No API keys found**: Raises `ConfigurationError` at startup
- **Invalid API response**: Logs error, retries with backoff

## Logging

Logs are written to:
- **Console**: INFO level and above
- **File**: `web_scraper.log` (all levels)

Example log output:
```
2025-11-28 10:30:15 - __main__ - INFO - Starting web scraper application
2025-11-28 10:30:15 - src.web_scraper.config - INFO - Using ScraperAPI
2025-11-28 10:30:15 - src.web_scraper.orchestrator - INFO - Processing data for 2025-11-28
2025-11-28 10:30:15 - src.web_scraper.file_handler - INFO - Found 3 category files for 2025-11-28
2025-11-28 10:30:15 - src.web_scraper.orchestrator - INFO - Processing category: software_engineering
2025-11-28 10:30:16 - src.web_scraper.orchestrator - INFO - Scraping: https://example.com/rust-adoption
2025-11-28 10:30:18 - src.web_scraper.file_handler - INFO - Saved output to data/scraped-content/2025-11-28/software_engineering/web-scrape.json
```

## Idempotency

The module is fully idempotent:
- Running multiple times on the same day produces identical results
- Already-processed categories are automatically skipped
- No duplicate API calls or wasted resources

## Code Quality

- ✅ **Type Hints**: All functions have complete type annotations
- ✅ **Docstrings**: Google-style docstrings for all public functions
- ✅ **Max Line Length**: 100 characters
- ✅ **Max Function Length**: 50 lines
- ✅ **No Hardcoded Values**: All configuration externalized

## Troubleshooting

### No input files found
**Issue**: `No input files found for {date}. Exiting.`

**Solution**: Ensure trend analysis files exist in `data/tech-trend-analysis/{TODAY_DATE}/`

### Configuration file not found
**Issue**: `Configuration file 'config.yaml' not found`

**Solution**: Create `config.yaml` in the project root directory

### No scraper API key found
**Issue**: `No valid scraper API key found in environment`

**Solution**: Add at least one API key to your `.env` file

### Scraping failed
**Issue**: `Failed to scrape {url}`

**Solution**: Check:
- API key is valid and has credits
- URL is accessible
- Network connection is stable
- Review logs for specific error details

## Development

### Running Tests (Optional)

```bash
# Unit tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

### Code Style

```bash
# Format code
black src/ web_scraper.py

# Check types
mypy src/ web_scraper.py

# Lint
flake8 src/ web_scraper.py --max-line-length=100
```

## License

This project is for internal use only.

## Support

For issues or questions, please check the logs in `web_scraper.log` or contact the development team.