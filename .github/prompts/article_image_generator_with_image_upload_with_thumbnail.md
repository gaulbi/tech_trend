# Article Image Generator

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Tasks**: Modify a Python module implementation based on the detailed requirements below.

---

## Module Overview

**Purpose**: Use a Python library (i.e, Pillow) to generate a thumbnail image from an existing image, store it locally.
The module must be compitible with the existing code and production-ready with comprehensive error handling, retry logic, and logging.

---

## Configuration

### File: `./config.yaml`
```yaml                  
image-generator:
  image-path: data/image                      # Original image output folder
  thumbnail-image-path: data/thumbnail/       # Image output folder
  url-mapping-path: data/image-url-mapping    
  log: log/image-generator
```

**Validation**: Missing config.yaml → Raise `ConfigurationError` and exit.
-- 
## Process
Iterate process on each category
1. Parse markdown article and generate summary
2. Generate original image from summary using LLM provider
3. Store original image in `{image-generator.image-path}` folder
4. Generate thumbnail image from the original image using Pillow. 800x420 pixels - Resize maintaining aspect ratio.
5. Store thumbnail image in `{image-generator.thumbnail-image-path}` folder.
6. Upload the original image to ImgBB
7. Upload the thumbnail image to IamgeBB.
8. Save Image URL Mapping file with both original and thumbnail metadata

---
## Store Thumbnail Image
### Path
`{image-generator.thumbnail-image-path}/{FEED_DATE}/{category}/thumbnail-{original-file-name}.jpg`

### Example
- **Original Image**: `data/image/2025-11-26/software_engineering/model-context-protocol-mcp.jpg`
- **Thumbnail Image**: `data/thumbnail/2025-11-26/software_engineering/thumbnail-model-context-protocol-mcp.jpg`

---

## Output: Image URL Mapping
### Format
```json
{
  "article_file": "carbon-capture-and-storage.md",
  "category": "software_engineering",
  "feed_date": "2025-11-26",
  "local_path": "data/image/2025-11-26/software_engineering/carbon-capture-and-storage.jpg",
  "imgbb_url": "https://i.ibb.co/Y7KxCDDZ/carbon-capture-and-storage.jpg",
  "thumbnail_local_path": "data/thumbnail/2025-11-26/software_engineering/thumbnail-carbon-capture-and-storage.jpg",
  "thumbnail_imgbb_url": "https://i.ibb.co/Y7KxCDDZ/thumbnail-carbon-capture-and-storage.jpg",
  "uploaded_at": "2025-11-26T02:47:36.790110",
  "status": "success"
}
```
`thumbnail_local_path` and `thumbnail_imgbb_url` are added after a thumbnail image file is generated and uploaded.

---

## IMPORTANT
- Create thumbnail.py for
  - Generate and store a thumbnail image from an original image file
  - Create image only for newly created images.

- Modify imgbb.py for
  - The imgbb.py will is invoked two times. The first call is for the original image, and the second call is for the thumbnail image by processor.py.
  - Use the exsiting rety logic.

- Modify procesor.py for
  - Invoke thumbnail.py after original image generation
  - Upload thumbnail image after original image upload
  - Update URL mapping properly to have the original image metadata and the thumbnail image metadata.

- Modify exceptions.py, config.py and url_mapper.py accordingly

- **KEEP EXSITING LOGIC AS MUCH AS POSSIBLE**. Modify only if it's needed to implement requirements. 
---

## Error Handling

### File/Parsing Errors
- Missing config.yaml → Raise ConfigurationError

---

## Logging
### Format: JSON (one object per line)
**File**: `{image-generator.log}/image-generator-{FEED_DATE}.log`

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
- **WARNING**: Hashnode upload disabled, retry attempts

---

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
│       ├── imgbb.py                # ImgBB uploader
│       └── llm/
│           ├── __init__.py
│           ├── base.py             # Abstract base class
│           ├── factory.py          # Provider factory
│           ├── openai_provider.py
│           ├── deepseek_provider.py
│           └── gemini_provider.py
├── config.yaml                     # Configuration
├── .env                            # API keys (gitignored)
```

---

## Code Quality Standards

- **Max function length**: 50 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants

---