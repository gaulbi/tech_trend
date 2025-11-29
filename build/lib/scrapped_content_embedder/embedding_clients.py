"""
Embedding client abstraction and factory.

Provides abstract base class and factory pattern for multiple embedding providers.
"""

from abc import ABC, abstractmethod
from typing import List
import time
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class EmbeddingClient(ABC):
    """Abstract base class for embedding clients."""
    
    def __init__(self, model_name: str, timeout: int = 60):
        """
        Initialize embedding client.
        
        Args:
            model_name: Name of the embedding model
            timeout: Timeout for API calls in seconds
        """
        self.model_name = model_name
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            Exception: If embedding fails after retries
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Embedding dimension
        """
        pass
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """
        Execute function with exponential backoff retry logic.
        
        Retries: 3 attempts with delays of 1s, 3s, 5s
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries fail
        """
        delays = [1, 3, 5]  # Exponential backoff delays as specified
        last_exception = None
        
        for attempt, delay in enumerate(delays, 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt == len(delays):
                    self.logger.error(
                        f"All {len(delays)} retry attempts failed: {str(e)}",
                        exc_info=True
                    )
                    raise
                self.logger.warning(
                    f"Attempt {attempt}/{len(delays)} failed: {str(e)}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
        
        # This should never be reached, but for safety
        if last_exception:
            raise last_exception


class OpenAIEmbeddingClient(EmbeddingClient):
    """OpenAI embedding client implementation."""
    
    def __init__(self, model_name: str = "text-embedding-3-small", timeout: int = 60):
        """
        Initialize OpenAI embedding client.
        
        Args:
            model_name: OpenAI embedding model name
            timeout: API call timeout in seconds
            
        Raises:
            ValueError: If OPENAI_API_KEY not found in environment
            ImportError: If openai package not installed
        """
        super().__init__(model_name, timeout)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, timeout=timeout)
            self.logger.info(f"Initialized OpenAI client with model: {model_name}")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        def _embed():
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts,
                timeout=self.timeout
            )
            return [item.embedding for item in response.data]
        
        return self._retry_with_backoff(_embed)
    
    def get_dimension(self) -> int:
        """Get embedding dimension for OpenAI models."""
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        return dimensions.get(self.model_name, 1536)


class VoyageAIEmbeddingClient(EmbeddingClient):
    """Voyage AI embedding client implementation."""
    
    def __init__(self, model_name: str = "voyage-2", timeout: int = 60):
        """
        Initialize Voyage AI embedding client.
        
        Args:
            model_name: Voyage AI model name
            timeout: API call timeout in seconds
            
        Raises:
            ValueError: If VOYAGE_API_KEY not found in environment
            ImportError: If voyageai package not installed
        """
        super().__init__(model_name, timeout)
        api_key = os.getenv("VOYAGE_API_KEY")
        if not api_key:
            raise ValueError("VOYAGE_API_KEY not found in environment variables")
        
        try:
            import voyageai
            self.client = voyageai.Client(api_key=api_key)
            self.logger.info(f"Initialized Voyage AI client with model: {model_name}")
        except ImportError:
            raise ImportError("voyageai package not installed. Run: pip install voyageai")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Voyage AI API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        def _embed():
            response = self.client.embed(
                texts=texts,
                model=self.model_name,
                truncation=True
            )
            return response.embeddings
        
        return self._retry_with_backoff(_embed)
    
    def get_dimension(self) -> int:
        """Get embedding dimension for Voyage AI models."""
        dimensions = {
            "voyage-2": 1024,
            "voyage-large-2": 1536,
            "voyage-code-2": 1536,
            "voyage-lite-02-instruct": 1024
        }
        return dimensions.get(self.model_name, 1024)


class GeminiEmbeddingClient(EmbeddingClient):
    """Google Gemini embedding client implementation."""
    
    def __init__(self, model_name: str = "models/embedding-001", timeout: int = 60):
        """
        Initialize Gemini embedding client.
        
        Args:
            model_name: Gemini model name
            timeout: API call timeout in seconds
            
        Raises:
            ValueError: If GOOGLE_API_KEY not found in environment
            ImportError: If google-generativeai package not installed
        """
        super().__init__(model_name, timeout)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
            self.logger.info(f"Initialized Gemini client with model: {model_name}")
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Run: pip install google-generativeai"
            )
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Gemini API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        def _embed():
            embeddings = []
            for text in texts:
                result = self.genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            return embeddings
        
        return self._retry_with_backoff(_embed)
    
    def get_dimension(self) -> int:
        """Get embedding dimension for Gemini models."""
        return 768


class SentenceTransformerClient(EmbeddingClient):
    """Local Sentence Transformers embedding client."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", timeout: int = 60):
        """
        Initialize Sentence Transformers client.
        
        Args:
            model_name: HuggingFace model name
            timeout: Not used for local models, kept for interface compatibility
            
        Raises:
            ImportError: If sentence-transformers package not installed
        """
        super().__init__(model_name, timeout)
        
        try:
            from sentence_transformers import SentenceTransformer
            self.logger.info(f"Loading Sentence Transformer model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.logger.info(f"Model loaded successfully - dimension: {self.get_dimension()}")
        except ImportError:
            raise ImportError(
                "sentence-transformers package not installed. "
                "Run: pip install sentence-transformers"
            )
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using local Sentence Transformers.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        def _embed():
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return embeddings.tolist()
        
        # Local models don't need retry logic, but we use it for consistency
        return self._retry_with_backoff(_embed)
    
    def get_dimension(self) -> int:
        """Get embedding dimension from the model."""
        return self.model.get_sentence_embedding_dimension()


class EmbeddingClientFactory:
    """Factory for creating embedding clients based on provider."""
    
    _SUPPORTED_PROVIDERS = {
        "openai": OpenAIEmbeddingClient,
        "voyage": VoyageAIEmbeddingClient,
        "voyageai": VoyageAIEmbeddingClient,
        "gemini": GeminiEmbeddingClient,
        "sentence-transformers": SentenceTransformerClient,
        "local": SentenceTransformerClient
    }
    
    @classmethod
    def create_client(
        cls,
        provider: str,
        model_name: str,
        timeout: int = 60
    ) -> EmbeddingClient:
        """
        Create an embedding client based on provider.
        
        Args:
            provider: Provider name (openai, voyage, gemini, sentence-transformers)
            model_name: Model name specific to the provider
            timeout: Timeout for API calls in seconds
            
        Returns:
            EmbeddingClient instance
            
        Raises:
            ValueError: If provider is not supported
        """
        provider_lower = provider.lower()
        
        if provider_lower not in cls._SUPPORTED_PROVIDERS:
            supported = ", ".join(cls._SUPPORTED_PROVIDERS.keys())
            raise ValueError(
                f"Unsupported provider: '{provider}'. "
                f"Supported providers: {supported}"
            )
        
        client_class = cls._SUPPORTED_PROVIDERS[provider_lower]
        
        try:
            client = client_class(model_name=model_name, timeout=timeout)
            logging.getLogger(__name__).info(
                f"Created {provider} embedding client with model: {model_name}"
            )
            return client
        except (ValueError, ImportError) as e:
            logging.getLogger(__name__).error(
                f"Failed to create {provider} client: {str(e)}"
            )
            raise
    
    @classmethod
    def list_supported_providers(cls) -> List[str]:
        """
        Get list of supported embedding providers.
        
        Returns:
            List of provider names
        """
        return list(cls._SUPPORTED_PROVIDERS.keys())