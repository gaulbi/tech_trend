# URL Scraper

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Tasks**: Generate a complete Python module implementation based on this plan.

---

## Module Overview

**Purpose**: Retreive content of given URLs and remove characters that are not relevant the content, such as HTML tag, reference indicator, and image link.
**Behavior**: Single-run batch processor for **today's date only** with idempotent behavior (skip categories that already have output files).

---

### Configuration
```yaml
tech-trend-analysis:
  analysis-report: data/tech-trend-analysis     #Base source folder
scrap:
  url-scrapped-content: data/scrapped-content   #Base output folder
  timeout: 60
  log: log/scrapped-content 
```

**Validation**: Missing config.yaml → Raise `ConfigurationError` and exit.

---

## Input: Tech Trend Analysis

### File Path
`{tech-trend-analysis.analysis-report}/{TODAY_DATE}/{category}.json`

**TODAY_DATE**: Automatically determined using `datetime.date.today().strftime('%Y-%m-%d')`

## Example
If today is 2025-11-26:
`data/tech-trend-analysis/2025-11-26/software_engineering.json`

## Format
```json
{
  "analysis_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "AI Agents",
      "reason": "Rising popularity in enterprise...",
      "links": ["https://example.com/article1", "https://example.com/article2"],
      "search_keywords": ["AI", "Agents"]
    }
  ]
}
```

**Validation**: 
- Invalid JSON → Raise ValidationError and continue with remaining categories.
- No files for today's date → Log WARNING and exit gracefully.

---

## Output

### File Path
`{scrap.url-scrapped-content}/{TODAY_DATE}/{category}/url-scrap.json`

### Example
If today is 2025-11-26:
`data/scrapped-content/2025-11-26/software_engineering/url-scrap.json`

### JSON Structure
_Note: The output flattens the input. Each link from the input becomes a distinct object in the output list._
```json
{
  "analysis_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "AI Agents",
      "link": "https://example.com/article1",
      "content": "Extracted readable text content from article 1...",
      "search_keywords": ["AI", "Agents"]
    },
    {
      "topic": "AI Agents",
      "link": "https://example.com/article2",
      "content": "Extracted readable text content from article 2...",
      "search_keywords": ["AI", "Agents"]
    }
  ]
}
```

# Processing Logic

## Date Processing Logic
- **Automatic Date Detection**: Module automatically determines today's date at runtime
- **Input Directory**: Only scan `{analysis-report}/{TODAY_DATE}/` for category JSON files
- **Output Directory**: Write all results to `{url-scrapped-content}/{TODAY_DATE}/{category}/`
- **No Historical Processing**: Ignore all data from previous dates

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
- **Action**: Log ERROR, skip scraping that trend, continue

### File/Parsing Errors
- Missing config.yaml → Raise ConfigurationError
- Malformed JSON → Raise ValidationError, continue
- No input files for today → Log WARNING, exit with code 0

---

## Logging

### Format: JSON (one object per line)
**File**: `{scrap.log}/url-scraper-{TODAY_DATE}.log`

---

## Project Structure
```
.
├── url_scraper.py              # Main entry point
├── src/
│   └── url_scraper/            # Package
├── data/
│   ├── tech-trend-analysis/
│   │   └── {TODAY_DATE}/      # Only process this directory
│   └── scrapped-content/
│       └── {TODAY_DATE}/      # Only write to this directory
├── .env                        # API keys (gitignored)
├── config.yaml                 # Configuration file
```
---

## Idempotency
Before scraping each category:
- Check if the output file exists at:
`{scrap.url-scrapped-content}/{TODAY_DATE}/{category}/web-scrap.json`
- If exists → Log INFO, print "Skipping {category} (already processed for {TODAY_DATE})", do not scrape again.

---

## Code Quality Standards

- **Max function length**: 50 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants

---

## Success Criteria

- Automatically processes only today's date without manual date input
- Accessing, scrapping, cleaning, and storing web content successfully for today's categories
- Error duing accessing don't stop execution
- Idempotent: Running twice on same day produces same results
- All code has type hints and docstrings
- Graceful handling when no input data exists for today

---

## Implementation Notes

### DO NOT GENERATE
- `config.yaml` (provided at runtime)
- Test files