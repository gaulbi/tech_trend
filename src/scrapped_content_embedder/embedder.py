"""
Main embedder module for processing scraped content.

Handles reading, chunking, embedding, and storing scraped content in ChromaDB.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
import chromadb
from chromadb.config import Settings

from .config import Config
from .embedding_clients import EmbeddingClientFactory


class ScrapedContentEmbedder:
    """Main class for embedding scraped content into ChromaDB."""
    
    def __init__(self, config: Config):
        """
        Initialize the embedder.
        
        Args:
            config: Configuration object
            
        Raises:
            ImportError: If required packages not installed
            ValueError: If configuration is invalid
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Validate configuration
        self._validate_config()
        
        # Initialize embedding client
        self.embedding_client = EmbeddingClientFactory.create_client(
            provider=config.embedding.embedding_provider,
            model_name=config.embedding.embedding_model,
            timeout=config.embedding.timeout
        )
        
        # Initialize ChromaDB
        self._init_chromadb()
        
        # Initialize text splitter
        self._init_text_splitter()
        
    def _validate_config(self) -> None:
        """
        Validate configuration parameters.
        
        Raises:
            ValueError: If configuration parameters are invalid
        """
        if self.config.embedding.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        
        if self.config.embedding.chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        
        if self.config.embedding.chunk_overlap >= self.config.embedding.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        
        if self.config.embedding.timeout <= 0:
            raise ValueError("timeout must be positive")
        
        self.logger.info("Configuration validated successfully")
    
    def _init_chromadb(self) -> None:
        """
        Initialize ChromaDB client and ensure database directory exists.
        
        Raises:
            OSError: If database directory cannot be created
        """
        try:
            db_path = self.config.embedding.database_path
            db_path.mkdir(parents=True, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            self.logger.info(f"ChromaDB initialized at {db_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    def _init_text_splitter(self) -> None:
        """
        Initialize text splitter for chunking using LangChain.
        
        Raises:
            ImportError: If langchain-text-splitters package not installed
        """
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.embedding.chunk_size,
                chunk_overlap=self.config.embedding.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""],
                keep_separator=False
            )
            self.logger.info(
                f"Text splitter initialized - chunk_size: {self.config.embedding.chunk_size}, "
                f"overlap: {self.config.embedding.chunk_overlap}"
            )
        except ImportError:
            self.logger.error("langchain-text-splitters package not installed")
            raise ImportError(
                "langchain-text-splitters package not installed. "
                "Run: pip install langchain-text-splitters"
            )
    
    def _normalize_category(self, category: str) -> str:
        """
        Convert category to normalized format for database name.
        
        Args:
            category: Original category string (e.g., "AI Chips / AI Hardware")
            
        Returns:
            Normalized category string (e.g., "ai-chips-ai-hardware")
        """
        normalized = category.lower()
        # Replace common separators with hyphens
        for char in [" ", "/", "_", "\\", "|"]:
            normalized = normalized.replace(char, "-")
        # Remove multiple consecutive hyphens
        while "--" in normalized:
            normalized = normalized.replace("--", "-")
        # Remove leading/trailing hyphens
        normalized = normalized.strip("-")
        return normalized
    
    def _get_or_create_collection(self, category: str) -> Any:
        """
        Get or create a ChromaDB collection for a category.
        
        Args:
            category: Category name
            
        Returns:
            ChromaDB collection object
            
        Raises:
            Exception: If collection creation fails
        """
        collection_name = self._normalize_category(category)
        
        try:
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self.logger.info(f"Using collection: {collection_name}")
            return collection
        except Exception as e:
            self.logger.error(
                f"Failed to create/get collection '{collection_name}': {str(e)}"
            )
            raise
    
    def _generate_document_id(
        self,
        source_file: str,
        category: str,
        trend_index: int,
        chunk_index: int
    ) -> str:
        """
        Generate unique document ID following the specified format.
        
        Format: {normalized_category}_{base_filename}_{trend_idx}_{chunk_idx}
        
        Args:
            source_file: Source filename
            category: Category name
            trend_index: Index of the trend in the file
            chunk_index: Index of the chunk within the trend
            
        Returns:
            Unique document ID
        """
        base_name = Path(source_file).stem
        normalized_category = self._normalize_category(category)
        return f"{normalized_category}_{base_name}_t{trend_index}_chunk_{chunk_index}"
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks using LangChain's text splitter.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        try:
            chunks = self.text_splitter.split_text(text)
            return [chunk.strip() for chunk in chunks if chunk.strip()]
        except Exception as e:
            self.logger.error(f"Error chunking text: {str(e)}")
            # Fallback: return original text as single chunk
            return [text.strip()] if text.strip() else []
    
    def _read_json_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Safely read and parse JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            json.JSONDecodeError: If JSON is malformed
            FileNotFoundError: If file doesn't exist
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error in {file_path}: {str(e)}")
            raise
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
    
    def _process_trend(
        self,
        trend: Dict[str, Any],
        trend_index: int,
        source_file: str,
        category: str,
        embedding_date: str,
        collection: Any
    ) -> Tuple[int, int, List[str]]:
        """
        Process a single trend (article) from scraped content.
        
        Args:
            trend: Trend dictionary containing content, link, topic
            trend_index: Index of this trend in the file
            source_file: Source filename
            category: Category name
            embedding_date: Date of embedding (YYYY-MM-DD)
            collection: ChromaDB collection
            
        Returns:
            Tuple of (chunks_created, documents_embedded, errors)
        """
        chunks_created = 0
        documents_embedded = 0
        errors = []
        
        try:
            # Skip if content is missing or has error
            content = trend.get('content', '')
            if not content or trend.get('error'):
                if trend.get('error'):
                    self.logger.debug(
                        f"Skipping trend with error: {trend.get('error')}"
                    )
                return chunks_created, documents_embedded, errors
            
            # Chunk the content
            chunks = self._chunk_text(content)
            if not chunks:
                return chunks_created, documents_embedded, errors
            
            chunks_created = len(chunks)
            
            # Prepare data for batch embedding
            documents = []
            metadatas = []
            ids = []
            
            for chunk_idx, chunk in enumerate(chunks):
                doc_id = self._generate_document_id(
                    source_file,
                    category,
                    trend_index,
                    chunk_idx
                )
                
                metadata = {
                    'url': trend.get('link', ''),
                    'source_file': source_file,
                    'category': category,
                    'one_word_category': self._normalize_category(category),
                    'embedding_date': embedding_date,
                    'chunk_index': chunk_idx,
                    'total_chunks': len(chunks),
                    'topic': trend.get('topic', '')[:500]  # Limit topic length
                }
                
                documents.append(chunk)
                metadatas.append(metadata)
                ids.append(doc_id)
            
            # Generate embeddings in batch
            try:
                embeddings = self.embedding_client.embed_texts(documents)
                
                # Upsert to ChromaDB
                collection.upsert(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
                
                documents_embedded = len(documents)
                topic_preview = trend.get('topic', 'N/A')[:60]
                self.logger.info(
                    f"✓ Embedded {len(documents)} chunks from: {topic_preview}"
                )
                
            except Exception as e:
                error_msg = f"Embedding failed for trend '{trend.get('topic', 'N/A')[:50]}': {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                
        except Exception as e:
            error_msg = f"Error processing trend {trend_index}: {str(e)}"
            self.logger.error(error_msg)
            errors.append(error_msg)
        
        return chunks_created, documents_embedded, errors
    
    def _process_scraped_file(
        self,
        file_path: Path,
        category: str,
        embedding_date: str
    ) -> Dict[str, Any]:
        """
        Process a single scraped content file.
        
        Args:
            file_path: Path to the scraped content file
            category: Category of the content
            embedding_date: Date of embedding (YYYY-MM-DD)
            
        Returns:
            Processing results dictionary with counts and errors
        """
        results = {
            'file': str(file_path.name),
            'chunks_created': 0,
            'documents_embedded': 0,
            'trends_processed': 0,
            'trends_skipped': 0,
            'errors': []
        }
        
        try:
            # Read and parse JSON file
            data = self._read_json_file(file_path)
            
            source_file = data.get('source_file', file_path.name)
            trends = data.get('trends', [])
            
            if not trends:
                self.logger.warning(f"No trends found in {file_path.name}")
                results['errors'].append(f"No trends in {file_path.name}")
                return results
            
            self.logger.info(
                f"Processing {len(trends)} trends from {file_path.name}"
            )
            
            # Get or create collection for this category
            collection = self._get_or_create_collection(category)
            
            # Process each trend
            for trend_idx, trend in enumerate(trends):
                chunks, docs, errors = self._process_trend(
                    trend=trend,
                    trend_index=trend_idx,
                    source_file=source_file,
                    category=category,
                    embedding_date=embedding_date,
                    collection=collection
                )
                
                results['chunks_created'] += chunks
                results['documents_embedded'] += docs
                results['errors'].extend(errors)
                
                if docs > 0:
                    results['trends_processed'] += 1
                else:
                    results['trends_skipped'] += 1
            
            self.logger.info(
                f"Completed {file_path.name}: {results['trends_processed']} trends, "
                f"{results['documents_embedded']} documents embedded"
            )
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in {file_path.name}: {str(e)}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
        except Exception as e:
            error_msg = f"Fatal error processing {file_path.name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            results['errors'].append(error_msg)
        
        return results
    
    def process_today_content(self) -> Dict[str, Any]:
        """
        Process all scraped content files from today's directory.
        
        Expected structure:
        {base_path}/{YYYY-MM-DD}/{category}/*.json
        
        Returns:
            Summary dictionary with processing statistics and errors
        """
        today = datetime.now().strftime("%Y-%m-%d")
        base_path = self.config.scrape.url_scrapped_content / today
        
        self.logger.info("="*80)
        self.logger.info(f"Starting embedding process for date: {today}")
        self.logger.info(f"Scanning directory: {base_path}")
        self.logger.info("="*80)
        
        # Initialize results summary
        results = {
            'execution_date': today,
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'successful_embeddings': 0,
            'failed_embeddings': 0,
            'total_chunks': 0,
            'total_documents': 0,
            'categories_processed': {},
            'errors': []
        }
        
        # Check if today's directory exists
        if not base_path.exists():
            error_msg = f"No content directory found for {today}: {base_path}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
        
        # Find all category directories
        category_dirs = [d for d in base_path.iterdir() if d.is_dir()]
        
        if not category_dirs:
            error_msg = f"No category directories found in {base_path}"
            self.logger.warning(error_msg)
            results['errors'].append(error_msg)
            return results
        
        self.logger.info(f"Found {len(category_dirs)} category directories")
        
        # Process each category directory
        for category_dir in sorted(category_dirs):
            category = category_dir.name
            self.logger.info(f"\n{'─'*80}")
            self.logger.info(f"Processing category: {category}")
            self.logger.info(f"{'─'*80}")
            
            # Find all JSON files in category directory
            json_files = list(category_dir.glob("*.json"))
            
            if not json_files:
                warning_msg = f"No JSON files found in {category_dir}"
                self.logger.warning(warning_msg)
                continue
            
            self.logger.info(f"Found {len(json_files)} JSON files")
            
            category_docs = 0
            
            # Process each JSON file
            for json_file in sorted(json_files):
                results['total_files'] += 1
                self.logger.info(f"\n📄 Processing: {json_file.name}")
                
                try:
                    file_results = self._process_scraped_file(
                        file_path=json_file,
                        category=category,
                        embedding_date=today
                    )
                    
                    # Aggregate results
                    results['total_chunks'] += file_results['chunks_created']
                    results['total_documents'] += file_results['documents_embedded']
                    category_docs += file_results['documents_embedded']
                    
                    if file_results['errors']:
                        results['failed_files'] += 1
                        results['errors'].extend(file_results['errors'])
                    else:
                        results['successful_files'] += 1
                    
                    # Track embedding success
                    if file_results['documents_embedded'] > 0:
                        results['successful_embeddings'] += 1
                    else:
                        results['failed_embeddings'] += 1
                    
                except Exception as e:
                    error_msg = f"Fatal error processing {json_file.name}: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    results['failed_files'] += 1
                    results['failed_embeddings'] += 1
                    results['errors'].append(error_msg)
            
            # Record category statistics
            if category_docs > 0:
                results['categories_processed'][category] = category_docs
                self.logger.info(
                    f"✓ Category '{category}' complete: {category_docs} documents embedded"
                )
        
        self.logger.info("\n" + "="*80)
        self.logger.info("Embedding process completed")
        self.logger.info("="*80)
        
        return results