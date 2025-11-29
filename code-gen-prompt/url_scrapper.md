# Python Module Generation Prompt: Tech Trend Analysis with LLM

You are an expert Python developer specializing in clean architecture, production-grade code, and LLM integration. Generate a complete, well-structured Python module with the following specifications:

---

## Module Overview

**Name**: URL Content Scrapper 
**Purpose**: Retreive content of given URLs and remove characters that are not relevant the content, such as HTML tag, reference indicator, and image link. The module should be production-ready with comprehensive error handling, retry logic, and logging.

---

## Core Requirements

### 1. Clean Content
- Remove unrelavant characters from the scrapped content to the content clean and clear. Use available python package instead of create list of unrelavant characters by yourself.
- Configure **timeout** for all API calls (default: 60 seconds)

### 2. Configuration Management
All settings must be loaded from `config.yaml`:

```yaml
tech-trend-analysis:
  prompt: prompt/tech-trend-analysis-prompt.md
  analysis-report: data/tech-trend-analysis/report #Base source folder
llm:
  server: openai
  llm-model: gpt-5.1
  timeout: 60
scrap:
  url-scrapped-content: data/scrapped-content # Base output folder
  timeout: 60
```

### 3. Tech Trend Analysis File Structure
```
{tech_trend_anaysis_base_path}/{YYYY-MM-DD}/{category}.json
```

**File Path Example**: 
If the execution date is `2025-11-21` and a catagory is `Software Engineering / Dev`, a source file is below.
`data/tech-trend-analysis/report/2025-11-21/software-engineering-dev.json`

**File Example**
```
{
  "analysis_timestamp": "2025-11-22T08:03:00.627012",
  "source_file": "ai-machine-learning.json",
  "category": "AI / Machine Learning",
  "trends": [
    {
      "topic": "MIT Technology Review’s ‘New Age of Conspiracies’ Roundtable and Digital Resilience in the Agentic AI Era",
      "reason": "Multiple pieces converge on how societies and systems should cope with a surge of conspiracy ...",
      "category": "AI/ML",
      "links": [
        "https://www.technologyreview.com/2025/11/20/1127749/roundtables-surviving-the-new-age-of-conspiracies/",
        "https://www.technologyreview.com/2025/11/20/1127941/designing-digital-resilience-in-the-agentic-ai-era/",
        "https://www.technologyreview.com/2025/11/20/1128183/the-download-whats-next-for-electricity-and-living-in-the-conspiracy-age/"
      ],
      "search_keywords": [
        "MIT Roundtables new age of conspiracies"
      ]
    }
  ]
}
```


### 4. Response File Structure
Save analysis results with this path format:
```
{url_scrapped_content_base_path}/{YYYY-MM-DD}/{category}/url-scrap.json
```

**File Path Example**:
If the execution date is `2025-11-21` and a catagory is `Software Engineering / Dev`, a source file is below.
`data/scrapped-content/2025-11-21/software-engineering-dev/url-scrap.json`

### 5. Processing Logic
- Read ***Today's*** tech trend analysis file.
- Take URLs from links field the tech trend analysis file.
- Process **one category at a time** sequentially
- Accumulate scrap contents in one file even content scrapped from multiple URLs.
- **Continue processing** remaining feeds even if one fails (error isolation)
- Generate detailed summary report at completion

### 6. Expected Output Format

```json
{
  "analysis_timestamp": "2025-11-18T16:49:13.130964",
  "source_file": "software-engineering-dev.json",
  "category": "Software Engineering / Dev",
  "trends": [
    {
      "topic": "Guts – Convert Golang Types to TypeScript",
      "link": "https://github.com/coder/guts",
      "content": "Newly released tool addressing common pain point...",
    }
  ]
}
```

---

## Project Structure

```
.
├── url_scrapper.py              # Main entry point
├── src/
│   └── url_scrapper /            # Package
├── data/
├── .env                                # API keys (gitignored)
├── config.yaml                         # Configuration file
```

---

## Technical Requirements

### Code Quality Standards
1. **Clean Architecture**: Separation of concerns (config, clients, business logic)
2. **SOLID Principles**: Single responsibility, dependency injection, abstractions
3. **Type Hints**: Comprehensive type annotations throughout
4. **Docstrings**: Every class, method, and function documented
5. **Error Handling**: Try-catch blocks with specific exception handling
6. **Logging**: Structured logging using Python's `logging` module
7. **DRY Principle**: No code duplication

### Production-Grade Features
1. **Retry Logic**: Exponential backoff for all LLM API calls
2. **Timeout Handling**: Configurable timeouts to prevent hanging
3. **Graceful Degradation**: Continue processing if one feed fails
4. **Comprehensive Logging**: INFO level for progress, ERROR for failures
5. **API Key Management**: Load from `.env` file with validation
6. **JSON Parsing Safety**: Handle malformed LLM responses gracefully
7. **Directory Auto-Creation**: Create output directories as needed

### Error Handling Requirements
- Handle JSON parsing errors in feed files
- Handle JSON parsing errors in LLM responses
- Handle network failures and timeouts
- Log all errors with context (filename, operation, error details)
- Generate error summary in final report

---

## Expected Behavior

When running `url_scrapper.py`:

1. Load configuration from `config.yaml`
2. Discover today's `.json` feed files in tech trend analysis directory
5. Process each link in an analysis file sequentially:
   - Access link
   - Extract content from the link
   - Clean content
   - Save to structured path
6. Generate final summary:
   - Total files processed
   - Total trends found
   - Errors encountered (if any)
   - Output directory path

---