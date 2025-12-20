# Article Publisher

A production-grade Python module for publishing technology articles to Hashnode using the GraphQL v2 API.

## Features

- ✅ Clean architecture with separation of concerns
- ✅ Comprehensive error handling with retry logic
- ✅ Structured JSON logging with rotation
- ✅ Type hints throughout
- ✅ Configurable via YAML
- ✅ Exponential backoff for retries
- ✅ Colored console output
- ✅ Google-style docstrings

## Project Structure

```
.
├── article-publisher.py              # Main entry point
├── src/
│   └── article_publisher/            # Package
│       ├── __init__.py
│       ├── config.py                 # Configuration management
│       ├── exceptions.py             # Custom exceptions
│       ├── logger.py                 # Logging utilities
│       ├── markdown_parser.py        # MD file parsing
│       ├── hashnode_client.py        # API client
│       └── publisher.py              # Main orchestrator
├── data/
│   └── tech-trend-article/           # Input articles
│       └── 2025-12-05/               # Today's articles
│           └── {category}/
│               └── *.md
├── log/
│   └── article-publisher/            # Log files
├── config.yaml                       # Configuration
├── .env                              # API keys
├── requirements.txt                  # Dependencies
└── README.md
```

## Installation

### Requirements
- Python 3.8+ (Python 3.9+ recommended for native timezone support)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```bash
# Hashnode API Key
HASHNODE_API_KEY=your_api_key_here
```

### 3. Update Configuration

Edit `config.yaml`:

```yaml
article-publisher:
  timeout: 60
  retry: 3
  log: log/article-publisher
  api-header: X-Hashnode-Api-Key
  server: https://gql.hashnode.com
  publication-id: YOUR_PUBLICATION_ID_HERE  # Required: must be alphanumeric
  timezone: America/New_York                 # Timezone for date determination
  rate-limit-delay: 1.0                      # Seconds between publishes

article-generator:
  tech-trend-article: data/tech-trend-article
```

## Usage

### Run Publisher

```bash
python article-publisher.py
```

### Input Format

Articles must be in Markdown format with this title structure:

```markdown
# [EN] Title: Your Article Title Here

Your article content goes here...
```

**Note**: Title will be automatically truncated to 250 characters if longer.

**Location**: `data/tech-trend-article/{TODAY_DATE}/{category}/*.md`

Where `{TODAY_DATE}` is automatically determined using `date.today()` in the configured timezone (default: America/New_York).

### Output

- **Console**: Colored logs (INFO and above)
- **File**: JSON logs at `log/article-publisher/article-publisher-{TODAY_DATE}.log`

### Exit Codes

- `0`: Success (all articles published)
- `1`: Failure (configuration error or publishing failures)

## Configuration Options

### article-publisher

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `timeout` | int | 60 | HTTP request timeout (seconds) |
| `retry` | int | 3 | Number of retry attempts |
| `log` | string | log/article-publisher | Log directory path |
| `api-header` | string | X-Hashnode-Api-Key | API key header name |
| `server` | string | https://gql.hashnode.com | GraphQL endpoint |
| `publication-id` | string | **REQUIRED** | Hashnode publication ID (alphanumeric) |
| `timezone` | string | America/New_York | Timezone for date determination |
| `rate-limit-delay` | float | 1.0 | Delay between publishes (seconds) |

### article-generator

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tech-trend-article` | string | data/tech-trend-article | Base input folder |

## Error Handling

### Network Errors
- **Timeout**: Configured timeout (default 60s)
- **Retry**: Exponential backoff (1s, 2s, 4s)
- **Action**: Log error, skip article, continue

### GraphQL Errors
- Logged with full error details
- Article skipped
- Processing continues

### File Parsing Errors
- Invalid title format → Warning logged, file skipped
- Empty files → Warning logged, file skipped
- Missing files → Warning logged

## Logging

### Console Output (Colored)
```
2025-12-05 10:30:15 - INFO - Article Publisher started
2025-12-05 10:30:16 - INFO - Processing articles from: data/tech-trend-article/2025-12-05
2025-12-05 10:30:16 - INFO - Found 5 markdown files
2025-12-05 10:30:17 - INFO - Successfully published: AI Trends 2025 (slug: ai-trends-2025)
2025-12-05 10:30:18 - WARNING - No title found in format '# [EN] Title: ...' in article2.md
2025-12-05 10:30:20 - INFO - Publishing completed: 4 succeeded, 1 failed
```

### File Output (JSON)
```json
{"timestamp": "2025-12-05T15:30:15.123456Z", "level": "INFO", "module": "publisher", "function": "publish_today_articles", "line": 85, "message": "Processing articles from: data/tech-trend-article/2025-12-05"}
{"timestamp": "2025-12-05T15:30:17.234567Z", "level": "INFO", "module": "hashnode_client", "function": "publish_article", "line": 120, "message": "Successfully published: AI Trends 2025 (slug: ai-trends-2025)"}
{"timestamp": "2025-12-05T15:30:18.345678Z", "level": "ERROR", "module": "hashnode_client", "function": "publish_article", "line": 135, "message": "GraphQL errors: Invalid title", "traceback": "..."}
```

## Code Quality

- ✅ Max function length: 79 lines
- ✅ Type hints on all functions
- ✅ Google-style docstrings
- ✅ Max line length: 100 characters
- ✅ No hardcoded values
- ✅ PEP 8 compliant

## Example Article

```markdown
# [EN] Title: The Future of AI in 2025

Artificial Intelligence continues to evolve at a rapid pace...

## Key Trends

1. **Multimodal AI**: Systems that understand text, images, and audio
2. **Edge Computing**: AI running on local devices
3. **Ethical AI**: Focus on responsible development

## Conclusion

The future looks promising with these exciting developments.
```

## Troubleshooting

### "Configuration file not found"
- Ensure `config.yaml` exists in the project root
- Check file permissions

### "HASHNODE_API_KEY environment variable not set"
- Create `.env` file in project root with your API key
- Or export: `export HASHNODE_API_KEY=your_key`
- Make sure `.env` file is in the same directory as `article-publisher.py`

### "No markdown files found"
- Verify date format: `YYYY-MM-DD`
- Check directory path in `config.yaml`
- Ensure files have `.md` extension

### "No title found in format"
- Article must start with: `# [EN] Title: Your Title`
- Check for typos in the title format
- Ensure there's text after "Title:"

### "Invalid 'article-publisher.publication-id' format"
- Publication ID must be alphanumeric (no spaces or special characters)
- Get your publication ID from Hashnode dashboard

### Rate Limiting
- Default 1 second delay between publishes
- Adjust `rate-limit-delay` in config.yaml if needed
- Set to 0 to disable rate limiting

## Development

### Running Tests
```bash
# Add your test framework here
pytest tests/
```

### Code Style
```bash
# Format with black
black src/

# Type check with mypy
mypy src/

# Lint with flake8
flake8 src/ --max-line-length=100
```

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.