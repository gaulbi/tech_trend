# Semantic Deduplicator

## Role Definition
**Role**: You are an expert Python developer specializing in clean architecture, production-grade code, and vector search strategies. Tasks: Generate a complete Python module implementation based on this plan.

---

## Module Overview
**Purpose**: Filter incoming tech trend keywords by comparing them against a historical vector database (ChromaDb) to prevent generating duplicate articles. The module must implement a "Semantic Check" to identify if a similar topic was covered within a specific timeframe, and a "Record" function to save new trends to history, and a **post-processing file rotation** to archive original reports and replace them with filtered versions.

### Feed Date
- If `--feed_date` argument is not specified in command, use today's date as the reference date.
- In this case, determine today's date using `datetime.date.today().strftime('%Y-%m-%d')`

---

## Configuration
### File: ./config.yaml
```yaml
deduplication:
  history-keywords: data/history_keywords  # distinct from content db
  collection-name: history_keywords
  dedup-analysis-report: data/dedup-tech-trend-analysis  # Base output folder
  similarity-threshold: 0.85                  # Cosine similarity cutoff
  lookback-days: 7                            # Only check against articles from last N days
  target-count: 1                             # Number of unique trends to return
  log: log/deduplication
  embedding-provider: openai                  # openai, voyageai, gemini, sentence-transformers
  embedding-model: text-embedding-3-small
  timeout: 60
  max-retries: 3

tech-trend-analysis:
  analysis-report: data/tech-trend-analysis # Base input folder
  org-analysis-report: data/org-tech-trend-analysis
```

**Validation**: Missing config.yaml → Raise ConfigurationError and exit

---

## Input
### File Path
`{tech-trend-analysis.analysis-report}/{FEED_DATE}/{category}.json`

### Example
If feed_date is 2025-11-21 and a category is software_engineering, output file is 
`data/tech-trend-analysis/2025-11-21/software_engineering.json`

## JSON Structure
```json
{
  "feed_date": "2025-11-22",
  "category": "software_engineering",
  "trends": [
    {
      "topic": "...",
      "reason": "...",
      "score": 10,
      "links": ["..."],
      "search_keywords": ["..."]
    }
  ]
}
```

**Validation**: Invalid JSON → Raise `ValidationError` and continue processing remaining categories.

---

## Output
### 1. Vector Database (History)
- Library: chromadb
- Persistence Path: `{deduplication.history-keywords}`
- **Action**: Store only the trends that successfully pass the filter and are selected for generation.

**Database Schema (ChromaDB Metadata & ID)**
- ID Format: `{date}|{category}|{topic_md5}` (Use deterministic MD5 hash of the topic string))
- Document: `Topic: {topic}. Keywords: {search_keywords joined by comma}`
- Metadata:
     - `topic`: The trend title
     - `date`: {FEED_DATE} (ISO format)
     - `keywords`: Original keywords string
     - `category`: Category

### 2. Filtered List (JSON)
#### File Path
`{deduplication.dedup-analysis-report}/{FEED_DATE}/{category}.json`

#### Example
If feed_date is 2025-11-21 and a category is software_engineering, output file is 
`data/dedup-tech-trend-analysis/2025-11-21/software_engineering.json`

### JSON Structure
- Same as input file (tech trend analysis JSON file)
- **Content**: The top `{deduplication.target-count}` trends that were determined to be unique.

### 3. File Cleanup & Rotation
- **Action**: After database insertion and filtered JSON creation:
  1. Copy the **original** tech trend analysis file to {tech-trend-analysis.org-analysis-report}/{FEED_DATE}/{category}.json
  2. Delete the **input file** from {tech-trend-analysis.analysis-report}/{FEED_DATE}/{category}.json
  3. Copy the **filtered** tech trend analysis file from {deduplication.dedup-analysis-report}/{FEED_DATE}/{category}.json to {tech-trend-analysis.analysis-report}/{FEED_DATE}/{category}.json
---

## Multi-Embedding Model Provider Support
- Support multiple Embedding model providers: **OpenAI**, **Voyage AI**, **Gemini**, and **Sentence Transformers** (local)
- Use a **Factory Pattern** to create appropriate embedding clients
- All embedding clients must inherit from an **Abstract Base Class**
- Implement **exponential backoff retry logic** (3 retries: 1s, 3s, 5s delays)
- Configure **timeout** for all API calls (default: 60 seconds)
- Load API keys from `.env` file

---

## Logging
```json
{
  "timestamp": "ISO format",
  "level": "INFO",
  "module": "deduplicator",
  "function": "check_uniqueness", 
  "line": 42,
  "message": "Duplicate found: 'New AI Agent' matches 'AI Agents' (Score: 0.89)",,
  "traceback": "full traceback for errors"
}
```
1. Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
2. Console output with colors for different levels
3. JSON formatting option for structured logging
4. Function decorator to auto-log calls with timing
5. Error logging helper that captures stack traces
6. Configurable via environment variables or config file

### Levels
- **INFO**: Start process, Final selection count, Record updates
- **DEBUG**: Similarity scores for rejected keywords
- **ERROR**: API failures, Database locks

### Rotation
Daily rotation, keep 30 days

---

## Project Structure
```
.
├── deduplicator.py          # Main entry point
├── src/
│   └── deduplicator/        # Package
├── data/
│   └── history_keywords/   # ChromaDB history
│   └── processing/          # Output folder for selected trends
├── config.yaml              # Configuration file
```

- DO NOT implement any logic in `deduplicator.py`. It's only for entry point.

### Entry Point
```bash

# Standard run (reads {category}.json, outputs {category}.json, updates DB)
python deduplicator.py 

# Run for specific date 
python deduplicator.py --feed_date "2025-02-01"

python deduplicator.py --category "software_engineering"

python deduplicator.py --feed_date "2025-02-01" --category "software_engineering"
```

**category** and **feed_date** are optional input parameters.

---

## Code Quality Standards
- **Max function length**: 50 lines
- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Line length**: Max 100 characters
- **No hardcoded values**: Use config or constants

---

## Idempotency

**Before runing job in each category**: Check if file exists at `{deduplication.dedup-analysis-report}/{FEED_DATE}/{category}.json`
- **If exists**: Log INFO, print "Skipping...", don't process deduplication logic for the category.
- **If not exists**: Process deduplication logic

---

## Success Criteria
**- Deduplication Logic**
  1. Iterate through trend sorted by impact.
  2. Embed `Topic: {topic}. Keywords: {keywords}`.
  3. Query History Keyword DB with filter: `date > (today - {deduplication.lookback-days})`.
  4. **Similarity Check**:
    - If `similarity_score > {deduplication.similarity-threshold}`: Log as **Duplicate** (Skip).
    - Else: Add to selection list.
  5. Stop when `target-count` is reached.

- **Persistence**: Save the selected trends into the History DB **only** if they are new and written to the JSON output.

**- Persistence & Rotation**:
  1. Save the selected trends into the History DB.
  2. Write the filtered JSON output.
  3. Copy the original input file to `{tech-trend-analysis.org-analysis-report}`.
  4. Delete the input file from `{tech-trend-analysis.analysis-report}`.
  5. Copy the filtered file from `{deduplication.dedup-analysis-report}` to `{tech-trend-analysis.analysis-report}`.
---

## Implementation Notes
### DO NOT GENERATE
- config.yaml (provided at runtime)
- Test files

### Environment Setup (.env file)
```bash

# OpenAI API Key
OPENAI_API_KEY=sk-...

# Voyage AI
VOYAGEAI_API_KEY=...

# Gemini API Key
GEMINI_API_KEY=...
```