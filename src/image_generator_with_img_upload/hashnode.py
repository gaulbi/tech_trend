"""
Hashnode image upload module.
"""
import logging
import time
from pathlib import Path
from typing import Optional

import requests

from .exceptions import HashNodeUploadError


class HashNodeUploader:
    """Handles image uploads to Hashnode."""
    
    # GRAPHQL_MUTATION = """
    # mutation UploadImage($input: UploadImageInput!) {
    #   uploadImage(input: $input) {
    #     url
    #   }
    # }
    # """

    GRAPHQL_MUTATION = """
    mutation PublishPost($input: PostBannerImageInput!) {
      publishPost(input: $input) {
        post { 
          url
        }
      }
    }
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int,
        max_retries: int,
        logger: logging.Logger
    ):
        """
        Initialize Hashnode uploader.
        
        Args:
            api_key: Hashnode API key
            base_url: Hashnode API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            logger: Logger instance
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger
    
    def upload(self, image_path: Path) -> str:
        """
        Upload image to Hashnode with retry logic.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Hashnode CDN URL
            
        Raises:
            HashNodeUploadError: If upload fails after all retries
        """
        for attempt in range(self.max_retries):
            try:
                return self._upload_attempt(image_path)
            except requests.exceptions.Timeout:
                self._handle_retry(attempt, "Timeout")
            except requests.exceptions.ConnectionError:
                self._handle_retry(attempt, "Connection error")
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise HashNodeUploadError(f"Upload failed: {e}")
                self._handle_retry(attempt, str(e))
        
        raise HashNodeUploadError(
            f"Upload failed after {self.max_retries} attempts"
        )
    
    def _upload_attempt(self, image_path: Path) -> str:
        """
        Perform single upload attempt.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Hashnode CDN URL
            
        Raises:
            HashNodeUploadError: If upload fails
        """
        if not image_path.exists():
            raise HashNodeUploadError(f"Image file not found: {image_path}")
        
        headers = {
            "Authorization": self.api_key
        }
        
        with open(image_path, 'rb') as f:
            files = {
                'operations': (
                    None,
                    self._build_operations_json(),
                    'application/json'
                ),
                'map': (
                    None,
                    '{"0": ["variables.input.image"]}',
                    'application/json'
                ),
                '0': (image_path.name, f, self._get_mime_type(image_path))
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                files=files,
                timeout=self.timeout
            )
        
        if response.status_code == 401:
            raise HashNodeUploadError("Authentication failed - invalid API key")
        
        if response.status_code == 429:
            self.logger.warning("Rate limit hit, waiting before retry")
            time.sleep(5)
            raise requests.exceptions.RequestException("Rate limited")
        
        response.raise_for_status()
        
        return self._extract_url(response.json())
    
    def _build_operations_json(self) -> str:
        """Build GraphQL operations JSON."""
        import json
        operations = {
            "query": self.GRAPHQL_MUTATION,
            "variables": {
                "input": {
                    "image": None
                }
            }
        }
        return json.dumps(operations)
    
    def _get_mime_type(self, image_path: Path) -> str:
        """Get MIME type based on file extension."""
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp'
        }
        return mime_types.get(image_path.suffix.lower(), 'image/jpeg')
    
    def _extract_url(self, response_data: dict) -> str:
        """
        Extract CDN URL from response.
        
        Args:
            response_data: API response JSON
            
        Returns:
            CDN URL
            
        Raises:
            HashNodeUploadError: If URL cannot be extracted
        """
        try:
            return response_data['data']['uploadImage']['url']
        except (KeyError, TypeError) as e:
            raise HashNodeUploadError(f"Invalid response format: {e}")
    
    def _handle_retry(self, attempt: int, reason: str) -> None:
        """Handle retry with exponential backoff."""
        if attempt < self.max_retries - 1:
            wait_time = 2 ** attempt
            self.logger.warning(
                f"Upload attempt {attempt + 1} failed ({reason}), "
                f"retrying in {wait_time}s"
            )
            time.sleep(wait_time)
