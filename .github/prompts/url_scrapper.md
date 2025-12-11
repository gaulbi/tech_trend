# URL Scraper

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Tasks**: Generate a complete Python module implementation based on the detailed requirements below.

---

## Module Overview

**Purpose**: Retreive content of given URLs and remove characters that are not relevant the content, such as HTML tag, reference indicator, and image link.

### Feed Date
- If no date is specified in command, the feed date is today's date.
- Determine today's date using `datetime.date.today().strftime('%Y-%m-%d')`

---

### Configuration
```yaml
tech-trend-analysis:
  analysis-report: data/tech-trend-analysis     #Base source folder
scrape:
  url-scraped-content: data/scraped-content   #Base output folder
  timeout: 60
  log: log/scraped-content 
```

**Validation**: Missing config.yaml → Raise `ConfigurationError` and exit.

---

## Input: Tech Trend Analysis

### File Path
`{tech-trend-analysis.analysis-report}/{FEED_DATE}/{category}.json`

### Example
If a feed date is _2025-11-26_ and a category is software_engineering,
`data/tech-trend-analysis/2025-11-26/software_engineering.json`

### Format
```json
{
  "feed_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "...",
      "reason": "...",
      "score": 10,
      "links": ["..."],
      "search_keywords": [
        "frontier‑class AI models", 
        "AI capability diffusion"]
    }
  ]
}
```

**Validation**: Invalid JSON → Raise `ValidationError` and continue processing remaining categories.

---

## Output

### File Path
`{scrape.url-scraped-content}/{FEED_DATE}/{category}/url-scrape.json`

### Example
If a feed date is _2025-11-26_ and a category is software_engineering, 
`data/scraped-content/2025-11-26/software_engineering/url-scrape.json`

### JSON Structure

```json
{
  "feed_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "...",
      "query_used": "",
      "search_link": "...",
      "content": "...",
    }
  ]
}
```

**Note**:
- If a trend in input file (**Tech Trend Analysis**) has multiple links in `links` field, create one trend item per link in the output file. For instance, if **three** links in `links` field in a trend item in input file, trend item in output file becomes **three**. 
- `search_link`: Link where the content is scraped.
- `query_used`: Enter **na**. This field is not for this task. 

---

# Processing Logic

## Date Processing Logic
- **Input Directory**: Only scan `{tech-trend-analysis.analysis-report}/{FEED_DATE}/` for category JSON files
- **Output Directory**: Write all results to `{scrape.url-scraped-content}/{FEED_DATE}/{category}/`

---
## Clean Content
- Use a standard Python library such as readability-lxml, BeautifulSoup, or similar to extract readable text.
- Remove irrelevant characters and normalize whitespace.
- Sanitization: Strictly remove `<script>`, `<style>`,` <meta>`, `<noscript>`, and comments before text extraction.
- Normalization: Collapse multiple spaces/newlines into single whitespace/paragraphs.

---

## Error Handling

### Network Errors
- **Timeout**: 60s
- **Retry**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Action**: Log ERROR, skip scraping that link, continue

### File/Parsing Errors
- Missing config.yaml → Raise ConfigurationError
- Malformed JSON → Raise ValidationError, continue
- No input files for feed date/category → Log WARNING, exit with code 0

---

## Logging

### Format: JSON (one object per line)
**File**: `{scrape.log}/url-scraper-{FEED_DATE}.log`

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
.
├── url-scraper.py              # Main entry point
├── src/
│   └── url_scraper/            # Package
├── data/
│   ├── tech-trend-analysis/
│   │   └── {FEED_DATE}/      # Only process this directory
│   └── scraped-content/
│       └── {FEED_DATE}/      # Only write to this directory
├── .env                        # API keys (gitignored)
├── config.yaml                 # Configuration file
```

- DO NOT implement any logic in `url-scraper.py`. It's only for entry point.

---

### Entry Point
```bash
python url-scraper.py

python url-scraper.py --category "software_engineering"

python url-scraper.py --feed_date "2025-02-01"

python url-scraper.py --category "software_engineering" --feed_date "2025-02-01"
```

**category** and **feed_date** are optional input parameters.

---

## Idempotency
Before scraping each category:
- Check if the output file exists at:
`{scrape.url-scraped-content}/{FEED_DATE}/{category}/url-scrape.json`
- If exists → Log INFO, print "Skipping {category} (already processed for {FEED_DATE})", do not scrape again.

---

## Code Quality Standards

- **Max function length**: 50 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants

---

## Success Criteria
- Accessing, scrapping, cleaning, and storing web content successfully for the given feed date's categories
- Error duing accessing don't stop execution
- Idempotent: Running twice on same day produces same results
- All code has type hints and docstrings
- Graceful handling when no input data exists for today

---

## Implementation Notes

### DO NOT GENERATE
- `config.yaml` (provided at runtime)
- Test files