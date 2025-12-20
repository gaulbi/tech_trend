# Article Publisher

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture and production-grade code.
**Task**: Generate a complete, runnable Python module that satisfies all requirements below.

---

## Module Overview

**Purpose**: Publish **today’s technology articles** (Markdown files) to Hashnode using the v2 GraphQL API.
The module must be production-ready with comprehensive error handling, retry logic, and logging.

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
  published-article: data/published-tech-trend-article # base output folder
article-generator:
  tech-trend-article: data/tech-trend-article       # base input folder
image-generator:
  url-mapping-path: data/image-url-mapping 
```

**Validation**: Missing config.yaml → Raise `ConfigurationError` and exit.

---


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

## Process

### Process Steps
1. Load an article file. **Load Tech Trend Article**
2. Extrace a title in the article file. **Article Title**
3. Load an image URL mapping file and take `imgbb_url`. **Load Image URL Mapping**
4. Inject extra information in the loaded article. **Extra Information In Article**
5. Upload the article to Hashnode. **Upload Article to Hashnode**
6. Record the status of article publish. **Status Article Publish**

### Process Rules
- Iterate through **Process Steps** in each `category` in the given `feed_date`.
- If multiple md files are found, iterate though **Process Steps** in each file.

### Idempotency

**Before fetching each category**: Check if file exists at `{article-publisher.published-article}/{FEED_DATE}/{category}/{article_file_name}.json`
- **If exists**: Log INFO, print "Skipping publishing `{article_file_name}.md`", don't publish

---

## Load Tech Trend Article

### Path
`{article-generator.tech-trend-article}/{FEED_DATE}/{category}/*.md `

### Example
If a feed date is 2025-11-25 and a category is software_engineering, the article pathes can be,
`data/tech-trend-article/2025-11-26/software_engineering/article_1.md`
`data/tech-trend-article/2025-11-26/software_engineering/article_2.md`

---

## Article Title
The value of `title` in Hashnode input payload is one line between `## Title` and `**Date/Time**:` in the article


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

**Date/Time**: 2025-12-11 15:30:20
```

---

## Load Image URL Mapping
### Path
`{image-generator.url-mapping-path}/{FEED_DATE}/{category}/{article_file_name}.json`

### Example
If a feed date is 2025-11-25, a category is software_engineering and a file name is article_1.md, the mapping file path is `data/image-url-mapping/2025-11-25/software_engineering/article_1.json`

### Format
```json
{
  "article_file": "retrieval-augmented-generation.md",
  "category": "software_engineering",
  "feed_date": "2025-12-20",
  "local_path": "data/image/2025-12-20/software_engineering/retrieval-augmented-generation.jpg",
  "imgbb_url": "https://i.ibb.co/1f5Fggns/retrieval-augmented-generation.png",
  "uploaded_at": "2025-12-20T16:29:11.271588",
  "status": "success"
}
```

---

## Extra Information In Article
### Published Date/Time
1. Determine current date/time using `datetime.date.today().strftime('"%Y-%m-%d %H:%M:%S"')`
2. Replace `{YYYY-MM-DD HH:mm:ss}` to currrent date/time.

**Important**:  
- Published Date/Time is different from `feed_date`.
- when the feed date is _2025-12-10_, the published date/time can be _2025-12-10 15:30:25_.

### Insert Image URL
1. Find `imgbb_url` in the loaded **Image URL Mapping** file
2. Find string "image_url_tag_here" in the loaded article file.
3. Replace the string "image_url_tag_here" to _Alt Text_ syntax using following format.
![Alt Text](`{imgbb_url}`)

**Example**
- If `imgbb_url` is https://example.com/image.jpg, and the loaded article is 
```md
## Title 
Article Title about Tech

**Date/Time**: 2025-12-10 15:30:13

image_url_tag_here

## Summary  
```

After URL is injected
```md
## Title 
Article Title about Tech

**Date/Time**: 2025-12-10 15:30:13

![Alt Text](https://example.com/image.jpg)

## Summary  
```

---

## Upload Article to Hashnode

Upload the modified, loaded article to Hashnode using GraphQL

### Hashnode Publishing (GraphQL v2)
Use the `PublishPost` mutation:
```graphql
  mutation PublishPost($input: PublishPostInput!) {
    publishPost(input: $input) {
      post { 
        id 
        slug 
        title
      }
    }
  }
```

---

## Status Article Publish
Create a json file after the article publish is completed.

### Output File Path
`{article-publisher.published-article}/{FEED_DATE}/{category}/{article_file_name}.json`

**File Path Example**
If a feed_date is 2025-12-10, a category is software_engineering, and a article_file_name is retrieval-augmented-generation.md, path is `data/published-tech-trend-article/2025-12-10/software_engineering/retrieval-augmented-generation.json`

### Output Payload
```json
{
  "feed_date": "",
  "title": "",
  "published_datetime": "",
  "category": "",
  "article_url": "",
  "status": "" 
}
```

`status` can be _Success_ or _Fail_. 

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

### Entry Point
```bash
python article-publisher.py

python article-publisher.py --category "software_engineering"

python article-publisher.py --feed_date "2025-02-01"

python article-publisher.py --category "software_engineering" --feed_date "2025-02-01" --file_name "model-context-protocol.md"
```
- **category**, **feed_date** and **file_name** are optional input parameters.
- **category** and **feed_date** are required to use **file_name**.
- If the optional parameters are presented, ignore **Idempotency** rule.

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