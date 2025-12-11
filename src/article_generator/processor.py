"""Main article generation processor with validation."""
import json
from datetime import date
from pathlib import Path
from typing import Dict, Any, List, Optional
from .config import Config
from .logger import Logger
from .clients.factories import LLMFactory, EmbeddingFactory
from .rag.retriever import RAGRetriever
from .utils.text_utils import slugify
from .validators import InputValidator, ValidationError


class ArticleProcessor:
    """Main processor for article generation."""
    
    def __init__(self, config: Config, logger: Logger):
        """
        Initialize processor with validation.
        
        Args:
            config: Configuration instance
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # Initialize clients
        self.llm_client = LLMFactory.create(config)
        self.embedding_client = EmbeddingFactory.create(config)
        
        # Initialize RAG retriever with logger and collection name from config
        database_path = config.get('embedding.database-path')
        collection_name = config.get('rag.collection-name', 'embeddings')
        
        self.rag_retriever = RAGRetriever(
            embedding_client=self.embedding_client,
            database_path=database_path,
            collection_name=collection_name,
            logger=logger
        )
        
        # Validate RAG schema
        try:
            schema = self.rag_retriever.validate_schema()
            self.logger.info(f"ChromaDB schema: {schema}")
            
            if schema['status'] == 'empty':
                self.logger.warning(
                    "ChromaDB is empty. Articles may lack context."
                )
            elif schema['status'] == 'invalid':
                self.logger.error(
                    f"ChromaDB missing required fields: "
                    f"{schema['missing_required_fields']}"
                )
        except Exception as e:
            self.logger.error(f"ChromaDB validation failed: {str(e)}")
        
        # Load and validate prompt templates
        self.system_prompt_template = self._load_prompt(
            config.get('article-generator.system-prompt')
        )
        self.user_prompt_template = self._load_prompt(
            config.get('article-generator.user-prompt')
        )
        
        # Validate prompts have required placeholders
        self._validate_prompt_templates()
    
    def _load_prompt(self, path: str) -> str:
        """
        Load prompt template from file.
        
        Args:
            path: Path to prompt file
            
        Returns:
            Prompt content
        """
        prompt_path = Path(path)
        if not prompt_path.exists():
            self.logger.warning(f"Prompt file not found: {path}")
            return ""
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _validate_prompt_templates(self) -> None:
        """Validate prompt templates have required placeholders."""
        required_vars = ['{{context}}', '{{search_keywords}}', '{{reason}}']
        
        for var in required_vars:
            if var not in self.user_prompt_template:
                self.logger.warning(
                    f"User prompt template missing variable: {var}"
                )
    
    def _inject_prompt_variables(
        self,
        template: str,
        context: str,
        search_keywords: List[str],
        reason: str
    ) -> str:
        """
        Inject variables into prompt template.
        
        Args:
            template: Prompt template
            context: RAG context
            search_keywords: Search keywords
            reason: Trend reason
            
        Returns:
            Populated prompt
        """
        prompt = template
        prompt = prompt.replace('{{context}}', context)
        prompt = prompt.replace(
            '{{search_keywords}}',
            ', '.join(search_keywords)
        )
        prompt = prompt.replace('{{reason}}', reason)
        return prompt
    
    def process_category(
        self,
        category: str,
        feed_date: str,
        cnt: Optional[int] = None,
        overwrite: bool = False
    ) -> int:
        """
        Process all trends in a category with validation.
        
        Args:
            category: Category name
            feed_date: Feed date (YYYY-MM-DD)
            cnt: Number of trends to process (top by score)
            overwrite: Whether to overwrite existing files
            
        Returns:
            Number of articles generated
        """
        # Validate inputs
        try:
            InputValidator.validate_category(category)
            InputValidator.validate_feed_date(feed_date)
        except ValidationError as e:
            self.logger.error(f"Validation failed: {str(e)}")
            return 0
        
        # Sanitize category for path
        safe_category = InputValidator.sanitize_path(category)
        
        # CORRECTED PATH: {base}/{feed_date}/{category}.json
        input_path = Path(
            self.config.get('tech-trend-analysis.analysis-report')
        ) / feed_date / f"{safe_category}.json"
        
        # Validate file exists
        try:
            InputValidator.validate_file_exists(input_path, "Input file")
        except ValidationError as e:
            self.logger.warning(str(e))
            return 0
        
        # Load and validate JSON
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            InputValidator.validate_json_schema(data)
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {input_path}: {str(e)}")
            return 0
        except ValidationError as e:
            self.logger.error(f"Schema validation failed: {str(e)}")
            return 0
        
        trends = data.get('trends', [])
        
        # Sort by score descending and limit if cnt specified
        if trends:
            trends = sorted(
                trends,
                key=lambda x: x.get('score', 0),
                reverse=True
            )
            if cnt is not None:
                if cnt <= 0:
                    self.logger.warning(f"Invalid cnt value: {cnt}")
                    return 0
                trends = trends[:cnt]
        
        self.logger.info(
            f"Processing {len(trends)} trends for {category}"
        )
        
        articles_generated = 0
        
        for trend in trends:
            try:
                if self._process_trend(
                    trend,
                    safe_category,
                    feed_date,
                    overwrite
                ):
                    articles_generated += 1
            except Exception as e:
                self.logger.error(
                    f"Failed to process trend {trend.get('topic')}: {str(e)}"
                )
        
        self.logger.info(
            f"Completed {category}: {articles_generated} articles generated"
        )
        
        return articles_generated
    
    def _process_trend(
        self,
        trend: Dict[str, Any],
        category: str,
        feed_date: str,
        overwrite: bool
    ) -> bool:
        """
        Process single trend with context validation.
        
        Args:
            trend: Trend data
            category: Category name
            feed_date: Feed date
            overwrite: Whether to overwrite existing files
            
        Returns:
            True if article generated, False if skipped
        """
        topic = trend.get('topic', '')
        reason = trend.get('reason', '')
        search_keywords = trend.get('search_keywords', [])
        
        # Construct output path
        output_dir = Path(
            self.config.get('article-generator.tech-trend-article')
        ) / feed_date / category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{slugify(topic)}.md"
        
        # Check if file exists
        if output_path.exists() and not overwrite:
            self.logger.debug(
                f"Skipping existing article: {output_path}"
            )
            return False
        
        self.logger.info(f"Generating article for: {topic}")
        
        # Retrieve context from RAG
        context = self.rag_retriever.retrieve(
            search_keywords=search_keywords,
            category=category,
            feed_date=feed_date,
            k_top=self.config.get('rag.ktop', 20)
        )
        
        # Warn if no context retrieved
        if not context:
            self.logger.warning(
                f"No RAG context retrieved for '{topic}'. "
                f"Article quality may be poor."
            )
            # Optional: Skip article generation if no context
            # return False
        
        # Prepare prompts
        system_prompt = self.system_prompt_template
        user_prompt = self._inject_prompt_variables(
            template=self.user_prompt_template,
            context=context,
            search_keywords=search_keywords,
            reason=reason
        )
        
        # Generate article
        article = self.llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7
        )
        
        # Save article
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(article)
        
        self.logger.info(f"Article saved: {output_path}")
        
        return True
    
    def discover_categories(self, feed_date: str) -> List[str]:
        """
        Discover all categories for a feed date.
        
        CORRECTED: Looks for {category}.json files directly in feed_date folder.
        
        Args:
            feed_date: Feed date (YYYY-MM-DD)
            
        Returns:
            List of category names
        """
        base_path = Path(
            self.config.get('tech-trend-analysis.analysis-report')
        ) / feed_date
        
        self.logger.debug(f"Looking for categories in: {base_path}")
        self.logger.debug(f"Base path exists: {base_path.exists()}")
        
        if not base_path.exists():
            self.logger.warning(
                f"Feed date directory not found: {base_path}"
            )
            # List what's actually in the parent directory
            parent = base_path.parent
            if parent.exists():
                available_dates = [
                    d.name for d in parent.iterdir() 
                    if d.is_dir()
                ]
                self.logger.info(
                    f"Available feed dates in {parent}: {available_dates}"
                )
            return []
        
        # List all JSON files in base_path
        json_files = list(base_path.glob('*.json'))
        self.logger.debug(
            f"JSON files in {base_path}: {[f.name for f in json_files]}"
        )
        
        categories = []
        for json_file in json_files:
            # Category name is the filename without .json extension
            category_name = json_file.stem
            
            self.logger.debug(f"Found category file: {json_file.name}")
            
            # Validate it has the expected JSON structure
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if it has required fields
                if 'category' in data and 'trends' in data:
                    categories.append(category_name)
                    self.logger.debug(
                        f"Added category: {category_name} "
                        f"({len(data.get('trends', []))} trends)"
                    )
                else:
                    self.logger.warning(
                        f"File {json_file.name} missing required fields "
                        f"('category' and/or 'trends')"
                    )
            
            except json.JSONDecodeError as e:
                self.logger.warning(
                    f"Invalid JSON in {json_file.name}: {str(e)}"
                )
            except Exception as e:
                self.logger.warning(
                    f"Error reading {json_file.name}: {str(e)}"
                )
        
        if not categories:
            self.logger.warning(
                f"No valid category JSON files found in {base_path}"
            )
            self.logger.info(
                f"Expected structure: {base_path}/{{category_name}}.json"
            )
        
        return categories