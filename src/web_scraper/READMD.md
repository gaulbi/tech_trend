# Web Scraper for Tech Trend Analysis

Production-ready web scraper that searches and extracts content from articles based on tech trend analysis keywords. Processes data for **today's date only** with idempotent behavior.

## Features

- ✅ **Multiple Scraper Provider Support**: ScraperAPI, ScrapingBee, ZenRows
- ✅ **Factory Pattern**: Automatic provider selection based on available API keys
- ✅ **Robust Error Handling**: Retry logic with exponential backoff
- ✅ **Structured Logging**: JSON-formatted logs for easy parsing
- ✅ **Idempotent**: Safe to run multiple times on same day
- ✅ **Clean Architecture**: Type hints, docstrings, modular design
- ✅ **Content Cleaning**: Extracts readable text from HTML

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with at least one API key:

```env
# Choose one or more providers
SCRAPERAPI_KEY=your_scraperapi_key_here
SCRAPINGBEE_KEY=your_scrapingbee_key_here
ZENROWS_KEY=your_zenrows_key_here
```

**Priority**: The scraper will use the first available key in this order: ScraperAPI → ScrapingBee → ZenRows

### 3. Configure Settings

Ensure your `config.yaml` exists:

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

### Basic Execution

```bash
python web_scraper.py
```

The scraper will:
1. Automatically determine today's date
2. Look for input files in `data/tech-trend-analysis/YYYY-MM-DD/`
3. Process each category JSON file
4. Save results to `data/scraped-content/YYYY-MM-DD/{category}/web-scrape.json`

### Expected Input Structure

**Location**: `data/tech-trend-analysis/2025-12-01/software_engineering.json`

```json
{
  "analysis_date": "2025-12-01",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "Zero Knowledge Proofs in Privacy",
      "reason": "Emerging cryptographic technique",
      "links": ["https://example.com"],
      "search_keywords": [
        "zero knowledge proof privacy protocol",
        "decentralized identity verifiable credentials"
      ]
    }
  ]
}
```

### Output Structure

**Location**: `data/scraped-content/2025-12-01/software_engineering/web-scrape.json`

```json
{
  "analysis_date": "2025-12-01",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "Zero Knowledge Proofs in Privacy",
      "query_used": "zero knowledge proof privacy protocol",
      "link": "https://article-url.com",
      "content": "Cleaned article text...",
      "source_search_terms": ["zero", "knowledge", "proof", "privacy", "protocol"]
    }
  ]
}
```

## How It Works

### 1. Search Phase
For each search keyword:
- Constructs Google search URL
- Fetches via scraper API (avoids IP blocking)
- Parses HTML to extract top N article URLs

### 2. Scrape Phase
For each discovered URL:
- Fetches full article content via scraper API
- Applies retry logic (3 attempts, exponential backoff)

### 3. Clean Phase
For each scraped article:
- Uses readability-lxml to extract main content
- Removes boilerplate, navigation, ads
- Normalizes whitespace

### 4. Output Phase
- Saves all successfully scraped articles
- One output object per article (input trend may produce multiple outputs)

## Architecture

```
src/web_scraper/
├── __init__.py
├── orchestrator.py          # Main coordination logic
├── scraper.py               # Core scraping operations
├── config.py                # Configuration management
├── logger.py                # Structured JSON logging
├── models.py                # Data classes
├── exceptions.py            # Custom exceptions
├── file_processor.py        # File I/O operations
├── search_parser.py         # Parse search results
├── content_cleaner.py       # HTML content cleaning
├── scraper_factory.py       # Factory pattern for clients
└── scraper_clients/
    ├── __init__.py
    ├── base.py              # Abstract base class
    ├── scraperapi.py        # ScraperAPI client
    ├── scrapingbee.py       # ScrapingBee client
    └── zenrows.py           # ZenRows client
```

## Logging

Logs are written to: `log/scraped-content/web-scraper-YYYY-MM-DD.log`

**Format**: JSON (one object per line)

```json
{
  "timestamp": "2025-12-01 10:30:45,123",
  "level": "INFO",
  "message": "Processing category: software_engineering",
  "module": "orchestrator",
  "function": "_process_category",
  "line": 123
}
```

## Error Handling

### Configuration Errors
- Missing `config.yaml` → Exit with error code 1
- Missing API keys → Exit with error code 1

### Validation Errors
- Invalid JSON in input file → Log error, skip category, continue
- Missing required fields → Log error, skip category, continue

### Network Errors
- Timeout (60s default) → Retry 3 times with backoff (1s, 2s, 4s)
- All retries failed → Log error, skip article, continue

### Graceful Handling
- No input files for today → Log warning, exit with code 0
- Already processed category → Skip, continue

## Idempotency

The scraper checks if output files exist before processing:

```
✓ data/scraped-content/2025-12-01/software_engineering/web-scrape.json exists
→ Skipping software_engineering (already processed for 2025-12-01)
```

Safe to run multiple times per day without duplicate work.

## Development

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-cov mypy

# Run tests (when test files are created)
pytest tests/

# Type checking
mypy src/
```

### Code Quality Standards

- ✅ Maximum function length: 50 lines
- ✅ Type hints on all functions
- ✅ Google-style docstrings
- ✅ Maximum line length: 100 characters
- ✅ No hardcoded values

## Troubleshooting

### "No scraper API key found"
Add at least one API key to your `.env` file

### "Configuration file not found"
Ensure `config.yaml` exists in the project root

### "No input files to process"
Create input files in `data/tech-trend-analysis/YYYY-MM-DD/` for today's date

### Rate Limiting
If you hit rate limits:
1. Check your API plan limits
2. Reduce `max-search-results` in config.yaml
3. Add delays between requests (modify scraper clients)

## License

Proprietary - Internal Use Only