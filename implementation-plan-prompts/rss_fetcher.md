# RSS Fetcher

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Task**: Generate a complete Python module implementation based on this plan.

---

## Module Overview

**Purpose**: Fetch RSS feeds from multiple sources, organize by categories, save as structured JSON files
**Behavior**: Single-run batch processor for **today's date only**  with idempotent behavior (skip already-fetched categories)

---

## Configuration

### File: `./config.yaml`
```yaml
rss:
  rss-list: data/rss/rss-list.json     # RSS sources
  rss-feed: data/rss/rss-feed          # Output directory
  log: log/rss-fetch                   # Log directory
  max-concurrent: 10                   # Max parallel requests
  timeout: 30                          # HTTP timeout (seconds)
  retry: 3                             # Max retry attempts
```

**Validation**: Missing config.yaml → Raise `ConfigurationError` and exit

---

## Input: RSS List

### File: From `config.yaml` → `rss.rss-list`

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

---

## Output

### File Path Format
`{rss.rss-feed}/{TODAY_DATE}/{sanitized_category}.json`

**TODAY_DATE**: Automatically determined using `datetime.date.today().strftime('%Y-%m-%d')`

### Example
If today is 2025-02-26
`data/rss/rss-feed/2025-02-26/software_engineering.json`

**Category Sanitization Rules**:
- Convert to lowercase
- Replace spaces and special characters with underscores
- Example: "AI & Hardware!" → "ai_hardware"

### JSON Structure
```json
{
  "category": "ai_hardware",    
  "fetch_date": "2025-11-26",   
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

### Format: JSON (one object per line)
**File**: `{rss.log}/rss-fetcher-{TODAY_DATE}.log`

### Fields
```json
{
  "timestamp": "2025-11-26T10:30:00+00:00",
  "level": "INFO|ERROR|DEBUG",
  "message": "Human-readable message",
  "category": "Category name (optional)",
  "feed_url": "URL (optional)",
  "status": "success|failure|skipped (optional)",
  "error_message": "Details (optional)"
}
```

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
- Rate limit: Max 2 requests/second per domain

### Progress Reporting
Print to stdout: `"Fetching [X/Y] categories: {category_name}"`

### Summary (at end)
```
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
│   └── rss_fetcher/            # Package
├── data/
│   ├── rss/
│   │   └── rss-feed/
│   │      └── {TODAY_DATE}/    # Only write to this directory
├── config.yaml                 # Configuration file
```

### Entry Point
```bash
python rss-fetcher.py
```

### Module Responsibilities

**main.py**: Orchestrate workflow, progress reporting, statistics

**config_loader.py**: Load and validate config.yaml with Pydantic

**rss_fetcher.py**: Async RSS fetching with retry logic and rate limiting

**models.py**: 
- `Config`: Pydantic model for config.yaml
- `Article`, `CategoryOutput`: Data models
- Custom exceptions: `ConfigurationError`, `ValidationError`

**logger.py**: Setup JSON structured logging with rotation

**utils.py**: 
- `sanitize_category_name()`: Transform category names
- `is_today_file_exists()`: Check if category already fetched today

---

## Required Libraries

```
feedparser>=6.0.11
aiohttp>=3.9.0
pydantic>=2.5.0
pyyaml>=6.0.1
```

---

## Idempotency

**Before fetching each category**: Check if file exists at `{rss.rss-feed}/{today}/{category}.json`
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

## Implementation Notes

### DO NOT GENERATE
- `config.yaml` (provided at runtime)
- Test files

### MUST GENERATE
- Complete working module in `src/`
- `requirements.txt`
- All functions fully implemented

### Example Execution
```bash
pip install -r requirements.txt
python src/rss-fetcher.py
```

**Output**:
```
Fetching [1/3] categories: AI Hardware
Skipping [2/3] categories: Tech News (already fetched)
Fetching [3/3] categories: DevOps

=== RSS Fetch Summary ===
Total categories: 3
Successful: 2
Skipped: 1
Total articles: 156
Duration: 18.3 seconds
```