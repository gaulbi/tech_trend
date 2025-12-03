# src/web_scraper/file_processor.py
"""File I/O operations for web scraper."""

import json
from pathlib import Path
from typing import List, Optional

from .models import InputData, OutputData, Trend, ScrapedTrend
from .exceptions import ValidationError


class FileProcessor:
    """Handle file reading and writing operations."""
    
    @staticmethod
    def read_input_file(file_path: Path) -> Optional[InputData]:
        """
        Read and parse input JSON file.
        
        Args:
            file_path: Path to input file
            
        Returns:
            Parsed input data or None if parsing failed
            
        Raises:
            ValidationError: If JSON is malformed
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            trends = [
                Trend(
                    topic=t['topic'],
                    reason=t['reason'],
                    links=t['links'],
                    search_keywords=t['search_keywords']
                )
                for t in data.get('trends', [])
            ]
            
            return InputData(
                analysis_date=data['analysis_date'],
                category=data['category'],
                trends=trends
            )
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in {file_path}: {e}")
        except KeyError as e:
            raise ValidationError(f"Missing required field in {file_path}: {e}")
        except Exception as e:
            raise ValidationError(f"Failed to parse {file_path}: {e}")
    
    @staticmethod
    def write_output_file(file_path: Path, data: OutputData) -> None:
        """
        Write output data to JSON file.
        
        Args:
            file_path: Path to output file
            data: Output data to write
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        output = {
            'analysis_date': data.analysis_date,
            'category': data.category,
            'trends': [
                {
                    'topic': t.topic,
                    'query_used': t.query_used,
                    'link': t.link,
                    'content': t.content,
                    'source_search_terms': t.source_search_terms
                }
                for t in data.trends
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(output, f, indent=2)
    
    @staticmethod
    def get_input_files(input_dir: Path) -> List[Path]:
        """
        Get all JSON files from input directory.
        
        Args:
            input_dir: Input directory path
            
        Returns:
            List of JSON file paths
        """
        if not input_dir.exists():
            return []
        
        return list(input_dir.glob('*.json'))
    
    @staticmethod
    def output_exists(output_path: Path) -> bool:
        """
        Check if output file already exists.
        
        Args:
            output_path: Path to output file
            
        Returns:
            True if file exists
        """
        return output_path.exists()