# Production-Ready Implementation - Fixed Version

## 🚨 CRITICAL: File Structure Required

The code MUST be split into separate files. Here's the corrected structure:

```
tech-trend-analysis/
├── tech-trend-analysis.py
├── src/
│   ├── __init__.py                          # ← CREATE THIS
│   └── tech_trend_analysis/
│       ├── __init__.py                      # ← CREATE THIS
│       ├── main.py
│       ├── config.py
│       ├── models.py
│       ├── processor.py
│       ├── exceptions.py
│       ├── llm/
│       │   ├── __init__.py                  # ← CREATE THIS
│       │   ├── base.py
│       │   ├── factory.py
│       │   ├── openai_client.py
│       │   ├── deepseek_client.py
│       │   ├── claude_client.py
│       │   └── ollama_client.py
│       └── utils/
│           ├── __init__.py                  # ← CREATE THIS
│           ├── logger.py
│           └── file_ops.py
```

## 📝 Create Empty __init__.py Files

```bash
# Run these commands:
mkdir -p src/tech_trend_analysis/llm
mkdir -p src/tech_trend_analysis/utils

touch src/__init__.py
touch src/tech_trend_analysis/__init__.py
touch src/tech_trend_analysis/llm/__init__.py
touch src/tech_trend_analysis/utils/__init__.py
```

## 🔧 CRITICAL FIXES TO APPLY

### Fix #1: Enhanced LLM Response Parser (processor.py)

Replace the `_parse_llm_response` method with this robust version:

```python
import re
from typing import Dict, Any

def _parse_llm_response(
    self,
    response: str,
    category: str,
    analysis_date: str
) -> AnalysisReport:
    """
    Parse LLM response - extract JSON from anywhere in text.

    Args:
        response: Raw LLM response text
        category: Category name
        analysis_date: Analysis date string

    Returns:
        AnalysisReport instance

    Raises:
        ValidationError: If response cannot be parsed
    """
    try:
        # Strategy 1: Try direct JSON parse
        try:
            data = json.loads(response.strip())
        except json.JSONDecodeError:
            # Strategy 2: Extract JSON from markdown code blocks
            json_match = re.search(
                r'```(?:json)?\s*(\{.*?\})\s*```',
                response,
                re.DOTALL
            )
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                # Strategy 3: Find raw JSON object with "trends" key
                json_match = re.search(
                    r'\{[^}]*"trends"[^}]*:.*?\}',
                    response,
                    re.DOTALL
                )
                if json_match:
                    # Find the complete JSON object
                    start = json_match.start()
                    brace_count = 0
                    end = start
                    for i, char in enumerate(response[start:], start):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end = i + 1
                                break
                    data = json.loads(response[start:end])
                else:
                    raise ValidationError(
                        "No valid JSON found in LLM response. "
                        f"Response preview: {response[:200]}..."
                    )

        # Validate structure
        if 'trends' not in data:
            raise ValidationError(
                "Missing 'trends' key in LLM response"
            )

        # Parse and validate each trend
        trends = []
        for idx, t in enumerate(data['trends']):
            required_fields = [
                'topic', 'reason', 'score', 'links', 'search_keywords'
            ]
            missing = [f for f in required_fields if f not in t]
            if missing:
                self.logger.warning(
                    f"Trend {idx} missing fields {missing}, skipping"
                )
                continue

            try:
                trends.append(Trend(
                    topic=str(t['topic']),
                    reason=str(t['reason']),
                    score=int(t['score']),
                    links=list(t['links']),
                    search_keywords=list(t['search_keywords'])
                ))
            except (ValueError, TypeError) as e:
                self.logger.warning(
                    f"Invalid trend data at index {idx}: {e}"
                )
                continue

        if not trends:
            self.logger.warning(
                f"No valid trends found for {category}"
            )

        return AnalysisReport(
            analysis_date=analysis_date,
            category=category,
            trends=trends
        )

    except json.JSONDecodeError as e:
        raise ValidationError(
            f"Invalid JSON in LLM response: {e}\n"
            f"Response preview: {response[:200]}..."
        )
    except Exception as e:
        raise ValidationError(
            f"Failed to parse LLM response: {e}\n"
            f"Response preview: {response[:200]}..."
        )
```

### Fix #2: Create Empty Output on Failure (processor.py)

Replace the `process_category` method:

