"""
Google Gemini image generation provider.
"""
import time
import base64
import requests
from pathlib import Path
from typing import Optional

from .base import BaseLLMProvider
from ..exceptions import LLMProviderError, NetworkError, ConfigurationError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini image generation provider."""
    
    def validate_config(self) -> bool:
        """Validate Gemini configuration."""
        if not self.api_key:
            raise ConfigurationError("Gemini API key is missing")
        return True
    
    def _get_api_url(self) -> str:
        """Get API URL for the model."""
        return (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self.model}:generateContent?key={self.api_key}"
        )
    
    def generate_image(
        self,
        prompt: str,
        output_path: Path,
        size: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        output_format: str = "jpg"
    ) -> Path:
        """Generate image using Gemini."""
        self.validate_config()
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Gemini expects simple text prompt for image generation
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 4096,
            }
        }
        
        last_error = None
        for attempt in range(self.retry):
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
                
            except requests.Timeout as e:
                last_error = NetworkError(f"Request timeout: {e}")
                if attempt < self.retry - 1:
                    time.sleep(2 ** attempt)
                    
            except NetworkError as e:
                last_error = e
                if attempt < self.retry - 1:
                    time.sleep(2 ** attempt)
                    
            except requests.RequestException as e:
                error_msg = f"Request failed: {e}"
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_data = e.response.json()
                        error_msg += f" - {error_data}"
                    except:
                        error_msg += f" - Status: {e.response.status_code}"
                last_error = NetworkError(error_msg)
                if attempt < self.retry - 1:
                    time.sleep(2 ** attempt)
                    
            except Exception as e:
                last_error = LLMProviderError(f"Unexpected error: {e}")
                if attempt < self.retry - 1:
                    time.sleep(2 ** attempt)
        
        raise last_error
