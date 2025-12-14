"""
OpenAI image generation provider.
"""
import base64
from pathlib import Path
from typing import Dict, Any

import requests

from .base import BaseLLMProvider
from ..exceptions import LLMProviderError


class OpenAIProvider(BaseLLMProvider):
    """OpenAI DALL-E image generation provider."""
    
    API_URL = "https://api.openai.com/v1/images/generations"
    
    def __init__(
        self,
        api_key: str,
        model: str,
        config: Dict[str, Any]
    ):
        """Initialize OpenAI provider."""
        super().__init__(api_key, model, config)
        self.timeout = config.get('timeout', 60)
    
    def generate_image(
        self,
        prompt: str,
        output_path: Path
    ) -> None:
        """
        Generate image using OpenAI DALL-E API.
        
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
        
        size = self._get_size()
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "n": 1,
            "size": size,
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
            raise LLMProviderError(f"OpenAI API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise LLMProviderError(f"Invalid OpenAI API response: {e}")
        except Exception as e:
            raise LLMProviderError(f"OpenAI image generation failed: {e}")
    
    def _get_size(self) -> str:
        """Get image size based on aspect ratio."""
        aspect_ratio = self.config.get('aspect-ratio', '1:1')
        size_map = {
            '1:1': '1024x1024',
            'square': '1024x1024',
            'wide': '1792x1024',
            'tall': '1024x1792'
        }
        return size_map.get(aspect_ratio, '1024x1024')
