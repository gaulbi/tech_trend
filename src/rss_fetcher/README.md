# RSS Fetcher

Production-grade RSS feed fetcher with async support, retry logic, and structured logging.

## Features

- ✅ Asynchronous fetching with configurable concurrency
- ✅ Exponential backoff retry logic
- ✅ Structured JSON logging with rotation
- ✅ Colored console output
- ✅ Idempotent execution (skip already-fetched categories)
- ✅ Duplicate article detection per category
- ✅ Graceful error handling
- ✅ Progress reporting
- ✅ Comprehensive statistics

## Installation

```bash
pip install -r requirements.txt
```

## Project Structure

```
├── rss-fetcher.py              # Entry point
├── src/
│   └── rss_fetcher/
│       ├── __init__.py
│       ├── cli.py              # CLI interface
│       ├── config.py           # Configuration management
│       ├── fetcher.py          # Core fetching logic
│       ├── logger.py           # Logging setup
│       ├── orchestrator.py     # Process orchestration
│       ├── utils.py            # Utility functions
│       └── validator.py        # Validation logic
├── config.yaml                 # Configuration file
├── rss/
│   └── rss-feed.json          # RSS sources
├── data/
│   └── rss/
│       └── rss-feed/          # Output directory
└── log/
    └── rss-fetch/             # Log directory
```

## Configuration

Edit `config.yaml`:

```yaml
rss:
  rss-source: rss/rss-feed.json    # RSS sources file
  rss-feed: data/rss/rss-feed      # Output directory
  log: log/rss-fetch               # Log directory
  max-concurrent: 10               # Max parallel requests
  timeout: 30                      # HTTP timeout (seconds)
  retry: 3                         # Max retry attempts
```

## RSS Sources Format

Create `rss/rss-feed.json`:

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

## Usage

### Fetch All Categories (Today's Date)

```bash
python rss-fetcher.py
```

### Fetch Specific Category

```bash
python rss-fetcher.py --category "AI Hardware"
```

### Fetch for Specific Date

```bash
python rss-fetcher.py --feed_date "2025-02-01"
```

### Combined

```bash
python rss-fetcher.py --category "AI Hardware" --feed_date "2025-02-01"
```

## Output Format

Files are saved to `data/rss/rss-feed/{YYYY-MM-DD}/{category}.json`:

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

## Logging

Logs are saved to `log/rss-fetch/rss-fetcher-{YYYY-MM-DD}.log` in JSON format:

```json
{
  "timestamp": "2025-02-26T10:30:45.123456",
  "level": "ERROR",
  "module": "fetcher",
  "function": "fetch_feed",
  "line": 42,
  "message": "Error message",
  "traceback": "full traceback for errors"
}
```

## Error Handling

- **Network timeouts**: Retry with exponential backoff (1s, 2s, 4s)
- **Invalid RSS**: Log error, skip feed, continue
- **Missing config**: Raise `ConfigurationError` and exit
- **Invalid JSON**: Raise `ValidationError` and exit
- **Partial failures**: Continue processing other categories

## Idempotency

The fetcher checks if output files already exist before fetching:
- Existing files are skipped (logged and reported)
- Running twice produces identical results
- Safe to re-run for partial failures

## Performance

- Default: 10 concurrent requests
- Typical duration: <5 minutes for 100 feeds
- Progress reporting shows real-time status

## Example Output

```
Fetching [1/3] categories: AI Hardware
Skipping [2/3] categories: Software Engineering (already fetched)
Fetching [3/3] categories: DevOps

=== RSS Fetch Summary ===
Total categories: 3
Successful: 2
Failed: 0
Skipped: 1
Total articles: 247
Duration: 32.5 seconds
```

## Development

### Type Hints
All functions include type hints for better IDE support.

### Docstrings
Google-style docstrings for all public functions.

### Code Quality
- Max function length: 50 lines
- Max line length: 100 characters
- No hardcoded values (use config)

## License

MIT