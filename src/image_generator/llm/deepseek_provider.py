"""
DeepSeek image generation provider.
"""
import base64
from pathlib import Path
from typing import Dict, Any

import requests

from .base import BaseLLMProvider
from ..exceptions import LLMProviderError


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek image generation provider."""
    
    API_URL = "https://api.deepseek.com/v1/images/generations"
    
    def __init__(
        self,
        api_key: str,
        model: str,
        config: Dict[str, Any]
    ):
        """Initialize DeepSeek provider."""
        super().__init__(api_key, model, config)
        self.timeout = config.get('timeout', 60)
    
    def generate_image(
        self,
        prompt: str,
        output_path: Path
    ) -> None:
        """
        Generate image using DeepSeek API.
        
        Args:
            prompt: Text prompt for image generation
            output_path: Path to save generated image
            
        Raises:
            LLMProviderError: If image generation fails
        """
        full_prompt = self._build_full_prompt(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "n": 1,
            "size": self._get_size(),
            "response_format": "b64_json"
        }
        
        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            image_b64 = data['data'][0]['b64_json']
            image_data = base64.b64decode(image_b64)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(image_data)
            
        except requests.exceptions.RequestException as e:
            raise LLMProviderError(f"DeepSeek API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise LLMProviderError(f"Invalid DeepSeek API response: {e}")
        except Exception as e:
            raise LLMProviderError(f"DeepSeek image generation failed: {e}")
    
    def _get_size(self) -> str:
        """Get image size based on configuration."""
        default_size = self.config.get('default-size', 1024)
        return f"{default_size}x{default_size}"
