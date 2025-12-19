# Article Image Generator

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Tasks**: Generate a complete Python module implementation based on the detailed requirements below.

---

## Module Overview

**Purpose**: Use AI API to generate image that will be used in technical article, store it locally, and upload to Hashnode.
The module must be production-ready with comprehensive error handling, retry logic, and logging.

### Feed Date
- If no date is specified in command, the feed date is today's date.
- Determine today's date using `datetime.date.today().strftime('%Y-%m-%d')`

---

## Configuration

### File: `./config.yaml`
```yaml
article-generator:
  tech-trend-article: data/tech-trend-article   #Base input folder
  log: log/article-generator                       # Log directory
image-generator:
  image-path: data/image                      #Base output folder
  url-mapping-path: data/image-url-mapping    # URL mapping storage
  log: log/image-generator
  timeout: 60
  retry: 3 
  provider: Gemini                     # Gemini, Deepseek, OpenAI
  llm-model: gemini-2.5-flash-image     # gemini-2.5-flash-image, DeepSeek-V2.5, dall-e-3
  default-size: 1024
  aspect-ratio: "1:1"   # square | wide | tall
  style-instruction: "Create a clean, modern, vector-style illustration that visually represents the following technical concept. Use flat colors and avoid text."
  output-format: "jpg"
hashnode:
  upload-enabled: true                   # Enable/disable Hashnode upload
  timeout: 30
  retry: 3
  url: https://api.hashnode.com/
```

**Validation**: Missing config.yaml → Raise `ConfigurationError` and exit.

---

## Input: Tech Trend Analysis

### File Path
`{article-generator.tech-trend-article}/{FEED_DATE}/{category}/*.md`

### Example
If a feed date is _2025-11-26_ and a category is software_engineering,
`data/tech-trend-analysis/2025-11-26/software_engineering/model-context-protocol-mcp.md`
`data/tech-trend-analysis/2025-11-26/software_engineering/linux-kernel.md`
``

### Format
```md
## 1. [EN] English Article

## Title  
... 

**Date/Time**: 2025-12-11 00:00

## Summary  
...

## Full Article  
...

```

**Validation**: Invalid MD structure → Raise `ValidationError` and continue processing remaining categories.

**Note**:
- Extract content between `## Summary` and `## Full Article`, and use it as prompt to pass LLM API to generate image.
- DO NOT include content in `## Full Article` in the prompt.

---

## Output

1. Local Image Storage
**File Path**: `{image-generator.image-path}/{FEED_DATE}/{category}/{article-file-name}.jpg`

**Example**: If a feed date is _2025-11-26_, a category is software_engineering, and article file name is model-context-protocol-mcp.md, 
`data/image/2025-11-26/software_engineering/model-context-protocol-mcp.jpg`

2. Hashnode Upload
After successfully generating and saving the local image:
  1. Upload the image to Hashnode using their upload API
  2. Retrieve the Hashnode CDN URL from the response
  3. Store the URL mapping locally

3. URL Mapping Storage
**File Path**: {image-generator.url-mapping-path}/{FEED_DATE}/{category}/{article-file-name}.json
**Example**: data/image-url-mapping/2025-11-26/software_engineering/model-context-protocol-mcp.json
**Format**:  

```json
{
  "article_file": "model-context-protocol-mcp.md",
  "category": "software_engineering",
  "feed_date": "2025-11-26",
  "local_path": "data/image/2025-11-26/software_engineering/model-context-protocol-mcp.jpg",
  "imgbb_url": "https://i.ibb.co/Sw1jqR40/model-context-protocol-mcp.png",
  "uploaded_at": "2025-11-26T10:30:45.123456",
  "status": "success"
}
```
***Status Values***:  
- `success`: Image uploaded successfully
- `upload_failed`: Image generated but Hashnode upload failed
- `upload_disabled`: Hashnode upload is disabled in config

---

## Hashnode Integration

### API Endpoint
**POST**: `{hashnode.url}`
Use GraphQL mutation for image upload:
```graphql
mutation UploadImage($input: UploadImageInput!) {
  uploadImage(input: $input) {
    url
  }
}
```

### Authentication
Load Hashnode API token from `.env` file:

```
HASHNODE_API_KEY=your_hashnode_api_token
```

Include in request headers:
```
Authorization: {HASHNODE_API_KEY}
```

### Request Format
- Content-Type: `multipart/form-data`
- Include the image file in the request
- Refer to Hashnode API documentation for exact multipart format

