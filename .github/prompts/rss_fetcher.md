# RSS Fetcher

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Task**: Generate a complete Python modules implementation based on this plan.

---

## Module Overview

**Purpose**: Fetch RSS feeds from multiple sources, organize by categories, save as structured JSON files

### Process Steps
1. Load config.yaml file to get module specific configuration.
2. Load RSS list file in `{rss.rss-source}` folder.
3. Get feed and store in JSON format.

### Feed Date
- If no date is specified in command, the feed date is today's date.
- Determine today's date using `datetime.date.today().strftime('%Y-%m-%d')`

---

## Configuration

**File**: `./config.yaml`

```yaml
rss:
  rss-source: rss/rss-feed.json        # RSS sources
  rss-feed: data/rss/rss-feed          # Output directory
  log: log/rss-fetch                   # Log directory
  max-concurrent: 10                   # Max parallel requests
  timeout: 30                          # HTTP timeout (seconds)
  retry: 3                             # Max retry attempts
```

**Validation**: Missing config.yaml → Raise `ConfigurationError` and exit

---

## Input: RSS List

### File:
**File Path**: `{rss.rss-source}`

### Format:
```json
{
  "AI Hardware": {
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/"
  },
  "Software Engineering": {
    "Hacker News": "https://hnrss.org/frontpage"
  }
}
```

**Validation**: Invalid JSON → Raise `ValidationError` with details

- RSS feed is organized by category (e.g. AI Machine Learning, Software Engineering). 
- If it's not specified, process all categories, one category at a time.
- Sanitize the category using below rules. 

**Category Sanitization Rules**:  
- Convert to lowercase
- Replace spaces and special characters with underscores
- Example: "AI & Hardware!" → "ai_hardware"

---

## Output

### File Path Format
`{rss.rss-feed}/{FEED_DATE}/{sanitized_category}.json`

### Example
If a feed date is _2025-02-26_ and a category is _AI & Hardware_, output file is `data/rss/rss-feed/2025-02-26/ai_hardware.json`

### JSON Structure
```json
{
  "category": "ai_hardware",    
  "feed_date": "2025-02-26",   
  "article_count": 2,
  "articles": [
    {
      "title": "Google releases AI chip",
      "link": "https://www.ai.com/article1"
    }
  ]
}
```

**Rules**:
- Required fields: `title` and `link` (skip articles missing these)
- Duplicate links: Keep first occurrence per category
- Empty feeds: Create JSON with `article_count: 0`, `articles: []`

---

## Error Handling

### Network Errors
- **Timeout**: 30 seconds per feed
- **Retry**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Action**: Log ERROR, skip feed, continue

### File/Parsing Errors
- Invalid RSS: Log ERROR, skip feed
- Missing config.yaml: Raise `ConfigurationError`
- Malformed RSS list JSON: Raise `ValidationError`

### Graceful Degradation
- Partial category failure: Continue with other categories
- All feeds fail in category: Create empty output file

---

## Logging

**File**: `{rss.log}/rss-fetcher-{FEED_DATE}.log`

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
3. Rotating file handler with 10MB limit keeping 5 backup files
4. JSON formatting option for structured logging
5. Function decorator to auto-log calls with timing
6. Error logging helper that captures stack traces
7. Configurable via environment variables or config file
8. Include example usage showing:
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

## Performance

### Concurrency
- Max 10 parallel requests using `asyncio` with `aiohttp`

### Progress Reporting
Print to stdout: `"Fetching [X/Y] categories: {category}"`

### Summary (at end)
```
Fetching [1/3] categories: AI Hardware
Skipping [2/3] categories: Tech News (already fetched)
Fetching [3/3] categories: DevOps

=== RSS Fetch Summary ===
Total categories: 5
Successful: 4
Failed: 1
Total articles: 247
Duration: 32.5 seconds
```

---

## Module Structure
```
├── rss-fetcher.py              # Main entry point
├── src/
│   └── rss_fetcher/            # Python codes
├── data/
│   ├── rss/
│   │   └── rss-feed/
│   │      └── {TODAY_DATE}/    # Only write to this directory
├── config.yaml                 # Configuration file
```

- DO NOT implement any logic in `rss-fetcher.py`. It's only for entry point.

### Entry Point
```bash
python rss-fetcher.py

python rss-fetcher.py --category "AI Machine Learning"

python rss-fetcher.py --feed_date "2025-02-01"

python rss-fetcher.py --category "AI Machine Learning" --feed_date "2025-02-01"
```

---

## Idempotency

**Before fetching each category**: Check if file exists at `{rss.rss-feed}/{FEED_DATE}/{sanitized_category}.json`
- **If exists**: Log INFO, print "Skipping...", don't fetch
- **If not exists**: Fetch all feeds for that category

---

## Code Quality Standards

- **Max function length**: 50 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants

---

## Success Criteria

- All valid feeds fetch successfully
- Invalid feeds don't stop execution
- Execution <5 minutes for 100 feeds
- Idempotent: Running twice produces same results
- All code has type hints and docstrings

---