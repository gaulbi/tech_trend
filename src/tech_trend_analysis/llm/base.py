"""Base abstract class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMClient(ABC):
    """Abstract base class for LLM client implementations."""

    def __init__(
        self, 
        api_key: str, 
        model: str, 
        timeout: int, 
        retry_count: int
    ):
        """Initialize LLM client.
        
        Args:
            api_key: API key for authentication
            model: Model name to use
            timeout: Request timeout in seconds
            retry_count: Number of retry attempts
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.retry_count = retry_count

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from LLM.
        
        Args:
            prompt: Input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            LLMError: If generation fails
            NetworkError: If network request fails
        """
        pass

    def _prepare_prompt(self, template: str, context: Dict[str, Any]) -> str:
        """Prepare prompt by replacing template variables.
        
        Args:
            template: Prompt template with {{variable}} placeholders
            context: Dictionary of variable values
            
        Returns:
            Formatted prompt string
        """
        import json
        prompt = template
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            if isinstance(value, (dict, list)):
                replacement = json.dumps(value, ensure_ascii=False)
            else:
                replacement = str(value)
            prompt = prompt.replace(placeholder, replacement)
        return prompt