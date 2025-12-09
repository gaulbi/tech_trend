"""
File handling operations for wiki_search module.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from .exceptions import ValidationError


def get_input_files(base_dir: Path, today: str) -> List[Path]:
    """
    Get all category JSON files for today's date.
    
    Args:
        base_dir: Base directory for tech trend analysis
        today: Today's date string (YYYY-MM-DD)
        
    Returns:
        List of JSON file paths
    """
    input_dir = base_dir / today
    if not input_dir.exists():
        return []
    
    return list(input_dir.glob("*.json"))


def load_category_data(file_path: Path) -> Dict[str, Any]:
    """
    Load and validate category JSON file.
    
    Args:
        file_path: Path to category JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        ValidationError: If JSON is malformed or invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        raise ValidationError(f"Failed to read {file_path}: {e}")
    
    _validate_category_data(data, file_path)
    return data


def _validate_category_data(data: Dict[str, Any], file_path: Path) -> None:
    """
    Validate category data structure.
    
    Args:
        data: Category data dictionary
        file_path: Path to source file (for error messages)
        
    Raises:
        ValidationError: If required fields are missing
    """
    required_fields = ['analysis_date', 'category', 'trends']
    for field in required_fields:
        if field not in data:
            raise ValidationError(
                f"Missing required field '{field}' in {file_path}"
            )


def save_output(output_path: Path, data: Dict[str, Any]) -> None:
    """
    Save output data to JSON file.
    
    Args:
        output_path: Path to output file
        data: Data to save
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def output_exists(output_path: Path) -> bool:
    """
    Check if output file already exists.
    
    Args:
        output_path: Path to check
        
    Returns:
        True if file exists, False otherwise
    """
    return output_path.exists()