### Error Handling for Hashnode Upload
- **Network Errors**: Retry 3 times with exponential backoff (1s, 2s, 4s)
- **Authentication Errors**: Log ERROR, save URL mapping with status upload_failed
- **Rate Limiting**: Log WARNING, wait and retry
- **Upload Failure**: Log ERROR, save local image path in URL mapping with status upload_failed
- **Note**: If Hashnode upload fails, the process should continue (local image is still saved)

### Upload Disabled
If `{imgbb.upload-enabled}` is false:
- Skip image upload to ImgBB
- Save URL mapping with status `upload_disabled` and `imgbb_url: null`

---

## Multi-LLM Provider Support
- Support multiple LLM providers: **OpenAI**, **DeepSeek**, **Gemini**
- Use a **Factory Pattern** to create appropriate LLM clients
- All LLM clients must inherit from an **Abstract Base Class**
- Load API keys from **`.env` file**

---

## Image Specification
```yaml
  default-size: 1024
  aspect-ratio: "1:1"   # square | wide | tall
  style-instruction: "Create a clean, modern, vector-style illustration that visually represents the following technical concept. Use flat colors and avoid text."
  output-format: "jpg"
```
- If LLM model doesn't support a specification, ignore it. For instance, if **gemini-2.5-flash-image** doesn't support `default-size`, do not apply it.

---

## Error Handling

### Network Errors
- **Timeout**: use timeout in config.yaml
- **Retry**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Action**: Log ERROR, skip generate image of the md file, continue

### File/Parsing Errors
- Missing config.yaml → Raise ConfigurationError
- Malformed md file → Raise ValidationError, continue
- No input files for feed date/category → Log WARNING, exit with code 0

### Hashnode Upload Errors
- Upload failure → Log ERROR, save URL mapping with `upload_failed` status, continue
- Missing API key → Log ERROR, save URL mapping with `upload_failed` status, continue
- Network timeout → Retry with exponential backoff, if all retries fail, save with `upload_failed` status

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

### Rotation
- Daily rotation, keep 30 days

---

## Project Structure
```
.
├── image-generator.py              # Main entry point
├── src/
│   └── image_generator/            # Package
├── data/
│   ├── image/
│   │   └── {FEED_DATE}/      # Only write to this directory
│   ├── image-url-mapping/
│   │   └── {FEED_DATE}/      # URL mapping storage
│   └── data/tech-trend-article/
│       └── {FEED_DATE}/      
├── .env                        # API keys (gitignored)
├── config.yaml                 # Configuration file
```

- DO NOT implement any logic in `image-generator.py`. It's only for entry point.

### Entry Point
```bash
python image-generator.py

python image-generator.py --category "software_engineering"

python image-generator.py --feed_date "2025-02-01"

python image-generator.py --category "software_engineering" --feed_date "2025-02-01" --file_name "model-context-protocol.md"
```
- **category**, **feed_date** and **file_name** are optional input parameters.
- **category** and **feed_date** are required to use **file_name**.

---

## Idempotency
Before searching each category:
1. Check if the output file exists at:
`{image-generator.image-path}/{FEED_DATE}/{category}/{article-file-name}.jpg`
2. Check if the URL mapping file exists at:
`{image-generator.url-mapping-path}/{FEED_DATE}/{category}/{article-file-name}.json`

**If both exist and URL mapping status is `success`**:  
- Log INFO, print "Skipping {article-file-name} (already processed for {category}/{FEED_DATE})"
- Do not generate or upload again

**If image exists but URL mapping is missing or status is upload_failed**:  
- Skip image generation
- Attempt Hashnode upload only
- Update URL mapping

**If neither exists**:
- Generate image, save locally, upload to Hashnode, save URL mapping

---

## Code Quality Standards

- **Max function length**: 50 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants

---

## Implementation Notes

### DO NOT GENERATE
- `config.yaml` (provided at runtime)
- Test files

## Environment Setup (.env file)

```bash

# OpenAI API Key
OPENAI_IMG_API_KEY=...

# Deep AI
DEEPSEEK_IMG_API_KEY=...

# Gemini API Key
GEMINI_IMG_API_KEY=...

# Hashnode API Key
HASHNODE_API_KEY=...
```
---

## Processing Flow
For each article:  
1. **Generate Image** → Save to local path
2. **Upload to Hashnode** (if enabled) → Get CDN URL
3. **Save URL Mapping** → Store local path, Hashnode URL, and status
4. **Log Results** → INFO for success, ERROR for failures