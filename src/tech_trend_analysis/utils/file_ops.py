# ============================================================================
# src/tech_trend_analysis/utils/file_ops.py
# ============================================================================

"""File operation utilities."""

import json
from pathlib import Path
from typing import Any, Dict, List

from ..exceptions import ValidationError


def read_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Read and parse a JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data

    Raises:
        ValidationError: If file doesn't exist or JSON is invalid
    """
    if not file_path.exists():
        raise ValidationError(f"File not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        raise ValidationError(f"Failed to read {file_path}: {e}")


def write_json_file(
    file_path: Path,
    data: Dict[str, Any],
    indent: int = 2
) -> None:
    """
    Write data to a JSON file.

    Args:
        file_path: Path to output file
        data: Data to write
        indent: JSON indentation level
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_text_file(file_path: Path) -> str:
    """
    Read a text file.

    Args:
        file_path: Path to text file

    Returns:
        File contents

    Raises:
        ValidationError: If file doesn't exist or can't be read
    """
    if not file_path.exists():
        raise ValidationError(f"File not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise ValidationError(f"Failed to read {file_path}: {e}")


def list_json_files(directory: Path) -> List[Path]:
    """
    List all JSON files in a directory.

    Args:
        directory: Directory to scan

    Returns:
        List of JSON file paths
    """
    if not directory.exists():
        return []

    return sorted(directory.glob('*.json'))