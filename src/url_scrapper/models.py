"""
Data Models Module

Defines data structures for the URL scraper application.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Trend:
    """
    Represents a single trend from analysis file.
    
    Attributes:
        topic: The trend topic/title
        reason: Explanation of why this is a trend
        category: Category classification
        links: List of URLs related to this trend
        search_keywords: Keywords for searching
    """
    topic: str
    reason: str
    category: str
    links: List[str]
    search_keywords: List[str] = field(default_factory=list)


@dataclass
class TrendAnalysis:
    """
    Represents a complete trend analysis file.
    
    Attributes:
        analysis_timestamp: When the analysis was performed
        source_file: Original source filename
        category: Overall category
        trends: List of trends
    """
    analysis_timestamp: str
    source_file: str
    category: str
    trends: List[Trend]


@dataclass
class ScrapedContent:
    """
    Represents scraped content from a URL.
    
    Attributes:
        topic: The trend topic this URL belongs to
        link: The URL that was scraped
        content: Cleaned content from the URL
        scrape_timestamp: When the content was scraped
        error: Error message if scraping failed
    """
    topic: str
    link: str
    content: Optional[str] = None
    scrape_timestamp: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ScrapedOutput:
    """
    Represents the output file structure for scraped content.
    
    Attributes:
        analysis_timestamp: Original analysis timestamp
        source_file: Original source filename
        category: Category of the trends
        trends: List of scraped content items
    """
    analysis_timestamp: str
    source_file: str
    category: str
    trends: List[ScrapedContent]


@dataclass
class ProcessingReport:
    """
    Summary report of the processing execution.
    
    Attributes:
        execution_date: Date of execution
        total_categories: Number of categories processed
        total_trends: Number of trends found
        total_urls_scraped: Total URLs attempted
        successful_scrapes: Number of successful scrapes
        failed_scrapes: Number of failed scrapes
        output_directory: Base output directory path
        errors: List of error messages
    """
    execution_date: str
    total_categories: int = 0
    total_trends: int = 0
    total_urls_scraped: int = 0
    successful_scrapes: int = 0
    failed_scrapes: int = 0
    output_directory: str = ""
    errors: List[str] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        """Add an error message to the report."""
        self.errors.append(error)
    
    def increment_success(self) -> None:
        """Increment successful scrape counter."""
        self.successful_scrapes += 1
    
    def increment_failure(self) -> None:
        """Increment failed scrape counter."""
        self.failed_scrapes += 1