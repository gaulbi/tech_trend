"""
Main image processing orchestration module.
"""
import logging
import time
from pathlib import Path
from typing import Optional

from .config import ConfigManager
from .parser import ArticleParser
from .llm import LLMProviderFactory
from .hashnode import HashNodeUploader
from .url_mapper import URLMapper
from .exceptions import (
    ValidationError,
    NetworkError,
    HashNodeUploadError,
    LLMProviderError
)


class ImageProcessor:
    """Orchestrates the image generation pipeline."""
    
    def __init__(
        self,
        config: ConfigManager,
        logger: logging.Logger,
        feed_date: str
    ):
        """
        Initialize image processor.
        
        Args:
            config: Configuration manager
            logger: Logger instance
            feed_date: Feed date string
        """
        self.config = config
        self.logger = logger
        self.feed_date = feed_date
        self.parser = ArticleParser()
        self.url_mapper = URLMapper(config.url_mapping_path)
        self.upload_enabled = config.get('hashnode.upload-enabled', True)
        
        self.llm_provider = self._create_llm_provider()
        self.hashnode_uploader = self._create_hashnode_uploader()
    
    def process(
        self,
        category: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> None:
        """
        Process articles and generate images.
        
        Args:
            category: Specific category to process (None for all)
            file_name: Specific file to process (requires category)
        """
        base_path = self.config.article_base_path / self.feed_date
        
        if not base_path.exists():
            self.logger.warning(
                f"No input directory found for feed date: {self.feed_date}"
            )
            return
        
        if category and file_name:
            self._process_single_file(base_path, category, file_name)
        elif category:
            self._process_category(base_path, category)
        else:
            self._process_all_categories(base_path)
    
    def _process_all_categories(self, base_path: Path) -> None:
        """Process all categories in base path."""
        categories = [d for d in base_path.iterdir() if d.is_dir()]
        
        if not categories:
            self.logger.warning(
                f"No categories found in {base_path}"
            )
            return
        
        for category_dir in categories:
            self._process_category(base_path, category_dir.name)
    
    def _process_category(self, base_path: Path, category: str) -> None:
        """Process all markdown files in a category."""
        category_path = base_path / category
        
        if not category_path.exists():
            self.logger.warning(f"Category not found: {category}")
            return
        
        md_files = list(category_path.glob("*.md"))
        
        if not md_files:
            self.logger.warning(
                f"No markdown files found in category: {category}"
            )
            return
        
        self.logger.info(
            f"Processing category: {category} ({len(md_files)} files)"
        )
        
        for md_file in md_files:
            self._process_article(category, md_file)
        
        self.logger.info(f"Completed category: {category}")
    
    def _process_single_file(
        self,
        base_path: Path,
        category: str,
        file_name: str
    ) -> None:
        """Process a single markdown file."""
        md_file = base_path / category / file_name
        
        if not md_file.exists():
            self.logger.error(
                f"File not found: {category}/{file_name}"
            )
            return
        
        self._process_article(category, md_file)
    
    def _process_article(self, category: str, md_file: Path) -> None:
        """
        Process single article: parse, generate image, upload.
        
        Args:
            category: Article category
            md_file: Path to markdown file
        """
        article_name = md_file.name
        
        try:
            if self._should_skip(category, article_name):
                return
            
            self.logger.info(
                f"Processing: {category}/{article_name}"
            )
            
            summary = self._parse_article(md_file)

            self.logger.info(f"Summary: {summary}")

            local_path = self._get_output_path(category, article_name)
            
            needs_generation = not local_path.exists()
            needs_upload = self._needs_upload(category, article_name)
            
            if needs_generation:
                self._generate_image(summary, local_path)
            
            hashnode_url = None
            status = 'upload_disabled'
            
            if needs_upload and self.upload_enabled and self.hashnode_uploader:
                hashnode_url, status = self._upload_image(local_path)
            elif not self.upload_enabled:
                status = 'upload_disabled'
            elif needs_generation:
                # Image was just generated but upload is disabled/unavailable
                status = 'upload_disabled' if not self.upload_enabled else 'upload_failed'
            
            self.url_mapper.save(
                self.feed_date,
                category,
                article_name,
                str(local_path),
                hashnode_url,
                status
            )
            
            self.logger.info(
                f"Completed: {category}/{article_name}",
                extra={
                    'extra_data': {
                        'status': status,
                        'hashnode_url': hashnode_url
                    }
                }
            )
            
        except ValidationError as e:
            self.logger.error(
                f"Validation error for {article_name}: {e}"
            )
        except Exception as e:
            self.logger.error(
                f"Unexpected error processing {article_name}: {e}",
                exc_info=True
            )
    
    def _should_skip(self, category: str, article_name: str) -> bool:
        """Check if article should be skipped (already processed)."""
        output_path = self._get_output_path(category, article_name)
        mapping = self.url_mapper.load(
            self.feed_date,
            category,
            article_name
        )
        
        if output_path.exists() and mapping and mapping.get('status') == 'success':
            self.logger.info(
                f"Skipping {article_name} "
                f"(already processed for {category}/{self.feed_date})"
            )
            return True
        
        return False
    
    def _needs_upload(self, category: str, article_name: str) -> bool:
        """Check if image needs to be uploaded to Hashnode."""
        mapping = self.url_mapper.load(
            self.feed_date,
            category,
            article_name
        )
        
        if not mapping:
            return True
        
        status = mapping.get('status')
        return status in ['upload_failed', 'upload_disabled']
    
    def _parse_article(self, md_file: Path) -> str:
        """Parse article and extract summary."""
        return self.parser.parse(md_file)
    
    def _get_output_path(self, category: str, article_name: str) -> Path:
        """Get output path for generated image."""
        output_format = self.config.get('image-generator.output-format', 'jpg')
        file_stem = Path(article_name).stem
        
        return (
            self.config.image_output_path /
            self.feed_date /
            category /
            f"{file_stem}.{output_format}"
        )
    
    def _generate_image(self, summary: str, output_path: Path) -> None:
        """Generate image with retry logic."""
        max_retries = self.config.get('image-generator.retry', 3)
        
        for attempt in range(max_retries):
            try:
                self.llm_provider.generate_image(summary, output_path)
                return
            except LLMProviderError as e:
                if attempt == max_retries - 1:
                    raise NetworkError(
                        f"Image generation failed after {max_retries} attempts: {e}"
                    )
                
                wait_time = 2 ** attempt
                self.logger.warning(
                    f"Generation attempt {attempt + 1} failed, "
                    f"retrying in {wait_time}s: {e}"
                )
                time.sleep(wait_time)
    
    def _upload_image(self, local_path: Path) -> tuple:
        """
        Upload image to Hashnode.
        
        Returns:
            Tuple of (hashnode_url, status)
        """
        if not self.hashnode_uploader:
            return None, 'upload_disabled'
        
        try:
            url = self.hashnode_uploader.upload(local_path)
            return url, 'success'
        except HashNodeUploadError as e:
            self.logger.error(f"Hashnode upload failed: {e}")
            return None, 'upload_failed'
    
    def _create_llm_provider(self):
        """Create LLM provider instance."""
        provider_name = self.config.get('image-generator.provider')
        model = self.config.get('image-generator.llm-model')
        
        return LLMProviderFactory.create(
            provider_name,
            model,
            self.config
        )
    
    def _create_hashnode_uploader(self) -> Optional[HashNodeUploader]:
        """Create Hashnode uploader instance."""
        if not self.upload_enabled:
            self.logger.info("Hashnode upload is disabled in config")
            return None
        
        api_key = self.config.get_env('HASHNODE_API_KEY')
        if not api_key:
            self.logger.warning(
                "HASHNODE_API_KEY not set, uploads will be disabled"
            )
            self.upload_enabled = False
            return None
        
        return HashNodeUploader(
            api_key=api_key,
            base_url=self.config.get('hashnode.url'),
            timeout=self.config.get('hashnode.timeout', 30),
            max_retries=self.config.get('hashnode.retry', 3),
            logger=self.logger
        )
