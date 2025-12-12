"""
Abstract base class for LLM providers.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM image generation providers."""
    
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int = 60,
        retry: int = 3
    ):
        """
        Initialize LLM provider.
        
        Args:
            api_key: API key for the provider
            model: Model name to use
            timeout: Request timeout in seconds
            retry: Number of retry attempts
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.retry = retry
    
    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        output_path: Path,
        size: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        output_format: str = "jpg"
    ) -> Path:
        """
        Generate image from prompt.
        
        Args:
            prompt: Text prompt for image generation
            output_path: Path to save generated image
            size: Image size (if supported)
            aspect_ratio: Aspect ratio (if supported)
            output_format: Output format
            
        Returns:
            Path to saved image
            
        Raises:
            LLMProviderError: If generation fails
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate provider configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass
