"""
Report Generator Module

Generates summary reports for article generation runs.
"""

import logging
from typing import List
from src.article_generator.article_service import ProcessingResult

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates summary reports."""
    
    def generate_report(self, results: List[ProcessingResult]) -> str:
        """
        Generate summary report from processing results.
        
        Args:
            results: List of processing results
            
        Returns:
            Formatted report string
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        report_lines = [
            "\n",
            "ARTICLE GENERATION SUMMARY REPORT",
            "=" * 80,
            f"Total Files Processed: {total}",
            f"Successful: {successful}",
            f"Failed: {failed}",
            "",
            "SUCCESSFUL GENERATIONS:",
            "-" * 80
        ]
        
        # Add successful results
        if successful > 0:
            for result in results:
                if result.success:
                    report_lines.append(
                        f"✓ {result.filename} ({result.category})\n"
                        f"  Output: {result.output_path}\n"
                        f"  Trends: {result.trends_processed}"
                    )
        else:
            report_lines.append("None")
        
        # Add failed results
        if failed > 0:
            report_lines.extend([
                "",
                "FAILED GENERATIONS:",
                "-" * 80
            ])
            for result in results:
                if not result.success:
                    report_lines.append(
                        f"✗ {result.filename} ({result.category})\n"
                        f"  Error: {result.error_message}"
                    )
        
        # Add statistics
        report_lines.extend([
            "",
            "STATISTICS:",
            "-" * 80,
            f"Success Rate: {(successful/total*100):.1f}%" if total > 0 else "N/A",
            f"Total Trends Processed: {sum(r.trends_processed for r in results if r.success)}",
            ""
        ])
        
        return "\n".join(report_lines)