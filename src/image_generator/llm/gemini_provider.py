"""
Google Gemini image generation provider.
"""
from pathlib import Path
from typing import Dict, Any
import base64
import requests

from .base import BaseLLMProvider
from ..exceptions import LLMProviderError, NetworkError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini image generation provider."""
    
    #API_URL = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict"
        
    def __init__(
        self,
        api_key: str,
        model: str,
        config: Dict[str, Any]
    ):
        """Initialize Gemini provider."""
        super().__init__(api_key, model, config)
        self.timeout = config.get('timeout', 60)

    def _get_api_url(self) -> str:
        """Get API URL for the model."""
        return (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self.model}:generateContent?key={self.api_key}"
        )
    
    def generate_image(
        self,
        prompt: str,
        output_path: Path
    ) -> None:
        """
        Generate image using Google Gemini API.
        
        Args:
            prompt: Text prompt for image generation
            output_path: Path to save generated image
            
        Raises:
            LLMProviderError: If image generation fails
        """
        full_prompt = self._build_full_prompt(prompt)
                
        headers = {
            "Content-Type": "application/json"
        }
        
        # Gemini expects simple text prompt for image generation
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 4096,
            }
        }

        try:
            response = requests.post(
                self._get_api_url(),
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            # Get detailed error info
            if not response.ok:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = f" - {error_data}"
                except:
                    error_detail = f" - {response.text}"
                raise NetworkError(
                    f"HTTP {response.status_code}{error_detail}"
                )

            response.raise_for_status()
            data = response.json()

            # Extract image from response with safe access
            if 'candidates' not in data or len(data['candidates']) == 0:
                raise LLMProviderError("No candidates in response")
            
            candidate = data['candidates'][0]
            
            if 'content' not in candidate:
                raise LLMProviderError("No content in candidate")
            
            if 'parts' not in candidate['content']:
                raise LLMProviderError("No parts in content")
            
            parts = candidate['content']['parts']
            
            for part in parts:
                if 'inlineData' in part:
                    mime_type = part['inlineData']['mimeType']
                    image_data = part['inlineData']['data']
                    
                    # Decode base64 image
                    img_bytes = base64.b64decode(image_data)
                    
                    output_path.parent.mkdir(
                        parents=True,
                        exist_ok=True
                    )
                    output_path.write_bytes(img_bytes)
                    
                    return output_path
            
            raise LLMProviderError("No image in response")
            
        except requests.exceptions.RequestException as e:
            raise LLMProviderError(f"Gemini API request failed: {e}")
        except Exception as e:
            raise LLMProviderError(f"Gemini image generation failed: {e}")
    
    def _get_aspect_ratio(self) -> str:
        """Get aspect ratio for Gemini API."""
        aspect_ratio = self.config.get('aspect-ratio', '1:1')
        ratio_map = {
            '1:1': '1:1',
            'square': '1:1',
            'wide': '16:9',
            'tall': '9:16'
        }
        return ratio_map.get(aspect_ratio, '1:1')
