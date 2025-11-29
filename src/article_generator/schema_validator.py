"""
Schema Validator Module

Validates analysis JSON files against expected schema.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Validates analysis JSON schema."""
    
    @staticmethod
    def validate_analysis(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate analysis JSON structure.
        
        Expected schema:
        {
            "analysis_timestamp": str,
            "source_file": str,
            "category": str,
            "trends": [
                {
                    "topic": str,
                    "reason": str,
                    "category": str,
                    "links": [str],
                    "search_keywords": [str]
                }
            ]
        }
        
        Args:
            data: Parsed JSON data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check top-level required fields
        required_fields = ['analysis_timestamp', 'source_file', 'category', 'trends']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate category
        if 'category' in data:
            if not isinstance(data['category'], str) or not data['category'].strip():
                errors.append("Field 'category' must be a non-empty string")
        
        # Validate trends
        if 'trends' in data:
            if not isinstance(data['trends'], list):
                errors.append("Field 'trends' must be a list")
            elif len(data['trends']) == 0:
                errors.append("Field 'trends' cannot be empty")
            else:
                # Validate each trend
                for i, trend in enumerate(data['trends']):
                    trend_errors = SchemaValidator._validate_trend(trend, i)
                    errors.extend(trend_errors)
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.error(f"Schema validation failed with {len(errors)} error(s)")
            for error in errors:
                logger.error(f"  - {error}")
        else:
            logger.info("Schema validation passed")
        
        return is_valid, errors
    
    @staticmethod
    def _validate_trend(trend: Dict[str, Any], index: int) -> List[str]:
        """
        Validate a single trend object.
        
        Args:
            trend: Trend dictionary
            index: Index in trends array
            
        Returns:
            List of error messages
        """
        errors = []
        prefix = f"trends[{index}]"
        
        # Check required fields
        required_trend_fields = ['topic', 'reason', 'category', 'links', 'search_keywords']
        for field in required_trend_fields:
            if field not in trend:
                errors.append(f"{prefix}: Missing required field '{field}'")
        
        # Validate topic
        if 'topic' in trend:
            if not isinstance(trend['topic'], str) or not trend['topic'].strip():
                errors.append(f"{prefix}.topic must be a non-empty string")
        
        # Validate reason (critical for similarity search)
        if 'reason' in trend:
            if not isinstance(trend['reason'], str) or not trend['reason'].strip():
                errors.append(f"{prefix}.reason must be a non-empty string")
        
        # Validate category
        if 'category' in trend:
            if not isinstance(trend['category'], str) or not trend['category'].strip():
                errors.append(f"{prefix}.category must be a non-empty string")
        
        # Validate links
        if 'links' in trend:
            if not isinstance(trend['links'], list):
                errors.append(f"{prefix}.links must be a list")
            else:
                for j, link in enumerate(trend['links']):
                    if not isinstance(link, str):
                        errors.append(f"{prefix}.links[{j}] must be a string")
        
        # Validate search_keywords
        if 'search_keywords' in trend:
            if not isinstance(trend['search_keywords'], list):
                errors.append(f"{prefix}.search_keywords must be a list")
            else:
                for j, keyword in enumerate(trend['search_keywords']):
                    if not isinstance(keyword, str):
                        errors.append(f"{prefix}.search_keywords[{j}] must be a string")
        
        return errors