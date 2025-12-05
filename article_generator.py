"""Main orchestrator for article generation."""

import json
import sys
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

from src.article_generator import (
    Config,
    ConfigurationError,
    EmbeddingFactory,
    LLMFactory,
    RAGEngine,
    ensure_directory,
    get_today_date,
    inject_prompt_variables,
    load_config,
    load_prompt_template,
    setup_logger,
    slugify,
)


class ValidationError(Exception):
    """Raised when data validation fails."""
    pass


class ArticleGenerator:
    """Main orchestrator for generating articles from tech trends."""
    
    def __init__(self, config: Config):
        """Initialize article generator.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.today_date = get_today_date()
        self.logger = setup_logger(
            self.config.article_generator.log,
            self.today_date
        )
        
        # Initialize LLM client
        self.llm_client = LLMFactory.create(
            provider=self.config.llm.server,
            model=self.config.llm.llm_model,
            timeout=self.config.llm.timeout,
            max_retries=self.config.llm.retry
        )
        
        # Initialize embedding client
        self.embedding_client = EmbeddingFactory.create(
            provider=self.config.embedding.embedding_provider,
            model=self.config.embedding.embedding_model,
            timeout=self.config.embedding.timeout,
            max_retries=self.config.embedding.max_retries
        )
        
        # Initialize RAG engine
        self.rag_engine = RAGEngine(
            database_path=self.config.embedding.database_path,
            embedding_client=self.embedding_client
        )
        
        # Load prompt templates
        self.system_prompt = load_prompt_template(
            self.config.article_generator.system_prompt
        )
        self.user_prompt_template = load_prompt_template(
            self.config.article_generator.user_prompt
        )
        
        self.logger.info(
            "Article generator initialized",
            extra={"date": self.today_date}
        )
    
    def discover_input_files(self) -> List[Path]:
        """Discover JSON files for today's date.
        
        Returns:
            List of JSON file paths
        """
        input_dir = Path(
            self.config.tech_trend_analysis.analysis_report
        ) / self.today_date
        
        if not input_dir.exists():
            self.logger.warning(
                f"Input directory does not exist: {input_dir}"
            )
            return []
        
        json_files = list(input_dir.glob("*.json"))
        
        self.logger.info(
            f"Discovered {len(json_files)} JSON files",
            extra={"directory": str(input_dir)}
        )
        
        return json_files
    
    def load_trend_data(self, file_path: Path) -> Dict:
        """Load and validate trend data from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            ValidationError: If JSON is malformed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate required fields
            required_fields = ["analysis_date", "category", "trends"]
            for field in required_fields:
                if field not in data:
                    raise ValidationError(
                        f"Missing required field: {field}"
                    )
            
            # Validate category is a string
            if not isinstance(data["category"], str):
                raise ValidationError(
                    f"Field 'category' must be a string, got {type(data['category']).__name__}"
                )
            
            if not data["category"].strip():
                raise ValidationError("Field 'category' is empty")
            
            # Validate trends is a list
            if not isinstance(data["trends"], list):
                raise ValidationError(
                    "Field 'trends' must be a list"
                )
            
            return data
        
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            raise ValidationError(f"Error loading {file_path}: {e}")
    
    def validate_trend(self, trend: Dict) -> bool:
        """Validate that a trend has required fields and correct types.
        
        Args:
            trend: Trend dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["topic", "reason"]
        
        for field in required_fields:
            if field not in trend:
                self.logger.warning(
                    f"Trend missing required field: {field}",
                    extra={"trend": str(trend)}
                )
                return False
            
            # Validate field is a non-empty string
            value = trend[field]
            if not isinstance(value, str):
                self.logger.warning(
                    f"Trend field '{field}' must be a string, got {type(value).__name__}",
                    extra={"trend": str(trend), "field_value": str(value)}
                )
                return False
            
            if not value.strip():
                self.logger.warning(
                    f"Trend field '{field}' is empty",
                    extra={"trend": str(trend)}
                )
                return False
        
        # Validate search_keywords if present (should be list of strings)
        if "search_keywords" in trend:
            keywords = trend["search_keywords"]
            if not (isinstance(keywords, list) and all(isinstance(kw, str) for kw in keywords)):
                # Allow string for backward compatibility
                if not isinstance(keywords, str):
                    self.logger.warning(
                        f"Trend field 'search_keywords' must be a list of strings or a string, got {type(keywords).__name__}",
                        extra={"trend": str(trend), "field_value": str(keywords)}
                    )
                    return False
        
        return True
    
    def construct_output_path(
        self, category: str, topic: str
    ) -> Path:
        """Construct output file path for article.
        
        Args:
            category: Trend category
            topic: Trend topic
            
        Returns:
            Path object for output file
            
        Raises:
            ValueError: If slugification fails
        """
        try:
            slug = slugify(topic)
        except ValueError as e:
            raise ValueError(
                f"Cannot create valid filename from topic '{topic}': {e}"
            )
        
        output_dir = (
            Path(self.config.article_generator.tech_trend_article)
            / self.today_date
            / category
        )
        
        return output_dir / f"{slug}.md"
    
    def process_trend(
        self, trend: Dict, category: str
    ) -> bool:
        """Process a single trend and generate article.
        
        Args:
            trend: Trend dictionary with topic, reason, etc.
            category: Category name
            
        Returns:
            True if successful, False otherwise
        """
        # Validate trend structure
        if not self.validate_trend(trend):
            return False
        
        topic = trend["topic"]
        
        # Construct output path (may raise ValueError)
        try:
            output_path = self.construct_output_path(category, topic)
        except ValueError as e:
            self.logger.error(
                f"Failed to construct output path: {e}",
                extra={"topic": topic, "category": category}
            )
            return False
        
        # Check if already exists (idempotency)
        if output_path.exists():
            self.logger.info(
                f"Article already exists, skipping: {topic}",
                extra={"path": str(output_path)}
            )
            return True
        
        try:
            # Retrieve context using RAG
            search_keywords_list = trend.get("search_keywords", [])
            if not isinstance(search_keywords_list, list):
                # Fallback: if it's a string, wrap in list
                if isinstance(search_keywords_list, str):
                    search_keywords_list = [search_keywords_list]
                else:
                    search_keywords_list = []
            context = self.rag_engine.retrieve_context(
                query_text=", ".join(search_keywords_list),
                category=category,
                embedding_date=self.today_date,
                top_k=self.config.embedding.ktop
            )
            
            # Validate context was retrieved
            if not context or not context.strip():
                self.logger.warning(
                    f"No context retrieved from RAG for trend: {topic}",
                    extra={"category": category, "query_text": ", ".join(search_keywords_list)}
                )
                # Continue anyway but log the issue
                context = "No relevant context found in knowledge base."
            
            # Prepare prompt variables
            search_keywords = str(search_keywords_list)

            variables = {
                "context": context,
                "search_keywords": search_keywords,
                "reason": trend["reason"]
            }
            
            # Inject variables into user prompt
            user_prompt = inject_prompt_variables(
                self.user_prompt_template,
                variables
            )
            
            # Generate article using LLM
            self.logger.info(
                f"Generating article: {topic}",
                extra={"category": category}
            )
            article_content = self.llm_client.generate(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt
            )
            
            # Validate LLM response
            if not article_content or not isinstance(article_content, str):
                raise ValueError(
                    f"LLM returned invalid response: {type(article_content)}"
                )
            
            article_content = article_content.strip()
            if not article_content:
                raise ValueError("LLM returned empty content")
            
            # Validate content has minimum length (at least 100 characters)
            if len(article_content) < 100:
                raise ValueError(
                    f"LLM response too short ({len(article_content)} chars). "
                    "Possible generation failure."
                )
            
            # Save to disk
            ensure_directory(output_path.parent)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(article_content)
            
            self.logger.info(
                f"Article generated successfully: {topic}",
                extra={
                    "output_path": str(output_path),
                    "content_length": len(article_content)
                }
            )
            
            return True
        
        except Exception as e:
            self.logger.error(
                f"Failed to process trend: {topic}",
                extra={"error": str(e), "category": category},
                exc_info=True
            )
            return False
    
    def process_file(self, file_path: Path) -> None:
        """Process all trends in a single JSON file.
        
        Args:
            file_path: Path to JSON file
        """
        try:
            # Load trend data
            data = self.load_trend_data(file_path)
            category = data["category"]
            trends = data["trends"]
            
            self.logger.info(
                f"Processing file: {file_path.name}",
                extra={
                    "category": category,
                    "trend_count": len(trends)
                }
            )
            
            # Process each trend
            success_count = 0
            for trend in trends:
                if self.process_trend(trend, category):
                    success_count += 1
            
            self.logger.info(
                f"File processing complete: {file_path.name}",
                extra={
                    "successful": success_count,
                    "total": len(trends)
                }
            )
        
        except ValidationError as e:
            self.logger.error(
                f"Validation error for {file_path.name}: {e}",
                extra={"file": str(file_path)}
            )
        except Exception as e:
            self.logger.error(
                f"Unexpected error processing {file_path.name}: {e}",
                extra={"file": str(file_path)},
                exc_info=True
            )
    
    def run(self) -> None:
        """Execute the article generation workflow."""
        self.logger.info("Starting article generation workflow")
        
        # Discover input files
        input_files = self.discover_input_files()
        
        if not input_files:
            self.logger.warning("No input files found. Exiting.")
            return
        
        # Process each file
        for file_path in input_files:
            self.process_file(file_path)
        
        self.logger.info(
            "Article generation workflow complete",
            extra={"files_processed": len(input_files)}
        )


def main():
    """Main entry point for article generator script."""
    # Load environment variables
    load_dotenv()
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize and run generator
        generator = ArticleGenerator(config)
        generator.run()
        
    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()