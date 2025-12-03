"""
Category processing logic for wiki_search module.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

from .content_cleaner import clean_wikipedia_content
from .file_handler import save_output
from .wikipedia_client import WikipediaClient


class CategoryProcessor:
    """Processes a single category: searches Wikipedia and saves results."""
    
    def __init__(
        self,
        wikipedia_client: WikipediaClient,
        max_results: int,
        logger: logging.Logger
    ):
        """
        Initialize category processor.
        
        Args:
            wikipedia_client: Wikipedia API client
            max_results: Maximum search results per query
            logger: Logger instance
        """
        self.wikipedia_client = wikipedia_client
        self.max_results = max_results
        self.logger = logger
    
    def process(
        self,
        category_data: Dict[str, Any],
        output_path: Path
    ) -> None:
        """
        Process a single category: search Wikipedia and save results.
        
        Args:
            category_data: Category data from input JSON
            output_path: Path to output JSON file
        """
        category = category_data['category']
        output_trends = []
        
        for trend in category_data.get('trends', []):
            topic = trend.get('topic', '')
            search_keywords = trend.get('search_keywords', [])
            
            for keyword in search_keywords:
                trend_results = self._process_keyword(
                    keyword, topic, category
                )
                output_trends.extend(trend_results)
        
        # Save output
        output_data = {
            'analysis_date': category_data['analysis_date'],
            'category': category,
            'trends': output_trends
        }
        
        save_output(output_path, output_data)
        
        self.logger.info(
            f"Saved {len(output_trends)} results for category",
            extra={'category': category}
        )
    
    def _process_keyword(
        self,
        keyword: str,
        topic: str,
        category: str
    ) -> List[Dict[str, str]]:
        """
        Process a single search keyword.
        
        Args:
            keyword: Search keyword
            topic: Original topic from input
            category: Category name
            
        Returns:
            List of trend result dictionaries
        """
        results = []
        
        # Search Wikipedia
        titles = self.wikipedia_client.search(
            keyword, self.max_results, self.logger, category
        )
        
        if not titles:
            self.logger.warning(
                f"No results found for keyword: {keyword}",
                extra={'category': category}
            )
            return results
        
        # Fetch and process each page
        for title in titles:
            page_result = self._fetch_and_clean_page(
                title, keyword, topic, category
            )
            if page_result:
                results.append(page_result)
        
        return results
    
    def _fetch_and_clean_page(
        self,
        title: str,
        keyword: str,
        topic: str,
        category: str
    ) -> Dict[str, str]:
        """
        Fetch a Wikipedia page and clean its content.
        
        Args:
            title: Wikipedia page title
            keyword: Search keyword that found this page
            topic: Original topic from input
            category: Category name
            
        Returns:
            Dictionary with topic, keyword, link, and cleaned content
        """
        result = self.wikipedia_client.fetch_page(
            title, self.logger, category
        )
        
        if result is None:
            return None
        
        url, content = result
        cleaned_content = clean_wikipedia_content(content)
        
        self.logger.info(
            f"Successfully processed: {title}",
            extra={'category': category}
        )
        
        return {
            'topic': topic,
            'search_keywords': keyword,
            'link': url,
            'content': cleaned_content
        }