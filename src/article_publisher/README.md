# Article Publisher

A production-ready Python module for publishing technology articles to Hashnode using the GraphQL v2 API.

## Features

- ✅ Complete error handling with retry logic
- ✅ Comprehensive JSON logging
- ✅ Idempotency checking
- ✅ Title extraction from markdown
- ✅ Image URL injection
- ✅ Published datetime injection
- ✅ Category-based organization
- ✅ Single file or batch publishing
- ✅ Clean architecture with type hints

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Create `.env` file

```bash
HASHNODE_API_KEY=your_api_key_here
```

### 2. Ensure `config.yaml` exists

See the provided `config.yaml` template in the project root.

## Usage

### Publish all articles for today

```bash
python article-publisher.py
```

### Publish all articles for specific date

```bash
python article-publisher.py --feed_date "2025-02-01"
```

### Publish specific category

```bash
python article-publisher.py --category "software_engineering"
```

### Publish specific article

```bash
python article-publisher.py --category "software_engineering" \
    --feed_date "2025-02-01" \
    --file_name "model-context-protocol.md"
```

## Project Structure

```
.
├── article-publisher.py              # Main entry point
├── src/
│   └── article_publisher/            # Package
│       ├── __init__.py
│       ├── cli.py                    # Command-line interface
│       ├── config.py                 # Configuration management
│       ├── core.py                   # Core publishing logic
│       ├── exceptions.py             # Custom exceptions
│       ├── hashnode.py               # Hashnode API client
│       ├── loader.py                 # Article/mapping loaders
│       ├── logger.py                 # Logging utilities
│       ├── models.py                 # Data models
│       ├── processor.py              # Content processing
│       └── storage.py                # Result storage
├── data/
│   ├── tech-trend-article/           # Input articles
│   ├── image-url-mapping/            # Image URL mappings
│   └── published-tech-trend-article/ # Publish results
├── log/                              # Log files
├── config.yaml                       # Configuration
├── .env                              # Environment variables
└── requirements.txt                  # Dependencies
```

## How It Works

### Process Flow

1. **Load Article**: Reads markdown file from `data/tech-trend-article/{date}/{category}/`
2. **Extract Title**: Parses title between `## Title` and `**Date/Time**:`
3. **Load Image Mapping**: Reads `imgbb_url` from JSON mapping file
4. **Process Content**:
   - Injects current datetime
   - Replaces `image_url_tag_here` with image markdown
5. **Publish to Hashnode**: Uses GraphQL v2 API
6. **Save Result**: Creates status JSON in `data/published-tech-trend-article/`

### Idempotency

The publisher checks for existing result files before publishing. If an article has already been published (result file exists), it will be skipped.

To force republishing, use the `--file_name` option which bypasses idempotency checks.

## Error Handling

- **Network errors**: 3 retries with exponential backoff (1s, 2s, 4s)
- **GraphQL errors**: Logged with full details
- **Missing files**: Graceful skip with warning
- **All errors**: Logged to both console and JSON log file

## Logging

Logs are written to: `log/article-publisher/article-publisher-{feed_date}.log`

Format: JSON with timestamp, level, module, function, line, message, and traceback.

Console output includes colored levels for better readability.

## Code Quality

- Max function length: 79 lines
- Type hints on all function signatures
- Google-style docstrings
- Max line length: 100 characters
- No hardcoded values

## License

Proprietary - Internal Use Only
