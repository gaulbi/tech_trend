"""
Report Generator Module

Generates summary reports for scraping operations.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates summary reports for web scraping operations.
    
    Compiles statistics and error information into structured reports.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        logger.info("Initialized ReportGenerator")
    
    def generate_summary(
        self,
        results: List[Dict[str, Any]],
        errors: List[str],
        elapsed_time: float,
        date: str
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report.
        
        Args:
            results: List of processing result dictionaries
            errors: List of error messages
            elapsed_time: Total elapsed time in seconds
            date: Processing date (YYYY-MM-DD)
            
        Returns:
            Summary report dictionary
        """
        total_files = len(results)
        total_trends = sum(r.get('trends_processed', 0) for r in results)
        total_scraped = sum(r.get('trends_scraped', 0) for r in results)
        
        summary = {
            'date': date,
            'total_files_processed': total_files,
            'total_trends_found': total_trends,
            'total_trends_scraped': total_scraped,
            'success_rate': self._calculate_success_rate(total_trends, total_scraped),
            'elapsed_time_seconds': round(elapsed_time, 2),
            'categories': [r.get('category', 'Unknown') for r in results],
            'errors': errors,
            'error_count': len(errors),
            'output_paths': [r.get('output_path', '') for r in results]
        }
        
        logger.info(f"Generated summary report: {total_files} files, "
                   f"{total_trends} trends, {total_scraped} scraped")
        
        return summary
    
    def _calculate_success_rate(self, total: int, successful: int) -> float:
        """
        Calculate success rate percentage.
        
        Args:
            total: Total number of items
            successful: Number of successful items
            
        Returns:
            Success rate as percentage (0-100)
        """
        if total == 0:
            return 0.0
        return round((successful / total) * 100, 2)
    
    def format_summary_text(self, summary: Dict[str, Any]) -> str:
        """
        Format summary as human-readable text.
        
        Args:
            summary: Summary dictionary
            
        Returns:
            Formatted text report
        """
        lines = [
            "=" * 60,
            "WEB SCRAPING SUMMARY REPORT",
            "=" * 60,
            f"Date: {summary.get('date', 'N/A')}",
            f"Files Processed: {summary.get('total_files_processed', 0)}",
            f"Trends Found: {summary.get('total_trends_found', 0)}",
            f"Trends Scraped: {summary.get('total_trends_scraped', 0)}",
            f"Success Rate: {summary.get('success_rate', 0)}%",
            f"Elapsed Time: {summary.get('elapsed_time_seconds', 0):.2f}s",
            "",
            "Categories Processed:",
        ]
        
        for category in summary.get('categories', []):
            lines.append(f"  - {category}")
        
        if summary.get('errors'):
            lines.extend([
                "",
                f"Errors ({summary.get('error_count', 0)}):",
            ])
            for error in summary.get('errors', []):
                lines.append(f"  - {error}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)