```python
def process_category(
    self,
    category_file: Path,
    feed_date: str,
    prompt_template: str
) -> bool:
    """
    Process a single category RSS feed.

    Args:
        category_file: Path to category JSON file
        feed_date: Feed date string (YYYY-MM-DD)
        prompt_template: LLM prompt template

    Returns:
        True if processing succeeded, False otherwise
    """
    category_name = None

    try:
        # Load and parse RSS feed
        feed_data = read_json_file(category_file)
        rss_feed = self._parse_rss_feed(feed_data)
        category_name = rss_feed.category

        # Check if output already exists (idempotency)
        output_path = self._get_output_path(rss_feed.category, feed_date)
        if output_path.exists():
            self.logger.info(
                f"Skipping {rss_feed.category}: "
                f"Output already exists at {output_path}"
            )
            return True

        # Generate prompt
        prompt = self._create_prompt(rss_feed, prompt_template)

        # Call LLM
        self.logger.info(
            f"Analyzing {rss_feed.category} "
            f"with {len(rss_feed.articles)} articles"
        )
        response = self.llm_client.generate(prompt)

        # Parse and save response
        report = self._parse_llm_response(
            response,
            rss_feed.category,
            feed_date
        )
        self._save_report(report, output_path)

        self.logger.info(
            f"Successfully processed {rss_feed.category}: "
            f"{len(report.trends)} trends identified"
        )
        return True

    except ValidationError as e:
        self.logger.error(
            f"Validation error processing {category_file}: {e}",
            exc_info=True
        )
        self._create_empty_output(category_name, category_file, feed_date)
        return False

    except LLMError as e:
        self.logger.error(
            f"LLM error processing {category_file}: {e}",
            exc_info=True
        )
        self._create_empty_output(category_name, category_file, feed_date)
        return False

    except Exception as e:
        self.logger.error(
            f"Unexpected error processing {category_file}: {e}",
            exc_info=True
        )
        self._create_empty_output(category_name, category_file, feed_date)
        return False


def _create_empty_output(
    self,
    category_name: str,
    category_file: Path,
    feed_date: str
) -> None:
    """
    Create empty output file when processing fails.

    Args:
        category_name: Category name (may be None if parsing failed)
        category_file: Original category file path
        feed_date: Feed date string
    """
    # Use category name from file if parsing failed
    if not category_name:
        category_name = category_file.stem

    output_path = self._get_output_path(category_name, feed_date)

    # Don't overwrite existing output
    if output_path.exists():
        return

    empty_report = AnalysisReport(
        analysis_date=feed_date,
        category=category_name,
        trends=[]
    )

    try:
        self._save_report(empty_report, output_path)
        self.logger.info(
            f"Created empty output for failed category: {category_name}"
        )
    except Exception as save_error:
        self.logger.error(
            f"Failed to create empty output for {category_name}: "
            f"{save_error}"
        )
```

### Fix #3: Validate Date Format (main.py)

```python
from datetime import datetime, date

def get_feed_date(args: argparse.Namespace) -> str:
    """
    Determine feed date from arguments or use today's date.

    Args:
        args: Parsed command line arguments

    Returns:
        Feed date string in YYYY-MM-DD format

    Raises:
        ValueError: If date format is invalid
    """
    if args.feed_date:
        # Validate date format
        try:
            datetime.strptime(args.feed_date, '%Y-%m-%d')
            return args.feed_date
        except ValueError:
            raise ValueError(
                f"Invalid date format: '{args.feed_date}'. "
                f"Expected format: YYYY-MM-DD (e.g., 2025-12-08)"
            )
    return date.today().strftime('%Y-%m-%d')
```

### Fix #4: Normalize Category Names (main.py)

```python
def normalize_category(name: str) -> str:
    """
    Normalize category name for comparison.

    Args:
        name: Category name to normalize

    Returns:
        Normalized category name (lowercase, underscores)

    Example:
        >>> normalize_category("Software Engineering")
        'software_engineering'
        >>> normalize_category("software-engineering")
        'software_engineering'
    """
    return name.lower().replace(' ', '_').replace('-', '_')


def get_category_files(
    config: Config,
    feed_date: str,
    category_filter: str = None
) -> list:
    """
    Get list of category files to process.

    Args:
        config: Application configuration
        feed_date: Feed date string
        category_filter: Optional category name filter

    Returns:
        List of category file paths
    """
    rss_dir = Path(config.rss_feed_path) / feed_date

    if not rss_dir.exists():
        return []

    all_files = list_json_files(rss_dir)

    if category_filter:
        # Normalize and filter for specific category
        normalized_filter = normalize_category(category_filter)
        filtered = [
            f for f in all_files
            if normalize_category(f.stem) == normalized_filter
        ]
        return filtered

    return all_files
```

