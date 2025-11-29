"""RSS sources loader and manager."""

import json
from pathlib import Path
from typing import Dict
import re


class RSSSourcesLoader:
    """Loads and manages RSS feed sources."""
    
    def __init__(self, sources_path: Path):
        """
        Initialize sources loader.
        
        Args:
            sources_path: Path to RSS sources JSON file
            
        Raises:
            FileNotFoundError: If sources file doesn't exist
            ValueError: If sources file is invalid
        """
        self.sources_path = sources_path
        self.sources = self._load_sources()
    
    def _load_sources(self) -> Dict[str, Dict[str, str]]:
        """Load RSS sources from JSON file."""
        if not self.sources_path.exists():
            raise FileNotFoundError(f"Sources file not found: {self.sources_path}")
        
        with open(self.sources_path, 'r', encoding='utf-8') as f:
            sources = json.load(f)
        
        if not isinstance(sources, dict):
            raise ValueError("Sources file must contain a JSON object")
        
        return sources
    
    def get_categories(self) -> list[str]:
        """Get list of all categories."""
        return list(self.sources.keys())
    
    def get_sources_for_category(self, category: str) -> Dict[str, str]:
        """
        Get all sources for a specific category.
        
        Args:
            category: Category name
            
        Returns:
            Dictionary mapping source names to URLs
        """
        return self.sources.get(category, {})
    
    @staticmethod
    def category_to_filename(category: str) -> str:
        """
        Convert category name to safe filename.
        
        Args:
            category: Category name (e.g., "AI / Machine Learning")
            
        Returns:
            Safe filename (e.g., "ai-machine-learning")
        """
        # Convert to lowercase
        filename = category.lower()
        
        # Replace spaces and slashes with hyphens
        filename = re.sub(r'[\s/]+', '-', filename)
        
        # Remove special characters except hyphens
        filename = re.sub(r'[^a-z0-9\-]', '', filename)
        
        # Remove multiple consecutive hyphens
        filename = re.sub(r'-+', '-', filename)
        
        # Remove leading/trailing hyphens
        filename = filename.strip('-')
        
        return filename