"""
Image generation processor module.
"""
from pathlib import Path
from typing import List, Optional

from .config import Config
from .logger import Logger, log_execution
from .parser import MarkdownParser
from .llm import LLMProviderFactory
from .exceptions import ValidationError, NetworkError, LLMProviderError


class ImageProcessor:
    """Processes markdown files and generates images."""
    
    def __init__(self, config: Config, logger: Logger):
        """
        Initialize processor.
        
        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.parser = MarkdownParser()
        
        # Create LLM provider
        self.llm_provider = LLMProviderFactory.create(
            provider=config.image_generator.provider,
            model=config.image_generator.llm_model,
            timeout=config.image_generator.timeout,
            retry=config.image_generator.retry
        )
    
    def _build_prompt(self, summary: str) -> str:
        """
        Build image generation prompt from summary.
        
        Args:
            summary: Article summary
            
        Returns:
            Complete prompt with style instructions
        """
        style = self.config.image_generator.style_instruction
        return f"{style}\n\n{summary}"
    
    def _get_output_path(
        self,
        feed_date: str,
        category: str,
        md_file: Path
    ) -> Path:
        """
        Get output path for generated image.
        
        Args:
            feed_date: Feed date (YYYY-MM-DD)
            category: Article category
            md_file: Source markdown file
            
        Returns:
            Output path for image
        """
        output_format = self.config.image_generator.output_format
        filename = md_file.stem + f".{output_format}"
        
        return (
            self.config.image_generator.image_path /
            feed_date /
            category /
            filename
        )
    
    def _should_skip(self, output_path: Path, md_file: Path) -> bool:
        """
        Check if image generation should be skipped.
        
        Args:
            output_path: Expected output path
            md_file: Source markdown file
            
        Returns:
            True if should skip
        """
        if output_path.exists():
            self.logger.info(
                f"Skipping {md_file.name} (already processed)"
            )
            print(
                f"Skipping {md_file.name} "
                f"(already processed for {output_path.parent.name}/"
                f"{output_path.parent.parent.name})"
            )
            return True
        return False
    
    def process_file(
        self,
        md_file: Path,
        feed_date: str,
        category: str
    ) -> Optional[Path]:
        """
        Process single markdown file and generate image.
        
        Args:
            md_file: Path to markdown file
            feed_date: Feed date
            category: Article category
            
        Returns:
            Path to generated image or None if skipped/failed
        """
        output_path = self._get_output_path(feed_date, category, md_file)
        
        # Check idempotency
        if self._should_skip(output_path, md_file):
            return None
        
        try:
            # Parse markdown and extract summary
            self.logger.debug(f"Parsing {md_file.name}")
            summary = self.parser.parse_file(md_file)
            
            # Build prompt
            prompt = self._build_prompt(summary)
            
            # Generate image
            self.logger.info(f"Generating image for {md_file.name}")
            self.llm_provider.generate_image(
                prompt=prompt,
                output_path=output_path,
                size=self.config.image_generator.default_size,
                aspect_ratio=self.config.image_generator.aspect_ratio,
                output_format=self.config.image_generator.output_format
            )
            
            self.logger.info(
                f"Successfully generated image: {output_path}"
            )
            return output_path
            
        except ValidationError as e:
            self.logger.error(
                f"Validation error for {md_file.name}: {e}",
                exc_info=False
            )
            return None
            
        except (NetworkError, LLMProviderError) as e:
            self.logger.error(
                f"Failed to generate image for {md_file.name}: {e}",
                exc_info=True
            )
            return None
            
        except Exception as e:
            self.logger.error(
                f"Unexpected error processing {md_file.name}: {e}",
                exc_info=True
            )
            return None
    
    def get_markdown_files(
        self,
        feed_date: str,
        category: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> List[tuple]:
        """
        Get list of markdown files to process.
        
        Args:
            feed_date: Feed date
            category: Specific category (optional)
            file_name: Specific file name (optional)
            
        Returns:
            List of (md_file, category) tuples
        """
        base_path = self.config.article_generator.tech_trend_article / feed_date
        
        if not base_path.exists():
            self.logger.warning(
                f"No data found for feed date: {feed_date}"
            )
            return []
        
        files = []
        
        if category and file_name:
            # Process specific file
            file_path = base_path / category / file_name
            if file_path.exists() and file_path.suffix.lower() == '.md':
                files.append((file_path, category))
            else:
                self.logger.warning(
                    f"File not found: {file_path}"
                )
                
        elif category:
            # Process all files in category
            category_path = base_path / category
            if category_path.exists():
                md_files = list(category_path.glob("*.md"))
                files.extend([(f, category) for f in md_files])
            else:
                self.logger.warning(
                    f"Category not found: {category}"
                )
                
        else:
            # Process all categories
            for cat_path in base_path.iterdir():
                if cat_path.is_dir():
                    md_files = list(cat_path.glob("*.md"))
                    cat_name = cat_path.name
                    files.extend([(f, cat_name) for f in md_files])
        
        return files
    
    def process_batch(
        self,
        feed_date: str,
        category: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> dict:
        """
        Process batch of markdown files.
        
        Args:
            feed_date: Feed date
            category: Specific category (optional)
            file_name: Specific file name (optional)
            
        Returns:
            Statistics dictionary
        """
        files = self.get_markdown_files(feed_date, category, file_name)
        
        if not files:
            self.logger.warning(
                f"No markdown files found for {feed_date}"
            )
            return {
                "total": 0,
                "processed": 0,
                "skipped": 0,
                "failed": 0
            }
        
        self.logger.info(
            f"Found {len(files)} markdown file(s) to process"
        )
        
        stats = {
            "total": len(files),
            "processed": 0,
            "skipped": 0,
            "failed": 0
        }
        
        for md_file, cat in files:
            result = self.process_file(md_file, feed_date, cat)
            
            if result is None:
                if self._get_output_path(feed_date, cat, md_file).exists():
                    stats["skipped"] += 1
                else:
                    stats["failed"] += 1
            else:
                stats["processed"] += 1
        
        return stats
