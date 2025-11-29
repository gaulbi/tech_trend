"""
Article Service Module

Main business logic for article generation.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from src.article_generator.config_loader import Config
from src.article_generator.chromadb_service import ChromaDBService
from src.article_generator.prompt_service import PromptService
from src.article_generator.llm_client_base import LLMClientFactory
from src.article_generator.schema_validator import SchemaValidator

logger = logging.getLogger(__name__)


class ProcessingResult:
    """Container for processing results."""
    
    def __init__(self, filename: str, category: str):
        self.filename = filename
        self.category = category
        self.success = False
        self.error_message = None
        self.output_path = None
        self.trends_processed = 0
    
    def mark_success(self, output_path: str, trends_count: int):
        """Mark as successful."""
        self.success = True
        self.output_path = output_path
        self.trends_processed = trends_count
    
    def mark_failure(self, error_message: str):
        """Mark as failed."""
        self.success = False
        self.error_message = error_message


class ArticleService:
    """Service for generating articles."""
    
    def __init__(self, config: Config):
        """
        Initialize article service.
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Initialize services
        self.chromadb_service = ChromaDBService(config)
        self.prompt_service = PromptService(
            config.paths.system_prompt,
            config.paths.user_prompt
        )
        
        # Initialize LLM client
        api_key = config.api_keys.get(config.llm.server)
        self.llm_client = LLMClientFactory.create_client(
            provider=config.llm.server,
            model=config.llm.model,
            api_key=api_key,
            timeout=config.llm.timeout,
            max_retries=3
        )
        
        logger.info(f"Article service initialized with LLM: {config.llm.server}")
    
    def process_all_analyses(self) -> List[ProcessingResult]:
        """
        Process all analysis files.
        
        Returns:
            List of processing results
        """
        results = []
        analysis_base_path = Path(self.config.paths.analysis_report)
        
        # Find all analysis JSON files recursively
        analysis_files = list(analysis_base_path.rglob('*.json'))
        
        if not analysis_files:
            logger.warning(f"No analysis files found in: {analysis_base_path}")
            return results
        
        logger.info(f"Found {len(analysis_files)} analysis file(s) to process")
        
        # Process each file with error isolation
        for analysis_file in analysis_files:
            try:
                result = self._process_single_analysis(analysis_file)
                results.append(result)
            except Exception as e:
                # Ensure we capture all errors and continue processing
                logger.error(f"Unexpected error processing {analysis_file}: {e}", exc_info=True)
                result = ProcessingResult(analysis_file.name, "Unknown")
                result.mark_failure(f"Unexpected error: {str(e)}")
                results.append(result)
        
        return results
    
    def _process_single_analysis(self, analysis_file: Path) -> ProcessingResult:
        """
        Process a single analysis file.
        
        Args:
            analysis_file: Path to analysis JSON file
            
        Returns:
            Processing result
        """
        logger.info("=" * 80)
        logger.info(f"Processing: {analysis_file}")
        
        result = ProcessingResult(analysis_file.name, "Unknown")
        
        try:
            # Load analysis file
            analysis_data = self._load_analysis_file(analysis_file)
            result.category = analysis_data.get('category', 'Unknown')
            
            # Validate schema
            is_valid, validation_errors = SchemaValidator.validate_analysis(analysis_data)
            if not is_valid:
                error_msg = f"Schema validation failed: {'; '.join(validation_errors)}"
                logger.error(error_msg)
                result.mark_failure(error_msg)
                return result
            
            # Extract date from file path (format: .../YYYY-MM-DD/filename.json)
            date_str = self._extract_date_from_path(analysis_file)
            logger.info(f"Processing category: {result.category}, date: {date_str}")
            
            # Process trends
            trends = analysis_data.get('trends', [])
            if not trends:
                logger.warning("No trends found in analysis file")
                result.mark_failure("No trends found")
                return result
            
            logger.info(f"Found {len(trends)} trend(s) to process")
            
            # Generate article for the first trend
            # NOTE: Current implementation processes only the first trend
            # To process all trends, loop through trends list and generate separate articles
            trend = trends[0]
            logger.info(f"Generating article for trend: {trend.get('topic', 'Unknown')}")
            
            article_content = self._generate_article_for_trend(
                trend,
                result.category,
                date_str
            )
            
            # Check if article was generated
            if not article_content or not article_content.strip():
                raise ValueError("LLM returned empty article content")
            
            # Save article
            output_path = self._save_article(
                article_content,
                date_str,
                result.category
            )
            
            result.mark_success(output_path, len(trends))
            logger.info(f"✓ Successfully generated article: {output_path}")
        
        except Exception as e:
            logger.error(f"✗ Failed to process {analysis_file}: {e}", exc_info=True)
            result.mark_failure(str(e))
        
        return result
    
    def _load_analysis_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and parse analysis JSON file.
        
        Args:
            file_path: Path to analysis file
            
        Returns:
            Parsed JSON data
            
        Raises:
            ValueError: If JSON is invalid
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to read {file_path}: {e}")
    
    def _extract_date_from_path(self, file_path: Path) -> str:
        """
        Extract date from file path.
        
        Expected structure: .../YYYY-MM-DD/category.json
        Per spec: data/tech-trend-analysis/YYYY-MM-DD/category.json
        
        Args:
            file_path: Path to analysis file
            
        Returns:
            Date string in YYYY-MM-DD format
        """
        # Get parent directory name (should be the date)
        parent_dir = file_path.parent.name
        
        # Validate it's a date format (YYYY-MM-DD)
        if len(parent_dir) == 10 and parent_dir.count('-') == 2:
            parts = parent_dir.split('-')
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                logger.info(f"Extracted date from path: {parent_dir}")
                return parent_dir
        
        # Fallback to today's date
        today = datetime.now().strftime('%Y-%m-%d')
        logger.warning(f"Could not extract date from path, using today: {today}")
        return today
    
    def _generate_article_for_trend(
        self,
        trend: Dict[str, Any],
        category: str,
        date_str: str
    ) -> str:
        """
        Generate article for a single trend.
        
        Args:
            trend: Trend data from analysis
            category: Category name
            date_str: Date string (YYYY-MM-DD)
            
        Returns:
            Generated article content
        """
        # Get reason (keywords) from trend
        reason = trend.get('reason', '')
        if not reason:
            raise ValueError("Trend missing 'reason' field")
        
        logger.info("Performing similarity search...")
        
        # Perform similarity search
        # Use date_str as embedding_date filter
        context_chunks = self.chromadb_service.similarity_search(
            query_text=reason,
            category=category,
            embedding_date=date_str,
            k=self.config.embedding.ktop
        )
        
        if not context_chunks:
            logger.warning("No context chunks found, proceeding with empty context")
        
        # Craft prompt with context
        logger.info("Crafting prompt with context...")
        prompt = self.prompt_service.craft_prompt(reason, context_chunks)
        
        # Generate article using LLM
        logger.info("Generating article with LLM...")
        article_content = self.llm_client.generate_with_retry(prompt)
        
        return article_content
    
    def _save_article(
        self,
        content: str,
        date_str: str,
        category: str
    ) -> str:
        """
        Save article to file.
        
        Format: {tech_trend_article_output_base_path}/{YYYY-MM-DD}/{category}.md
        
        Args:
            content: Article content
            date_str: Date string (YYYY-MM-DD)
            category: Category name
            
        Returns:
            Path to saved file
        """
        # Create output directory
        output_base = Path(self.config.paths.tech_trend_article)
        output_dir = output_base / date_str
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename from category
        filename = category.lower().replace(' ', '-').replace('/', '-') + '.md'
        output_path = output_dir / filename
        
        # Save file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Article saved to: {output_path}")
        return str(output_path)