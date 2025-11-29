# Python Module Generation Prompt
You are an expert Python developer specializing in clean architecture and production-grade code. Generate a complete, well-structured Python module with the following specifications:

---

## Module Overview
- Module Name: RSS Fetcher
- Purpose: Create a Python module that fetches RSS feeds from multiple sources, organizes them by category, and saves them as structured JSON files.

--

## Functional Requirements

1. **Configuration**
   - Read configuration from a `config.yaml` file
   - Config should specify:
     - `rss.rss-list`: Path to RSS sources file
     - `rss.rss-feed`: Base directory for output files

2. **RSS Sources**
   - Load RSS feed URLs from a JSON file (path specified in config)
   - Sources are grouped by categories
   - Multiple sources can exist per category
   - Example structure:
   ```json
   {
     "AI / Machine Learning": {
       "TechCrunch AI": "https://techcrunch.com/category/ai/feed/",
       "MIT News AI": "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml"
     },
     "Software Engineering / Dev": {
       "Hacker News": "https://hnrss.org/frontpage"
     }
   }
   ```

3. **Fetch and Process**
   - Fetch RSS feeds from all sources in all categories
   - Extract relevant information from each article
   - Handle errors gracefully (network issues, malformed feeds, etc.)

4. **Output Format**
   - Save one JSON file per category
   - File path: `{rss-feed}/{YYYY-MM-DD}/{category-filename}.json`
     - Example: `../data/rss/rss-feed/2025-11-11/ai-machine-learning.json`
   - Category names should be converted to safe filenames (lowercase, no special chars)
   - Output format must match this structure exactly:
   ```json
   {
     "category": "Software Engineering / Dev",
     "fetch_timestamp": "2025-11-18T14:01:53.652441",
     "article_count": 2,
     "articles": [
       {
         "title": "NPR to get $36M in settlement to operate US public radio system",
         "link": "https://apnews.com/article/trump-npr-lawsuit-2cc4abfa8cf00fe6f89e387e63eb4a2a",
         "published": "Tue, 18 Nov 2025 18:19:10 +0000",
         "source": "Hacker News Front Page"
       },
       {
         "title": "Show HN: Guts – convert Golang types to TypeScript",
         "link": "https://github.com/coder/guts",
         "published": "Tue, 18 Nov 2025 17:55:55 +0000",
         "source": "Hacker News Front Page"
       }
     ]
   }
   ```

5. **Execution**
   - Provide a runnable entry point using module name (e.g., `rss-fetch.py` or similar)
   - Process all categories automatically
   - Show progress and summary statistics

## Technical Requirements

- Use appropriate Python libraries for RSS parsing and YAML handling
- Follow Python best practices (type hints, error handling, clean code)
- Design with modularity and maintainability in mind
- Create directories automatically as needed
- Provide clear console output for user feedback
- Create a module under src

## Deliverables

- Complete, working Python code with proper structure
- Dependencies list (requirements.txt)
- Example configuration file
- Brief usage instructions

## IMPORTANT
1. Design the architecture and file structure as you see fit to best meet these requirements.