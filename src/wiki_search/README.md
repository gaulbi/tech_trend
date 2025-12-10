# Wikipedia Search Module

A production-grade Python module for searching Wikipedia, extracting content, and storing cleaned results for tech trend analysis.

## Features

- **Automated Wikipedia Search**: Searches keywords from tech trend analysis
- **Content Cleaning**: Removes citations, references, and excessive whitespace
- **Robust Error Handling**: Retry logic with exponential backoff for network failures
- **Idempotent Processing**: Safely rerun without duplicating work
- **Comprehensive Logging**: JSON-formatted logs for production monitoring
- **Type-Safe**: Full type hints throughout codebase
- **Progress Tracking**: Real-time progress indication for long-running jobs
- **Validation**: Input validation for dates, configuration, and data structure

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create `config.yaml` in the project root:

```yaml
tech-trend-analysis:
  analysis-report: data/tech-trend-analysis
scrape:
  url-scraped-content: data/scraped-content
  log: log/scraped-content
  max-search-results: 5
```

### Configuration Validation

The module validates:
- All required fields are present
- `max-search-results` is a positive integer
- Config file is valid YAML

## Usage

### Process all categories for today's date
```bash
python wiki-search.py
```

### Process specific category
```bash
python wiki-search.py --category "software_engineering"
```

### Process specific date
```bash
python wiki-search.py --feed_date "2025-02-01"
```

### Process specific category and date
```bash
python wiki-search.py --category "software_engineering" --feed_date "2025-02-01"
```

### Debug Mode
```bash
export DEBUG=true
python wiki-search.py
```

## Input Format

Expected input file structure:
```
data/tech-trend-analysis/{FEED_DATE}/{category}.json
```

Example input:
```json
{
  "feed_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "AI Development",
      "reason": "...",
      "score": 10,
      "links": ["..."],
      "search_keywords": ["frontier-class AI models", "AI capability diffusion"]
    }
  ]
}
```

**Validation**: The module validates:
- JSON structure is valid
- All required fields are present
- `feed_date` format is YYYY-MM-DD
- `feed_date` and `category` match file location

## Output Format

Generated output file structure:
```
data/scraped-content/{FEED_DATE}/{category}/wiki-search.json
```

Example output:
```json
{
  "feed_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "AI Development",
      "query_used": "frontier-class AI models",
      "search_link": "https://en.wikipedia.org/wiki/...",
      "content": "Cleaned Wikipedia content..."
    }
  ]
}
```

**Note**: 
- One input trend may result in multiple output trend objects
- Every Wikipedia page scraped appears separately in `trends`
- `search_link`: Properly URL-encoded Wiki page link
- `query_used`: The exact query sent to Wikipedia

## Architecture

```
.
├── wiki-search.py              # Entry point
├── src/
│   └── wiki_search/
│       ├── __init__.py
│       ├── config.py           # Configuration management with validation
│       ├── content_cleaner.py  # Content cleaning with improved patterns
│       ├── exceptions.py       # Custom exceptions
│       ├── logger.py           # Logging utilities
│       ├── main.py             # Main execution with progress tracking
│       ├── models.py           # Data models
│       ├── processor.py        # Core processing logic
│       └── wikipedia_searcher.py  # Wikipedia API with loop prevention
├── config.yaml
└── requirements.txt
```

## Error Handling

### Network Errors
- **Timeout**: 15 seconds (explicitly set)
- **Retry**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Action**: Log ERROR with context, skip that search, continue

### Zero Results
- **Action**: Log WARNING with keyword and topic, continue

### Disambiguation Pages
- **Action**: Automatically follows first option
- **Loop Prevention**: Tracks visited pages, max depth of 5
- **Circular Reference**: Detected and logged as WARNING

### Invalid Input
- **Invalid JSON**: Raises `ValidationError`, logs error, continues with other categories
- **Missing Config**: Raises `ConfigurationError`, exits with code 1
- **Invalid Date Format**: Validates YYYY-MM-DD format, exits with error message
- **Missing Required Fields**: Validates all required fields in input data

### Partial Failures
- If processing 3 keywords and 2 succeed but 1 fails, successful results are saved
- Logs clearly indicate partial success: "Collected N Wikipedia pages"

## Logging

### File Location
Logs are written in JSON format to:
```
log/scraped-content/wiki-search-{FEED_DATE}.log
```

### Log Entry Format
Each log entry contains:
- `timestamp`: ISO format timestamp
- `level`: Log level (INFO, WARNING, ERROR)
- `message`: Detailed log message with context
- `module`: Source module name
- `function`: Source function name
- `exception`: Stack trace (for ERROR level)

### Enhanced Context
All logs include relevant context:
- Category name
- Topic name
- Search keyword
- Attempt number (for retries)
- Progress indicators (e.g., "Processing 3/10")

## Content Cleaning

The module removes:
1. **Citation markers**: `[1]`, `[23]`, `[citation needed]`
2. **Reference sections**: Everything from "== References ==" onward
3. **Metadata sections**: See also, External links, Further reading, Notes, Bibliography, Sources
4. **Excessive whitespace**: While preserving paragraph structure

### Section Detection
- Case-insensitive matching
- Flexible spacing (handles "==References==" and "== References ==")
- Handles both singular and plural forms

### Whitespace Normalization
- Preserves paragraph breaks (double newlines)
- Removes excessive spacing
- Maintains readability

## URL Encoding

- Uses proper URL encoding via `urllib.parse.quote()`
- Handles special characters (e.g., "C++", "AT&T")
- Safe characters: `/:` (for URL structure)

## Idempotency

Before processing each category:
1. Check if output file exists: `{scraped_content}/{FEED_DATE}/{category}/wiki-search.json`
2. If exists → Log INFO, skip processing
3. Prevents duplicate API calls and processing

## Progress Indication

The module provides real-time feedback:
```
INFO - Found 5 categories to process
INFO - Processing category 1/5: software_engineering
INFO - Processing trend 2/8: 'AI Development' with 3 keywords
INFO - Search found 5 results for 'AI models' (topic: 'AI Development')
INFO - Successfully fetched 4/5 pages for keyword: 'AI models'
INFO - Trend 'AI Development': collected 12 Wikipedia pages
INFO - Completed category 'software_engineering': generated 45 result entries
```

## Code Quality Standards

- **Max function length**: 50 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants
- **Comprehensive validation**: Input data, configuration, dates
- **Error context**: All errors include relevant context for debugging

## Success Criteria

✅ Automatically processes today's date without manual input  
✅ Validates feed_date format (YYYY-MM-DD)  
✅ Validates configuration values (types and ranges)  
✅ Proper URL encoding for all characters  
✅ Prevents infinite loops in disambiguation chains  
✅ Searching, cleaning, and storing wiki content successfully  
✅ Invalid searches don't stop execution  
✅ Partial success is handled gracefully  
✅ Idempotent: Running twice produces same results  
✅ All code has type hints and docstrings  
✅ Graceful handling when no input data exists  
✅ Progress tracking for long-running operations  
✅ Enhanced logging with full context  

## Troubleshooting

### "Invalid feed_date format" error
- Ensure date is in YYYY-MM-DD format
- Example: `--feed_date "2025-02-01"`

### "Configuration file not found" error
- Ensure `config.yaml` exists in project root
- Check file path is correct

### "max-search-results must be a positive integer" error
- Check `config.yaml` has valid integer for `scrape.max-search-results`
- Value must be > 0

### No results for search
- Check spelling of search keywords
- Wikipedia may not have articles for very specific terms
- Check logs for detailed error messages

## License

MIT