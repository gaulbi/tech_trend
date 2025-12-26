"""
Abstract base class for LLM image generation providers.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any


class BaseLLMProvider(ABC):
    """Abstract base class for LLM image generation providers."""
    
    def __init__(
        self,
        api_key: str,
        model: str,
        config: Dict[str, Any]
    ):
        """
        Initialize LLM provider.
        
        Args:
            api_key: API key for the provider
            model: Model name to use
            config: Configuration dictionary
        """
        self.api_key = api_key
        self.model = model
        self.config = config
    
    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        output_path: Path
    ) -> None:
        """
        Generate image from prompt and save to output path.
        
        Args:
            prompt: Text prompt for image generation
            output_path: Path to save generated image
            
        Raises:
            LLMProviderError: If image generation fails
        """
        pass
    
    def _build_full_prompt(self, summary: str) -> str:
        """
        Build full prompt with style instructions.
        
        Args:
            summary: Article summary text
            
        Returns:
            Complete prompt for image generation
        """
        style_instruction = self.config.get('style-instruction', '')
        return f"{style_instruction}\n\n{summary}"
