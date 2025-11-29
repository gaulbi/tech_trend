# Python Module Generation Prompt
You are a seasoned Python developer specializing in clean architecture and maintainable code.

## Module Name
Tech Trend Analysis

## Module Goal
Create a well structured Python module that find out techonologies using LLM. To make LLM to identify technology trend, send fetched feed files and prompt stored in a file. When LLM respond stores in a file for the next process.

## Instructions:
1. LLM Server: Make the code flexible to swtich LLM server running in local machine (Ollama) or major LLM service (OpenAI, Deepseek, Cloude). To achieve this, use ./config.yaml to get LLM Server.
2. LLM model: Write code to use ./config.yaml to get LLM module.
3. Feed File Path: write code to use ./config.yaml to get feed file paths.
4. Prompt: Write code to use ./config.yaml to get prompt file.
5. Response: Write code to use ./config.yaml to get a path to store response. Response file path format is ${search-trend.trend}/$category/%y-%m-%d/
6. Feed list folder can have muliple files, and each file represents a category. Write code to prcess one category at a time.

## Response Format
{
  "analysis_timestamp": "2025-11-18T16:49:13.130964",
  "source_file": "software-engineering-dev.json",
  "category": "Software Engineering / Dev",
  "article_count": 98,
  "trends_found": 3,
  "trends": [
    {
      "topic": "Guts – Convert Golang Types to TypeScript",
      "reason": "Guts is a newly released open-source tool that automates conversion of Golang types into TypeScript interfaces, addressing a common pain point in full-stack development by ensuring type safety and consistency between backend and frontend codebases. Its appearance on Hacker News with notable community engagement highlights its immediate relevance for developers working with Go and TypeScript integration.",
      "links": [
        "https://github.com/coder/guts",
        "https://news.ycombinator.com/item?id=45969708"
      ],
      "search_keywords": [
        "Guts Golang TypeScript"
      ]
    }
  ]
}

## .config.yaml 
rss:
  rss-list: data/rss/rss-list.json
  rss-feed: data/rss/rss-feed
search-trend:
  prompt: prompt/search-trend-prompt.md
  trend: data/trend
llm:
  server: openai
  llm-module: gpt-4.1


## Project Structure

```
.
├── tech-trend-analysis.py              # Main entry point
├── src/
│   └── tech-trend-analysis/  # package
├── data/
└── config.yaml          

## Important:
1. Do not write prompt by yourself. Use prompt stored in a file.