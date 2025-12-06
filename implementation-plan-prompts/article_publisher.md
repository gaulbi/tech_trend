# Article Publisher

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Task**: Generate a complete, runnable Python module that satisfies all requirements below.

---

## Module Overview

**Purpose**: Publish **today’s technology articles** (Markdown files) to Hashnode using the v2 GraphQL API.

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
```

**Validation**:
- Missing `config.yaml` → Raise `ConfigurationError` and exit.
- Missing `article-publisher.publication-id` → Raise `ConfigurationError`.

---

## Input Data
**Path**: `{article-generator.tech-trend-article}/{TODAY_DATE}/{category}/*.md `

### TODAY_DATE:
Automatically determined using `datetime.date.today().strftime('%Y-%m-%d')`

### Markdown Parsing Requirements
Inside each markdown file:
- **Title Format**: `# [EN] Title: Your English Title Here`
- **Extraction Logic**:
  - Find the first H1 line starting with `# [EN] Title:`
  - Extract everything after `[EN] Title:` and trim whitespace
  - If no matching H1 found → Log WARNING and skip file
- **Content**: The entire Markdown file content (including title line) becomes `contentMarkdown`

### Processing Rules
- Process articles one by one (order not important).
- Skip empty files.
- Log all skip events.

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
- `title`: Extracted title string
- `contentMarkdown`: Full Markdown content
- `publicationId`: Loaded from `article-publisher.publication-id`
- `tags`: Optional → default to empty list `[]`

### HTTP Requirements:
- Method: POST with JSON body
- Header name: Value from `article-publisher.api-header`
- Header value: From environment variable `HASHNODE_API_KEY`
- Timeout: From `article-publisher.timeout` (seconds)

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

### Format: JSON (one object per line)
**File**: `{article-publisher.log}/article-publisher-{TODAY_DATE}.log`

---

## Project Structure

```
.
├── article-publisher.py              # Main entry point
├── src/
│   └── article-publisher/            # Package
├── data/
│   └── tech-trend-article/            # Analysis results (input) folder
│          └── {TODAY_DATE}/            # Only write to this directory
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