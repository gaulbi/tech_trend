"""
URL mapping storage module.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class URLMapper:
    """Manages URL mapping storage for generated images."""
    
    def __init__(self, base_path: Path):
        """
        Initialize URL mapper.
        
        Args:
            base_path: Base path for URL mapping storage
        """
        self.base_path = base_path
    
    def save(
        self,
        feed_date: str,
        category: str,
        article_file: str,
        local_path: str,
        imgbb_url: Optional[str],
        status: str
    ) -> None:
        """
        Save URL mapping to JSON file.
        
        Args:
            feed_date: Feed date string
            category: Article category
            article_file: Article filename
            local_path: Local image path
            imgbb_url: imgbb_url CDN URL (None if upload failed/disabled)
            status: Upload status (success, upload_failed, upload_disabled)
        """
        mapping_path = self._get_mapping_path(
            feed_date,
            category,
            article_file
        )
        
        mapping_data = {
            'article_file': article_file,
            'category': category,
            'feed_date': feed_date,
            'local_path': local_path,
            'imgbb_url': imgbb_url,
            'uploaded_at': datetime.utcnow().isoformat(),
            'status': status
        }
        
        mapping_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, indent=2, ensure_ascii=False)
    
    def load(
        self,
        feed_date: str,
        category: str,
        article_file: str
    ) -> Optional[dict]:
        """
        Load URL mapping from JSON file.
        
        Args:
            feed_date: Feed date string
            category: Article category
            article_file: Article filename
            
        Returns:
            Mapping dictionary or None if not found
        """
        mapping_path = self._get_mapping_path(
            feed_date,
            category,
            article_file
        )
        
        if not mapping_path.exists():
            return None
        
        try:
            with open(mapping_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _get_mapping_path(
        self,
        feed_date: str,
        category: str,
        article_file: str
    ) -> Path:
        """Get path for URL mapping file."""
        file_stem = Path(article_file).stem
        return (
            self.base_path /
            feed_date /
            category /
            f"{file_stem}.json"
        )
