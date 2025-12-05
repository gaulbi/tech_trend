# Tech Trend Analysis - Setup Instructions

## 🔧 Critical Fixes Applied

The following critical errors have been fixed:

1. ✅ **Module Import Error**: Added proper error handling and path resolution
2. ✅ **Missing Dependencies**: Added early detection with helpful error messages
3. ✅ **Path Assumptions**: Changed to use script-relative paths instead of CWD
4. ✅ **JSON Extraction Bug**: Fixed code block parsing logic
5. ✅ **Prompt Template Validation**: Added validation for {articles} placeholder
6. ✅ **Empty Articles Handling**: Skip analysis instead of creating empty files
7. ✅ **Better Error Messages**: All LLM errors now include installation instructions

---

## 📁 Manual Setup (Required)

Since the code is provided as a combined artifact, you need to split it into separate files:

### Step 1: Create Directory Structure

```bash
mkdir -p src/tech_trend_analysis
mkdir -p data/rss/rss-feed
mkdir -p data/tech-trend-analysis
mkdir -p prompt
mkdir -p log
```

### Step 2: Extract Module Files

From the artifact "Complete Tech Trend Analysis Package", create these files:

```
src/tech_trend_analysis/__init__.py
src/tech_trend_analysis/exceptions.py
src/tech_trend_analysis/logger.py
src/tech_trend_analysis/config.py
src/tech_trend_analysis/models.py
src/tech_trend_analysis/llm_client.py
src/tech_trend_analysis/processor.py
src/tech_trend_analysis/main.py
```

**Each file starts with a header like:**
```python
# ============================================================================
# FILE: src/tech_trend_analysis/exceptions.py
# ============================================================================
```

Copy the code between headers into the corresponding file.

### Step 3: Create Configuration Files

#### `config.yaml`
```yaml
rss:
  rss-feed: data/rss/rss-feed

tech-trend-analysis:
  prompt: prompt/tech-trend-analysis-prompt.md
  analysis-report: data/tech-trend-analysis
  log: log/tech-trend-analysis

llm:
  server: openai  # Options: openai, deepseek, claude, ollama
  llm-model: gpt-4
  timeout: 60
  retry: 3
```

#### `.env`
```bash
# Choose the provider you're using and add the appropriate key

# OpenAI
OPENAI_API_KEY=sk-your-actual-key-here

# DeepSeek
DEEPSEEK_API_KEY=sk-your-actual-key-here

# Claude
CLAUDE_API_KEY=sk-ant-your-actual-key-here

# Ollama (no key needed, runs locally)
```

#### `prompt/tech-trend-analysis-prompt.md`
```markdown
Analyze the following technology articles and identify key trends.

Articles:
{{context}}

Provide your analysis in JSON format:
{
  "trends": [
    {
      "topic": "Brief trend topic",
      "reason": "Why this is trending",
      "links": ["relevant article URLs"],
      "search_keywords": ["keywords for further research"]
    }
  ]
}
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Create Sample RSS Feed Data

Create a file: `data/rss/rss-feed/2024-12-04/software_engineering.json`

```json
{
  "category": "software_engineering",
  "fetch_date": "2024-12-04",
  "article_count": 2,
  "articles": [
    {
      "title": "The Rise of Rust in System Programming",
      "link": "https://example.com/rust-systems"
    },
    {
      "title": "WebAssembly: The Future of Web Development",
      "link": "https://example.com/wasm-future"
    }
  ]
}
```

---

## 🚀 Running the Application

```bash
python tech-trend-analysis.py
```

---

## 🔍 Verification Tests

### Test 1: Module Import
```bash
python -c "from tech_trend_analysis.main import main; print('✓ Import successful')"
```

### Test 2: Configuration Loading
```bash
python -c "from tech_trend_analysis.config import Config; from pathlib import Path; c = Config(Path('config.yaml')); print('✓ Config loaded')"
```

### Test 3: Dependencies
```bash
python -c "import yaml, dotenv; print('✓ Core dependencies installed')"
```

### Test 4: LLM Client (OpenAI example)
```bash
python -c "from tech_trend_analysis.llm_client import OpenAIClient; print('✓ LLM client can be imported')"
```

---

## 🐛 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'tech_trend_analysis'"

**Solution**: 
- Ensure `src/tech_trend_analysis/` directory exists
- Ensure all `.py` files are in that directory
- Run from project root (where `tech-trend-analysis.py` is)

### Issue: "ModuleNotFoundError: No module named 'yaml'"

**Solution**: 
```bash
pip install pyyaml
```

### Issue: "ConfigurationError: Configuration file not found"

**Solution**: 
- Create `config.yaml` in project root
- Ensure you're running from the correct directory

### Issue: "OPENAI_API_KEY not found in environment"

**Solution**: 
- Create `.env` file in project root
- Add your API key: `OPENAI_API_KEY=sk-...`

### Issue: "No category files found for today"

**Solution**: 
- Create directory: `data/rss/rss-feed/YYYY-MM-DD/` (today's date)
- Add at least one `.json` file with RSS feed data

---

## 📊 Project Structure After Setup

```
tech-trend-analysis/
├── tech-trend-analysis.py          # Entry point
├── setup_project.py                 # Helper setup script
├── config.yaml                      # Configuration
├── .env                             # API keys (gitignored)
├── requirements.txt                 # Dependencies
├── SETUP_INSTRUCTIONS.md           # This file
│
├── src/
│   └── tech_trend_analysis/
│       ├── __init__.py
│       ├── main.py
│       ├── processor.py
│       ├── config.py
│       ├── logger.py
│       ├── llm_client.py
│       ├── models.py
│       └── exceptions.py
│
├── data/
│   ├── rss/
│   │   └── rss-feed/
│   │       └── 2024-12-04/         # Today's date
│   │           ├── software_engineering.json
│   │           └── ai_ml.json
│   └── tech-trend-analysis/
│       └── 2024-12-04/              # Output directory
│           ├── software_engineering.json
│           └── ai_ml.json
│
├── prompt/
│   └── tech-trend-analysis-prompt.md
│
└── log/
    └── tech-trend-analysis/
        └── tech-trend-analysis-2024-12-04.log
```

---

## ✅ Success Indicators

When properly set up, you should see:

```
======================================================================
Starting Tech Trend Analysis for 2024-12-04
======================================================================
2024-12-04 10:30:15 - INFO - Found 2 categories to process
2024-12-04 10:30:15 - INFO - Processing category: software_engineering
2024-12-04 10:30:18 - INFO - Successfully analyzed software_engineering: 3 trends identified
======================================================================
Processing Summary:
  Date: 2024-12-04
  Total categories: 2
  Successful: 2
  Failed: 0
  Skipped: 0
======================================================================
```

---

## 🔄 Idempotency Test

Run the script twice:

```bash
python tech-trend-analysis.py
python tech-trend-analysis.py  # Second run
```

Second run should show:
```
Skipping software_engineering: Analysis already exists
```

---

## 📝 Notes

- The application only processes today's date
- Historical data is ignored
- API keys must be in `.env` file (not in code)
- Log files are rotated at 10MB with 5 backups
- All output is in JSON format for easy parsing