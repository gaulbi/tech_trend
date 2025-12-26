"""
ImgBB image upload module.
"""
import base64
import logging
import time
from pathlib import Path
from typing import Optional

import requests

from .exceptions import ImgBBUploadError


class ImgBBUploader:
    """Handles image uploads to ImgBB."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int,
        max_retries: int,
        logger: logging.Logger
    ):
        """
        Initialize ImgBB uploader.
        
        Args:
            api_key: ImgBB API key
            base_url: ImgBB API base URL
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
        Upload image to ImgBB with retry logic.
        
        Args:
            image_path: Path to image file
            
        Returns:
            ImgBB CDN URL
            
        Raises:
            ImgBBUploadError: If upload fails after all retries
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
                    raise ImgBBUploadError(f"Upload failed: {e}")
                self._handle_retry(attempt, str(e))
        
        raise ImgBBUploadError(
            f"Upload failed after {self.max_retries} attempts"
        )
    
    def _upload_attempt(self, image_path: Path) -> str:
        """
        Perform single upload attempt.
        
        Args:
            image_path: Path to image file
            
        Returns:
            ImgBB CDN URL
            
        Raises:
            ImgBBUploadError: If upload fails
        """
        if not image_path.exists():
            raise ImgBBUploadError(f"Image file not found: {image_path}")
        
        # Check file size (ImgBB limit: 32 MB)
        file_size = image_path.stat().st_size
        max_size = 32 * 1024 * 1024  # 32 MB in bytes
        if file_size > max_size:
            raise ImgBBUploadError(
                f"Image file too large: {file_size / (1024 * 1024):.2f} MB "
                f"(max: 32 MB)"
            )
        
        # Read and encode image as base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Build the API URL with the key parameter
        url = f"{self.base_url}?key={self.api_key}"
        
        # Prepare form data
        data = {
            'image': image_data,
            'name': image_path.stem
        }
        
        response = requests.post(
            url,
            data=data,
            timeout=self.timeout
        )
        
        if response.status_code == 400:
            try:
                error_msg = response.json().get('error', {}).get('message', 'Bad request')
                raise ImgBBUploadError(f"Upload failed: {error_msg}")
            except (KeyError, ValueError):
                raise ImgBBUploadError("Upload failed: Bad request")
        
        if response.status_code == 401 or response.status_code == 403:
            raise ImgBBUploadError("Authentication failed - invalid API key")
        
        if response.status_code == 429:
            self.logger.warning("Rate limit hit, waiting before retry")
            time.sleep(5)
            raise requests.exceptions.RequestException("Rate limited")
        
        response.raise_for_status()
        
        return self._extract_url(response.json())
    
    def _extract_url(self, response_data: dict) -> str:
        """
        Extract CDN URL from response.
        
        Args:
            response_data: API response JSON
            
        Returns:
            CDN URL
            
        Raises:
            ImgBBUploadError: If URL cannot be extracted
        """
        try:
            if not response_data.get('success'):
                error_msg = response_data.get('error', {}).get('message', 'Unknown error')
                raise ImgBBUploadError(f"Upload failed: {error_msg}")
            
            return response_data['data']['url']
        except (KeyError, TypeError) as e:
            raise ImgBBUploadError(f"Invalid response format: {e}")
    
    def _handle_retry(self, attempt: int, reason: str) -> None:
        """Handle retry with exponential backoff."""
        if attempt < self.max_retries - 1:
            wait_time = 2 ** attempt
            self.logger.warning(
                f"Upload attempt {attempt + 1} failed ({reason}), "
                f"retrying in {wait_time}s"
            )
            time.sleep(wait_time)