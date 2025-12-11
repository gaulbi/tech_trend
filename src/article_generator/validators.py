"""Input validation utilities."""
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from .exceptions import ArticleGeneratorError


class ValidationError(ArticleGeneratorError):
    """Raised when validation fails."""
    pass


class InputValidator:
    """Validates input data and configurations."""
    
    @staticmethod
    def validate_feed_date(feed_date: str) -> bool:
        """
        Validate feed date format (YYYY-MM-DD).
        
        Args:
            feed_date: Date string to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If format invalid
        """
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, feed_date):
            raise ValidationError(
                f"Invalid feed_date format: {feed_date}. "
                f"Expected YYYY-MM-DD"
            )
        
        # Validate it's a real date
        try:
            datetime.strptime(feed_date, '%Y-%m-%d')
        except ValueError as e:
            raise ValidationError(f"Invalid date: {feed_date}. {str(e)}")
        
        return True
    
    @staticmethod
    def validate_category(category: str) -> bool:
        """
        Validate category name.
        
        Args:
            category: Category name to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If invalid
        """
        if not category:
            raise ValidationError("Category cannot be empty")
        
        # Category should be alphanumeric with underscores
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(pattern, category):
            raise ValidationError(
                f"Invalid category: {category}. "
                f"Use only alphanumeric, underscore, or hyphen characters"
            )
        
        return True
    
    @staticmethod
    def validate_json_schema(data: Dict[str, Any]) -> bool:
        """
        Validate input JSON schema.
        
        Args:
            data: JSON data to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If schema invalid
        """
        required_fields = ['feed_date', 'category', 'trends']
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(
                    f"Missing required field: {field}"
                )
        
        if not isinstance(data['trends'], list):
            raise ValidationError("'trends' must be a list")
        
        # Validate each trend
        for idx, trend in enumerate(data['trends']):
            InputValidator.validate_trend_schema(trend, idx)
        
        return True
    
    @staticmethod
    def validate_trend_schema(trend: Dict[str, Any], index: int) -> bool:
        """
        Validate single trend schema.
        
        Args:
            trend: Trend data
            index: Trend index for error messages
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If schema invalid
        """
        required_fields = ['topic', 'reason', 'score', 'search_keywords']
        
        for field in required_fields:
            if field not in trend:
                raise ValidationError(
                    f"Trend #{index}: Missing required field '{field}'"
                )
        
        if not isinstance(trend['search_keywords'], list):
            raise ValidationError(
                f"Trend #{index}: 'search_keywords' must be a list"
            )
        
        if not trend['search_keywords']:
            raise ValidationError(
                f"Trend #{index}: 'search_keywords' cannot be empty"
            )
        
        if not isinstance(trend['score'], (int, float)):
            raise ValidationError(
                f"Trend #{index}: 'score' must be a number"
            )
        
        return True
    
    @staticmethod
    def validate_file_exists(file_path: Path, file_type: str = "File") -> bool:
        """
        Validate file exists.
        
        Args:
            file_path: Path to check
            file_type: Type of file for error message
            
        Returns:
            True if exists
            
        Raises:
            ValidationError: If file doesn't exist
        """
        if not file_path.exists():
            raise ValidationError(
                f"{file_type} not found: {file_path}"
            )
        return True
    
    @staticmethod
    def sanitize_path(path_component: str) -> str:
        """
        Sanitize path component to prevent path traversal.
        
        Args:
            path_component: Path component to sanitize
            
        Returns:
            Sanitized path component
            
        Raises:
            ValidationError: If path contains dangerous patterns
        """
        dangerous_patterns = ['..', '~', '/', '\\']
        
        for pattern in dangerous_patterns:
            if pattern in path_component:
                raise ValidationError(
                    f"Invalid path component: {path_component}. "
                    f"Contains dangerous pattern: {pattern}"
                )
        
        # Remove any null bytes
        sanitized = path_component.replace('\0', '')
        
        return sanitized