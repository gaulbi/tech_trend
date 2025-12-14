# Article Image Generator

Production-ready Python module for generating AI-powered images for technical articles and uploading them to Hashnode.

## Features

- **Multi-LLM Support**: OpenAI (DALL-E), DeepSeek, and Google Gemini
- **Automatic Upload**: Upload generated images to Hashnode CDN
- **Idempotent Processing**: Skip already processed articles
- **Robust Error Handling**: Retry logic with exponential backoff
- **Comprehensive Logging**: JSON-structured logs with rotation
- **URL Mapping**: Track local and CDN URLs for all images

## Project Structure

```
.
├── image-generator.py              # Main entry point
├── src/
│   └── image_generator/
│       ├── __init__.py
│       ├── main.py                 # Orchestration
│       ├── config.py               # Configuration management
│       ├── exceptions.py           # Custom exceptions
│       ├── logger.py               # Advanced logging
│       ├── parser.py               # Markdown parser
│       ├── processor.py            # Main processor
│       ├── hashnode.py             # Hashnode uploader
│       ├── url_mapper.py           # URL mapping storage
│       └── llm/
│           ├── __init__.py
│           ├── base.py             # Abstract base class
│           ├── factory.py          # Provider factory
│           ├── openai_provider.py
│           ├── deepseek_provider.py
│           └── gemini_provider.py
├── data/
│   ├── tech-trend-article/         # Input articles
│   ├── image/                      # Generated images
│   └── image-url-mapping/          # URL mappings
├── log/                            # Log files
├── config.yaml                     # Configuration
├── .env                            # API keys (gitignored)
└── requirements.txt
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Choose one or more based on your provider
OPENAI_IMG_API_KEY=sk-...
DEEPSEEK_IMG_API_KEY=...
GEMINI_IMG_API_KEY=...

# Required for Hashnode upload
HASHNODE_API_KEY=...
```

### 3. Configure Application

Ensure `config.yaml` exists with your settings (see requirements document for full structure).

## Usage

### Process All Articles for Today

```bash
python image-generator.py
```

### Process Specific Category

```bash
python image-generator.py --category "software_engineering"
```

### Process Specific Date

```bash
python image-generator.py --feed_date "2025-02-01"
```

### Process Single File

```bash
python image-generator.py --category "software_engineering" \
  --feed_date "2025-02-01" \
  --file_name "model-context-protocol.md"
```

## Configuration

Key configuration options in `config.yaml`:

- **Provider Selection**: Choose between OpenAI, Deepseek, or Gemini
- **Upload Control**: Enable/disable Hashnode uploads
- **Image Specifications**: Size, aspect ratio, output format
- **Retry Settings**: Timeout and retry attempts
- **Style Instructions**: Custom prompts for image generation

## Output

### Generated Images

```
data/image/{FEED_DATE}/{category}/{article-name}.jpg
```

### URL Mappings

```
data/image-url-mapping/{FEED_DATE}/{category}/{article-name}.json
```

Example mapping:
```json
{
  "article_file": "model-context-protocol-mcp.md",
  "category": "software_engineering",
  "feed_date": "2025-11-26",
  "local_path": "data/image/2025-11-26/software_engineering/model-context-protocol-mcp.jpg",
  "hashnode_url": "https://cdn.hashnode.com/res/hashnode/image/upload/v1234567890/xyz.jpg",
  "uploaded_at": "2025-11-26T10:30:45.123456",
  "status": "success"
}
```

## Logging

Logs are written to:
```
log/image-generator/image-generator-{FEED_DATE}.log
```

JSON format with:
- Timestamp (ISO format)
- Log level
- Module, function, line number
- Message and context
- Full traceback for errors

Console output uses colored formatting for easy reading.

## Error Handling

- **Network Errors**: 3 retries with exponential backoff (1s, 2s, 4s)
- **Validation Errors**: Log and continue with remaining files
- **Upload Failures**: Save local image, mark as `upload_failed`
- **Missing API Keys**: Clear error messages with configuration help

## Idempotency

The system automatically skips files that have been successfully processed:
- Checks for existing local image
- Checks for URL mapping with `success` status
- Only re-uploads if status is `upload_failed` or `upload_disabled`

## Code Quality

- Type hints on all functions
- Google-style docstrings
- Max 50 lines per function
- Max 100 characters per line
- No hardcoded values
- Comprehensive error handling

## License

[Your License Here]
