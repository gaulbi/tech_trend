# Wiki Search

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Tasks**: Generate a complete Python module implementation based on the detailed requirements below.

---

## Module Overview

**Purpose**: Search keywords against Wikipedia, extract/clean content, and store cleaned content.  
The module must be production-ready with comprehensive error handling, retry logic, and logging.

### Feed Date
- If no date is specified in command, the feed date is today's date.
- Determine today's date using `datetime.date.today().strftime('%Y-%m-%d')`

---

## Configuration

### File: `./config.yaml`
```yaml
tech-trend-analysis:
  analysis-report: data/tech-trend-analysis   #Base source folder
scrape:
  url-scraped-content: data/scraped-content   #Base output folder
  log: log/scraped-content                        # Log directory
  max-search-results: 5                        # Max number of search results to search per query
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
`{scrape.url-scraped-content}/{FEED_DATE}/{category}/wiki-search.json`

### Example
If a feed date is _2025-11-26_ and a category is software_engineering, 
`data/scraped-content/2025-11-26/software_engineering/wiki-search.json`

### JSON Structure
```json
{
  "feed_date": "2025-11-26",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "...",
      "query_used": "...",
      "search_link": "...",
      "content": "...",
    }
  ]
}
```
**Note**: 
- One input trend may result in multiple output trend objects
- Every Wikipedia page scraped should appear separately in `trends`.
- `search_link`: Wiki page link
- `query_used`: The actual query sent to Wikipedia

## Date Processing Logic
- **Input Directory**: Only scan `{tech-trend-analysis.analysis-report}/{FEED_DATE}/` for category JSON files
- **Output Directory**: Write all results to `{scrape.url-scraped-content}/{FEED_DATE}/{category}/`

---

### Wikiepedia Search Logic
For each category → each trend → each keyword:
1. **Treat the search keyword string** exactly as provided (no tokenization).  
  Example: "frontier class AI models" is used as-is.
2. **Perform search**
- Use the `wikipedia` package
- Retrieve up to `{scrape.max-search-results}` titles
3. **Fetch page content** for each title found
4. **Clean content**
- Remove citation markers (`[1]`, `[23]`, `[citation needed]`)
- Remove entire section headings like `"== References =="` and anything after
- Normalize whitespace (collapse multiple spaces/newlines)
5. **Append cleaned content** as a trend entry

---

## Error Handling

### 0 Results Wiki Search
- **Action**: Log WARN, continue

### Network Errors
- **Timeout**: use the default timeout(15s) of wikipedia API
- **Retry**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Action**: Log ERROR, skip search that trend, continue

### File/Parsing Errors
- Missing config.yaml → Raise ConfigurationError
- Malformed JSON → Raise ValidationError, continue
- No input files for feed date/category → Log WARNING, exit with code 0

### Partial Failure
- If processing 3 keywords and 2 succeed but 1 fails, use successful search results.

---

## Logging

### Format: JSON (one object per line)
**File**: `{scrape.log}/wiki-search-{FEED_DATE}.log`
---

## Project Structure
```
.
├── wiki-search.py              # Main entry point
├── src/
│   └── wiki_search/            # Package
├── data/
│   ├── tech-trend-analysis/
│   │   └── {FEED_DATE}/      # Only process this directory
│   └── scraped-content/
│       └── {FEED_DATE}/      # Only write to this directory
├── .env                        # API keys (gitignored)
├── config.yaml                 # Configuration file
```

- DO NOT implement any logic in `wiki-search.py`. It's only for entry point.

### Entry Point
```bash
python wiki-search.py

python wiki-search.py --category "software_engineering"

python wiki-search.py --feed_date "2025-02-01"

python wiki-search.py --category "software_engineering" --feed_date "2025-02-01"
```
**category** and **feed_date** are optional input parameters.

---

## Idempotency
Before searching each category:
- Check if the output file exists at:
`{scrape.url-scraped-content}/{FEED_DATE}/{category}/wiki-search.json`
- If exists → Log INFO, print "Skipping {category} (already processed for {FEED_DATE})", do not search again.

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
- Searching, cleaning, and storing wiki content successfully for the given feed date's categories
- Invalid search response don't stop execution
- Idempotent: Running twice on same day produces same results
- All code has type hints and docstrings
- Graceful handling when no input data exists for the given feed date

---

## Implementation Notes

### DO NOT GENERATE
- `config.yaml` (provided at runtime)
- Test files
