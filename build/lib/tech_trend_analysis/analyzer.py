"""
Trend Analyzer Module

Orchestrates the analysis of RSS feeds using LLMs to identify tech trends.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .llm_client import LLMClientFactory

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """
    Orchestrates the analysis of RSS feed files using LLMs.
    
    Processes feed files sequentially, extracts trends, and saves results.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the trend analyzer.
        
        Args:
            config: Configuration dictionary loaded from YAML
        """
        self.config = config
        self.llm_client = self._initialize_llm_client()
        self.prompt_template = self._load_prompt_template()
        self.feed_base_path = Path(config['rss']['rss-feed'])
        self.output_base_path = Path(config['tech-trend-analysis']['analysis-report'])
        
    def _initialize_llm_client(self):
        """
        Initialize the LLM client based on configuration.
        
        Returns:
            An initialized LLM client instance
            
        Raises:
            ValueError: If API key is missing for the selected provider
        """
        llm_config = self.config['llm']
        provider = llm_config['server']
        model = llm_config['llm-model']
        timeout = llm_config.get('timeout', 60)
        api_keys = llm_config['api_keys']
        
        api_key = api_keys.get(provider, '')
        
        if not api_key and provider != 'ollama':
            raise ValueError(
                f"API key not found for {provider}. "
                f"Please set the appropriate environment variable in .env file."
            )
        
        return LLMClientFactory.create_client(provider, api_key, model, timeout)
    
    def _load_prompt_template(self) -> str:
        """
        Load the prompt template from external file.
        
        Returns:
            The prompt template as a string
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        prompt_path = Path(self.config['tech-trend-analysis']['prompt'])
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template file not found: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        logger.info(f"Loaded prompt template from {prompt_path}")
        return template
    
    def _discover_feed_files(self) -> List[Path]:
        """
        Discover today's JSON feed files in the feed directory.
        
        Only processes feeds from today's date folder (YYYY-MM-DD format).
        
        Returns:
            List of Path objects for today's feed files
        """
        if not self.feed_base_path.exists():
            logger.warning(f"Feed directory not found: {self.feed_base_path}")
            return []
        
        # Get today's date in YYYY-MM-DD format
        today = datetime.now().strftime('%Y-%m-%d')
        today_feed_path = self.feed_base_path / today
        
        if not today_feed_path.exists():
            logger.warning(f"Today's feed directory not found: {today_feed_path}")
            return []
        
        # Get all JSON files in today's directory only
        feed_files = list(today_feed_path.glob('*.json'))
        logger.info(f"Discovered {len(feed_files)} feed files for {today}")
        
        return sorted(feed_files)
    
    def _load_feed_data(self, feed_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load and parse feed data from JSON file.
        
        Args:
            feed_path: Path to the feed JSON file
            
        Returns:
            Parsed feed data or None if loading fails
        """
        try:
            with open(feed_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded feed data from {feed_path}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {feed_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading feed file {feed_path}: {e}")
            return None
    
    def _extract_category(self, feed_data: Dict[str, Any], feed_path: Path) -> str:
        """
        Extract category from feed data or filename.
        
        Args:
            feed_data: Feed data dictionary
            feed_path: Path to the feed file
            
        Returns:
            Category name
        """
        # Try to get category from feed data
        if 'category' in feed_data:
            return feed_data['category']
        
        # Fallback to filename without extension
        category = feed_path.stem
        logger.info(f"Using filename as category: {category}")
        return category
    
    def _create_prompt(self, feed_data: Dict[str, Any]) -> str:
        """
        Create the complete prompt by combining template and feed data.
        
        Args:
            feed_data: Feed data to analyze
            
        Returns:
            Complete prompt string
        """
        # Convert feed data to JSON string
        articles_json = json.dumps(feed_data, indent=2, ensure_ascii=False)
        
        # Replace placeholder in template
        prompt = self.prompt_template.replace('{articles_json}', articles_json)
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Optional[List[Dict[str, Any]]]:
        """
        Parse LLM response, handling potential malformed JSON.
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Parsed trends list or None if parsing fails
        """
        try:
            # Remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            trends = json.loads(cleaned_response)
            
            # Validate structure
            if not isinstance(trends, list):
                logger.error("LLM response is not a list")
                return None
            
            logger.info(f"Parsed {len(trends)} trends from LLM response")
            return trends
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Raw response: {response[:500]}...")
            return None
    
    def _save_analysis(
        self,
        trends: List[Dict[str, Any]],
        feed_path: Path,
        category: str
    ) -> Optional[Path]:
        """
        Save analysis results to structured output path.
        
        Args:
            trends: List of identified trends
            feed_path: Original feed file path
            category: Category name
            
        Returns:
            Path to saved file or None if saving fails
        """
        try:
            # Extract date from feed path (assumes structure: .../YYYY-MM-DD/file.json)
            date_folder = feed_path.parent.name
            
            # Create output directory structure
            output_dir = self.output_base_path / date_folder
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create output filename using original filename (preserves category naming)
            # This maintains the same filename as input: category.json
            output_filename = feed_path.name
            output_path = output_dir / output_filename
            
            # Prepare output data
            output_data = {
                "analysis_timestamp": datetime.now().isoformat(),
                "source_file": feed_path.name,
                "category": category,
                "trends": trends
            }
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved analysis to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            return None
    
    def analyze_feed(self, feed_path: Path) -> Optional[Dict[str, Any]]:
        """
        Analyze a single feed file.
        
        Args:
            feed_path: Path to the feed file
            
        Returns:
            Analysis result summary or None if analysis fails
        """
        logger.info(f"Processing feed: {feed_path}")
        
        # Load feed data
        feed_data = self._load_feed_data(feed_path)
        if feed_data is None:
            return None
        
        # Extract category
        category = self._extract_category(feed_data, feed_path)
        
        # Create prompt
        prompt = self._create_prompt(feed_data)
        
        try:
            # Call LLM
            logger.info(f"Sending request to LLM for {feed_path.name}")
            response = self.llm_client.generate(prompt)
            
            # Parse response
            trends = self._parse_llm_response(response)
            if trends is None:
                return {
                    'success': False,
                    'error': 'Failed to parse LLM response',
                    'file': str(feed_path)
                }
            
            # Save results
            output_path = self._save_analysis(trends, feed_path, category)
            if output_path is None:
                return {
                    'success': False,
                    'error': 'Failed to save analysis',
                    'file': str(feed_path)
                }
            
            return {
                'success': True,
                'file': str(feed_path),
                'category': category,
                'trends_count': len(trends),
                'output_path': str(output_path)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {feed_path}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'file': str(feed_path)
            }
    
    def analyze_all_feeds(self) -> Dict[str, Any]:
        """
        Analyze all feed files in the feed directory.
        
        Returns:
            Summary dictionary with analysis results
        """
        feed_files = self._discover_feed_files()
        
        if not feed_files:
            logger.warning("No feed files found to analyze")
            return {
                'total_processed': 0,
                'total_trends': 0,
                'successful': 0,
                'failed': 0,
                'errors': [],
                'output_directory': str(self.output_base_path)
            }
        
        results = []
        total_trends = 0
        errors = []
        
        for feed_path in feed_files:
            result = self.analyze_feed(feed_path)
            
            if result:
                results.append(result)
                if result['success']:
                    total_trends += result.get('trends_count', 0)
                else:
                    errors.append(f"{result['file']}: {result.get('error', 'Unknown error')}")
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        return {
            'total_processed': len(results),
            'total_trends': total_trends,
            'successful': successful,
            'failed': failed,
            'errors': errors,
            'output_directory': str(self.output_base_path)
        }