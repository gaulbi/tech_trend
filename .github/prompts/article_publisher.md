# Article Publisher

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Task**: Generate a complete, runnable Python module that satisfies all requirements below.

---

## Module Overview

**Purpose**: Publish **today’s technology articles** (Markdown files) to Hashnode using the v2 GraphQL API.

### Feed Date
- If no date is specified in command, the feed date is today's date.
- Determine today's date using `datetime.date.today().strftime('%Y-%m-%d')`

---

## Configuration

### File: `./config.yaml`
```yaml
article-publisher:
  timeout: 60
  retry: 3
  log: log/article-publisher
  api-header: X-Hashnode-Api-Key
  server: https://gql.hashnode.com
  publication-id: 69337c78b74a62fa02a93b49
  timezone: America/New_York
article-generator:
  tech-trend-article: data/tech-trend-article       # base input folder
image-generator:
  image-path: data/image
```

**Validation**:
- Missing `config.yaml` → Raise `ConfigurationError` and exit.
- Missing `article-publisher.publication-id` → Raise `ConfigurationError`.

---

## Hashnode Publishing (GraphQL v2)
Use the `createStory` mutation:
```graphql
mutation CreateStory($input: CreateStoryInput!) {
  createStory(input: $input) {
    post { 
      id 
      slug 
    }
  }
}
```

### Required Input Fields:
- `title`: Refer **### Extracted Title**
- `contentMarkdown`: Full Markdown content
- `publicationId`: Loaded from `article-publisher.publication-id`
- `tags`: Optional → default to empty list `[]`

### HTTP Requirements:
- Method: POST with JSON body
- Header name: Value from `article-publisher.api-header`
- Header value: From environment variable `HASHNODE_API_KEY`
- Timeout: From `article-publisher.timeout` (seconds)

---

## Input Data: Tech Trend Articles

### Path
`{article-generator.tech-trend-article}/{FEED_DATE}/{category}/*.md `

### Example
If a feed date is 2025-11-25 and a category is software_engineering,
`data/tech-trend-analysis/2025-11-26/software_engineering/model-context-protocol-mcp.md`

### Processing Rules
- Process articles one by one (order not important).
- Skip empty files.
- Log all skip events.


### Extracted Title
The `title` is one line between `## Title` and `**Date/Time**:`


```md
## 1. [EN] English Article

## Title  
_title here_

**Date/Time**: 
```

**Example**  
If the article has below content, `title` is _Model Context Protocol (MCP)_.
```md
## 1. [EN] English Article

## Title  
Model Context Protocol (MCP)

**Date/Time**: 2025-12-11 00:00
```

#### Validation
- If MD file has invalid structure, use article file name as title.
- Replace all underscores to space.
- Convert it to compatible to a general article title naming.

**Example**:  
if an article file path is `data/tech-trend-analysis/2025-11-26/software_engineering/model-context-protocol-mcp-of-ai-agent.md`, title is _Model Context Protocol of AI Agent_.


---

## Input Data: Images for Articles

### Path
`{image-generator.image-path}/{FEED_DATE}/{category}/{article_file_name_with_extention}.jpg`

### Example
If an article file path is `data/tech-trend-analysis/2025-11-26/software_engineering/model-context-protocol-mcp.md`, image file path is `data/image/2025-11-26/software_engineering/model-context-protocol-mcp.jpg`

If an image file doesn't exist, 
- publish the article without image.
- Raise WARN message in log.

---



## Error Handling

### Network Errors
- **Timeout**: 60s
- **Retry**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Action**: Log ERROR, skip feed, continue

### GraphQL Errors
If GraphQL returns `errors`, treat as failed publish, log with details, skip.

## Logging
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

### Format: JSON (one object per line)
**File**: `{article-publisher.log}/article-publisher-{FEED_DATE}.log`

---

## Project Structure

```
.
├── article-publisher.py              # Main entry point
├── src/
│   └── article-publisher/            # Package
├── data/
│   └── tech-trend-article/            # Analysis results (input) folder
│          └── {FEED_DATE}/            # Only write to this directory
├── .env                                # API keys
├── config.yaml                         # Configuration file
```

---

## Code Quality Standards

- **Max function length**: 79 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants

---

## Environment Setup (.env file)

```bash
# Hashnode API Key
HASHNODE_API_KEY=...
```