### Fix #5: Validate Config Values (config.py)

```python
@property
def llm_timeout(self) -> int:
    """
    Get LLM request timeout in seconds.

    Returns:
        Timeout value in seconds

    Raises:
        ConfigurationError: If timeout is invalid
    """
    timeout = self._config.get('llm', {}).get('timeout', 60)
    if not isinstance(timeout, int) or timeout <= 0:
        raise ConfigurationError(
            f"Invalid timeout value: {timeout}. "
            f"Must be a positive integer"
        )
    if timeout > 300:  # 5 minutes max
        self.logger.warning(
            f"Very large timeout configured: {timeout}s"
        )
    return timeout


@property
def llm_retry(self) -> int:
    """
    Get number of retry attempts for LLM requests.

    Returns:
        Number of retry attempts

    Raises:
        ConfigurationError: If retry count is invalid
    """
    retry = self._config.get('llm', {}).get('retry', 3)
    if not isinstance(retry, int) or retry < 0:
        raise ConfigurationError(
            f"Invalid retry value: {retry}. "
            f"Must be a non-negative integer"
        )
    if retry > 10:
        self.logger.warning(
            f"Very high retry count configured: {retry}"
        )
    return retry
```

### Fix #6: Validate Prompt Template (processor.py)

```python
def _create_prompt(
    self,
    rss_feed: RSSFeed,
    template: str
) -> str:
    """
    Create LLM prompt from RSS feed and template.

    Args:
        rss_feed: RSS feed data
        template: Prompt template

    Returns:
        Formatted prompt string

    Raises:
        ValidationError: If template is missing required placeholders
    """
    # Validate required placeholders exist
    required_placeholders = [
        '{category}',
        '{articles}',
        '{article_count}',
        '{fetch_date}'
    ]
    missing = [p for p in required_placeholders if p not in template]
    if missing:
        raise ValidationError(
            f"Prompt template missing required placeholders: {missing}. "
            f"Required: {required_placeholders}"
        )

    articles_text = "\n\n".join(
        f"Title: {art.title}\nLink: {art.link}"
        for art in rss_feed.articles
    )

    prompt = template.replace("{category}", rss_feed.category)
    prompt = prompt.replace("{articles}", articles_text)
    prompt = prompt.replace(
        "{article_count}",
        str(rss_feed.article_count)
    )
    prompt = prompt.replace("{fetch_date}", rss_feed.fetch_date)

    return prompt
```

## 🧪 Testing Before Production

### 1. Create Test Structure

```bash
# Create test RSS feed
mkdir -p data/rss/rss-feed/2025-12-08

cat > data/rss/rss-feed/2025-12-08/test_category.json << 'EOF'
{
  "category": "test_category",
  "fetch_date": "2025-12-08",
  "article_count": 2,
  "articles": [
    {
      "title": "Test Article 1",
      "link": "https://example.com/1"
    },
    {
      "title": "Test Article 2",
      "link": "https://example.com/2"
    }
  ]
}
EOF
```

### 2. Run Tests

```bash
# Test 1: Normal execution
python tech-trend-analysis.py

# Test 2: Specific category
python tech-trend-analysis.py --category test_category

# Test 3: Invalid date (should error)
python tech-trend-analysis.py --feed_date "invalid-date"

# Test 4: Idempotency (run twice)
python tech-trend-analysis.py
python tech-trend-analysis.py  # Should skip

# Test 5: Category name normalization
python tech-trend-analysis.py --category "Test Category"
```

### 3. Verify Outputs

```bash
# Check output exists
ls -la data/tech-trend-analysis/2025-12-08/

# Check log file
cat log/tech-trend-analysis/tech-trend-analysis-2025-12-08.log | jq .

# Verify JSON structure
cat data/tech-trend-analysis/2025-12-08/test_category.json | jq .
```

## ✅ Pre-Production Checklist

- [ ] All `__init__.py` files created
- [ ] Code split into separate files
- [ ] All critical fixes applied
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with API keys
- [ ] `config.yaml` created and validated
- [ ] Prompt template created
- [ ] Test RSS feed created
- [ ] Test run successful
- [ ] Idempotency verified
- [ ] Empty output creation tested
- [ ] Error handling tested
- [ ] Log files readable and complete

## 🚀 Deployment Steps

1. **Split the monolithic artifact into separate files**
2. **Apply all critical fixes above**
3. **Run full test suite**
4. **Monitor first production run**
5. **Check logs for any warnings/errors**
6. **Verify output quality**

Your code will be production-ready after these fixes!