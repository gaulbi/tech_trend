# URL Content Scraper

A production-grade Python module for scraping and cleaning content from URLs found in tech trend analysis files.

## Features

- ✅ Clean architecture with separation of concerns
- ✅ Comprehensive error handling with retry logic
- ✅ Automatic content cleaning (removes HTML, scripts, navigation, etc.)
- ✅ Configurable timeouts and retry strategies
- ✅ Structured logging with file and console output
- ✅ Error isolation - continues processing if one URL fails
- ✅ Type hints throughout
- ✅ Detailed summary reports

## Project Structure

```
.
├── url_scrapper.py              # Main entry point
├── src/
│   └── url_scrapper/            # Package
│       ├── __init__.py
│       ├── config_manager.py    # Configuration handling
│       ├── scraper.py           # URL scraping logic
│       ├── file_processor.py    # File processing orchestration
│       └── models.py            # Data models
├── data/
│   ├── tech-trend-analysis/
│   │   └── report/
│   │       └── YYYY-MM-DD/
│   │           └── *.json
│   └── scrapped-content/
│       └── YYYY-MM-DD/
│           └── category/
│               └── url-scrap.json
├── config.yaml                  # Configuration file
├── requirements.txt             # Dependencies
└── README.md
```

## Installation

1. **Clone or download the project**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   
   Edit `config.yaml` to set your paths and timeouts:
   ```yaml
   tech-trend-analysis:
     analysis-report: data/tech-trend-analysis/report
   
   scrap:
     url-scrapped-content: data/scrapped-content
     timeout: 60
   ```

## Usage

### Basic Usage

Run the scraper for today's trend analysis files:

```bash
python url_scrapper.py
```

### Expected Input Format

Place your trend analysis files in:
```
data/tech-trend-analysis/report/YYYY-MM-DD/category.json
```

Example input file (`software-engineering-dev.json`):
```json
{
  "analysis_timestamp": "2025-11-22T08:03:00.627012",
  "source_file": "software-engineering-dev.json",
  "category": "Software Engineering / Dev",
  "trends": [
    {
      "topic": "New Go to TypeScript Converter",
      "reason": "Addresses common developer pain point...",
      "category": "Dev Tools",
      "links": [
        "https://github.com/example/tool",
        "https://example.com/article"
      ],
      "search_keywords": ["golang", "typescript"]
    }
  ]
}
```

### Output Format

Scraped content is saved to:
```
data/scrapped-content/YYYY-MM-DD/category/url-scrap.json
```

Example output:
```json
{
  "analysis_timestamp": "2025-11-22T08:03:00.627012",
  "source_file": "software-engineering-dev.json",
  "category": "Software Engineering / Dev",
  "trends": [
    {
      "topic": "New Go to TypeScript Converter",
      "link": "https://github.com/example/tool",
      "content": "Clean extracted content without HTML tags...",
      "scrape_timestamp": "2025-11-22T10:30:45.123456",
      "error": null
    }
  ]
}
```

## Features in Detail

### Content Cleaning

The scraper automatically removes:
- HTML tags and attributes
- JavaScript and CSS
- Navigation elements (nav, footer, header)
- Comments and metadata
- URLs and email addresses
- Reference indicators like [1], [2]
- Excessive whitespace

### Error Handling

- **Network errors**: Automatic retry with exponential backoff
- **Timeouts**: Configurable timeout with graceful failure
- **Invalid URLs**: Validation before scraping
- **Malformed HTML**: Robust parsing with BeautifulSoup
- **Error isolation**: One failure doesn't stop processing

### Retry Logic

- Automatic retries for transient failures (500, 502, 503, 504)
- Exponential backoff: 1s, 2s, 4s
- Configurable max retries (default: 3)

### Logging

Logs are written to:
- Console (INFO level)
- `url_scrapper.log` file (all levels)

Example log output:
```
2025-11-22 10:30:45,123 - __main__ - INFO - Starting URL Content Scraper
2025-11-22 10:30:45,234 - url_scrapper.config_manager - INFO - Configuration loaded
2025-11-22 10:30:46,345 - url_scrapper.scraper - INFO - Scraping URL: https://example.com
2025-11-22 10:30:47,456 - url_scrapper.scraper - INFO - Successfully scraped 15432 characters
```

## Configuration Options

### config.yaml

```yaml
tech-trend-analysis:
  prompt: prompt/tech-trend-analysis-prompt.md
  analysis-report: data/tech-trend-analysis/report  # Input directory

llm:
  server: openai
  llm-model: gpt-4
  timeout: 60

scrap:
  url-scrapped-content: data/scrapped-content  # Output directory
  timeout: 60  # HTTP request timeout in seconds
```

## Development

### Running Tests

```bash
# Add your test commands here
python -m pytest tests/
```

### Code Style

The codebase follows:
- PEP 8 style guide
- Type hints throughout
- Comprehensive docstrings
- SOLID principles

## Troubleshooting

### "No JSON files found"
- Ensure files exist in `data/tech-trend-analysis/report/YYYY-MM-DD/`
- Check that today's date matches the directory structure

### "Timeout while scraping"
- Increase timeout in `config.yaml`
- Check network connectivity
- Some sites may block automated scrapers

### "Failed to scrape content"
- Check if URL is accessible manually
- Some sites require authentication
- Review logs for specific error details

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please ensure:
1. Code follows existing style
2. Type hints are included
3. Docstrings are comprehensive
4. Error handling is robust