"""Factory pattern implementation for LLM and Embedding clients."""

import os
import time
from abc import ABC, abstractmethod
from typing import List, Optional

import openai


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
    
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text using the LLM.
        
        Args:
            system_prompt: System-level instructions
            user_prompt: User query/content
            
        Returns:
            Generated text response
        """
        pass
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry logic."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                time.sleep(wait_time)


class OpenAILLMClient(BaseLLMClient):
    """OpenAI LLM client implementation."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        super().__init__(model, timeout, max_retries)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.client = openai.OpenAI(api_key=api_key, timeout=timeout)
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate using OpenAI API."""
        def _call():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        
        return self._retry_with_backoff(_call)


class DeepSeekLLMClient(BaseLLMClient):
    """DeepSeek LLM client implementation."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        super().__init__(model, timeout, max_retries)
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment")
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=timeout
        )
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate using DeepSeek API."""
        def _call():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        
        return self._retry_with_backoff(_call)


class ClaudeLLMClient(BaseLLMClient):
    """Anthropic Claude LLM client implementation."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        super().__init__(model, timeout, max_retries)
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY not found in environment")
        
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required for Claude. "
                "Install: pip install anthropic"
            )
        
        self.client = Anthropic(api_key=api_key, timeout=timeout)
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate using Claude API."""
        def _call():
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        
        return self._retry_with_backoff(_call)


class OllamaLLMClient(BaseLLMClient):
    """Ollama local LLM client implementation."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        super().__init__(model, timeout, max_retries)
        self.client = openai.OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            timeout=timeout
        )
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate using Ollama API."""
        def _call():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        
        return self._retry_with_backoff(_call)


class LLMFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create(
        provider: str, model: str, timeout: int, max_retries: int
    ) -> BaseLLMClient:
        """Create LLM client based on provider.
        
        Args:
            provider: Provider name (openai, deepseek, claude, ollama)
            model: Model identifier
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            
        Returns:
            Configured LLM client instance
        """
        providers = {
            "openai": OpenAILLMClient,
            "deepseek": DeepSeekLLMClient,
            "claude": ClaudeLLMClient,
            "ollama": OllamaLLMClient,
        }
        
        provider_lower = provider.lower()
        if provider_lower not in providers:
            raise ValueError(f"Unknown LLM provider: {provider}")
        
        return providers[provider_lower](model, timeout, max_retries)


class BaseEmbeddingClient(ABC):
    """Abstract base class for embedding clients."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate embeddings for text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
        """
        pass
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry logic."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                time.sleep(wait_time)


class OpenAIEmbeddingClient(BaseEmbeddingClient):
    """OpenAI embedding client implementation."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        super().__init__(model, timeout, max_retries)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.client = openai.OpenAI(api_key=api_key, timeout=timeout)
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI."""
        def _call():
            response = self.client.embeddings.create(
                model=self.model, input=text
            )
            return response.data[0].embedding
        
        return self._retry_with_backoff(_call)


class VoyageAIEmbeddingClient(BaseEmbeddingClient):
    """VoyageAI embedding client implementation."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        super().__init__(model, timeout, max_retries)
        api_key = os.getenv("VOYAGEAI_API_KEY")
        if not api_key:
            raise ValueError("VOYAGEAI_API_KEY not found in environment")
        
        try:
            import voyageai
        except ImportError:
            raise ImportError(
                "voyageai package required for VoyageAI. "
                "Install: pip install voyageai"
            )
        
        self.client = voyageai.Client(api_key=api_key)
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings using VoyageAI."""
        def _call():
            response = self.client.embed(
                texts=[text], model=self.model
            )
            return response.embeddings[0]
        
        return self._retry_with_backoff(_call)


class GeminiEmbeddingClient(BaseEmbeddingClient):
    """Google Gemini embedding client implementation."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        super().__init__(model, timeout, max_retries)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai package required for Gemini. "
                "Install: pip install google-generativeai"
            )
        
        genai.configure(api_key=api_key)
        self.genai = genai
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings using Gemini."""
        def _call():
            result = self.genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        
        return self._retry_with_backoff(_call)


class SentenceTransformersEmbeddingClient(BaseEmbeddingClient):
    """Local sentence-transformers embedding client."""
    
    def __init__(self, model: str, timeout: int, max_retries: int):
        super().__init__(model, timeout, max_retries)
        
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers package required. "
                "Install: pip install sentence-transformers"
            )
        
        self.model_instance = SentenceTransformer(model)
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings using sentence-transformers."""
        embedding = self.model_instance.encode(text)
        return embedding.tolist()


class EmbeddingFactory:
    """Factory for creating embedding clients."""
    
    @staticmethod
    def create(
        provider: str, model: str, timeout: int, max_retries: int
    ) -> BaseEmbeddingClient:
        """Create embedding client based on provider.
        
        Args:
            provider: Provider name
            model: Model identifier
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            
        Returns:
            Configured embedding client instance
        """
        providers = {
            "openai": OpenAIEmbeddingClient,
            "voyageai": VoyageAIEmbeddingClient,
            "gemini": GeminiEmbeddingClient,
            "sentence-transformers": SentenceTransformersEmbeddingClient,
        }
        
        provider_lower = provider.lower()
        if provider_lower not in providers:
            raise ValueError(f"Unknown embedding provider: {provider}")
        
        return providers[provider_lower](model, timeout, max_retries)