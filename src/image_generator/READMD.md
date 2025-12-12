# Article Image Generator

Production-ready Python module that uses AI APIs to generate images for technical articles.

## Features

- **Multi-LLM Provider Support**: OpenAI (DALL-E), DeepSeek, Google Gemini
- **Factory Pattern**: Clean architecture with abstract base classes
- **Comprehensive Error Handling**: Network errors, timeouts, retries with exponential backoff
- **Advanced Logging**: JSON-formatted logs with rotation, colored console output
- **Idempotency**: Skips already-processed files
- **Flexible CLI**: Process all files, specific categories, or individual files

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with API keys:
```bash
# OpenAI API Key
OPENAI_IMG_API_KEY=your_openai_key

# DeepSeek API Key
DEEPSEEK_IMG_API_KEY=your_deepseek_key

# Gemini API Key
GEMINI_IMG_API_KEY=your_gemini_key
```

3. Ensure `config.yaml` exists in the project root (see Configuration section)

## Usage

### Process all files for today:
```bash
python image-generator.py
```

### Process specific category:
```bash
python image-generator.py --category software_engineering
```

### Process specific date:
```bash
python image-generator.py --feed_date 2025-02-01
```

### Process specific file:
```bash
python image-generator.py --category software_engineering --feed_date 2025-02-01 --file_name model-context-protocol.md
```

## Configuration

The `config.yaml` file controls all aspects of the image generation:

```yaml
scrape:
  url-scraped-content: data/scraped-content
  log: log/scraped-content
  max-search-results: 5

image-generator:
  image-path: data/image
  log: log/image-generator
  timeout: 60
  retry: 3
  provider: Deepseek              # Gemini, Deepseek, OpenAI
  llm-model: DeepSeek-V2.5        # gemini-2.5-flash-image, DeepSeek-V2.5, dall-e-3
  default-size: 1024
  aspect-ratio: "1:1"             # square | wide | tall
  style-instruction: "Create a clean, modern, vector-style illustration..."
  output-format: "jpg"
```

## Project Structure

```
.
├── image-generator.py                    # Entry point
├── src/
│   └── image_generator/
│       ├── __init__.py
│       ├── cli.py                        # Command-line interface
│       ├── config.py                     # Configuration management
│       ├── exceptions.py                 # Custom exceptions
│       ├── logger.py                     # Advanced logging
│       ├── parser.py                     # Markdown parser
│       ├── processor.py                  # Main processing logic
│       └── llm/
│           ├── __init__.py
│           ├── base.py                   # Abstract base class
│           ├── factory.py                # Factory pattern
│           ├── openai_provider.py        # OpenAI implementation
│           ├── deepseek_provider.py      # DeepSeek implementation
│           └── gemini_provider.py        # Gemini implementation
├── data/
│   ├── scraped-content/                  # Input markdown files
│   └── image/                            # Generated images
├── log/                                  # Log files
├── .env                                  # API keys (gitignored)
├── config.yaml                           # Configuration
└── requirements.txt                      # Dependencies
```

## Input Format

Markdown files should follow this structure:

```markdown
## 1. [EN] English Article

## Title  
Article Title

**Date/Time**: 2025-12-11 00:00

## Summary  
Article summary content here...

## Full Article  
Full article content...
```

The generator extracts content between `## Summary` and `## Full Article` to create the image prompt.

## Output

Generated images are saved to:
```
data/image/{FEED_DATE}/{category}/{article-file-name}.jpg
```

## Error Handling

- **Network Errors**: 3 retry attempts with exponential backoff (1s, 2s, 4s)
- **Timeouts**: Configurable timeout from config.yaml
- **Validation Errors**: Logs error, continues with next file
- **Missing Config**: Raises ConfigurationError and exits

## Logging

Logs are written to `log/image-generator/image-generator-{FEED_DATE}.log` in JSON format:

```json
{
  "timestamp": "2025-12-11T10:30:45.123456",
  "level": "INFO",
  "module": "processor",
  "function": "process_file",
  "line": 123,
  "message": "Successfully generated image",
  "traceback": null
}
```

- **Daily rotation** with 30-day retention
- **Colored console output** for easy reading
- **Multiple log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Code Quality

- **Type hints**: All function signatures
- **Google-style docstrings**: All public functions
- **Max function length**: 50 lines
- **Max line length**: 100 characters
- **No hardcoded values**: Everything in config or constants

## License

Proprietary - Internal use only
