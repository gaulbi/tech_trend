"""Hashnode API client for publishing articles."""

import time
from typing import Dict, Any, List

import requests

from .models import HashnodeResponse
from .exceptions import PublishError, NetworkError
from .logger import get_logger

logger = get_logger(__name__)


class HashnodeClient:
    """Client for Hashnode GraphQL API."""
    
    PUBLISH_MUTATION = """
    mutation PublishPost($input: PublishPostInput!) {
        publishPost(input: $input) {
            post { 
                id 
                slug 
                title
            }
        }
    }
    """
    
    def __init__(
        self,
        server_url: str,
        api_key: str,
        api_header: str,
        timeout: int,
        max_retries: int
    ):
        """
        Initialize Hashnode client.
        
        Args:
            server_url: Hashnode GraphQL server URL
            api_key: API key for authentication
            api_header: Header name for API key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.server_url = server_url
        self.api_key = api_key
        self.api_header = api_header
        self.timeout = timeout
        self.max_retries = max_retries
    
    def publish_article(
        self,
        title: str,
        content: str,
        publication_id: str,
        tags: List[str] = None
    ) -> HashnodeResponse:
        """
        Publish article to Hashnode.
        
        Args:
            title: Article title
            content: Article content in markdown
            publication_id: Hashnode publication ID
            tags: Optional list of tags
            
        Returns:
            HashnodeResponse object
            
        Raises:
            PublishError: If publishing fails
            NetworkError: If network request fails
        """
        if tags is None:
            tags = []
        
        # Prepare GraphQL variables
        variables = {
            "input": {
                "title": title,
                "contentMarkdown": content,
                "publicationId": publication_id,
                "tags": tags
            }
        }
        
        # Prepare request payload
        payload = {
            "query": self.PUBLISH_MUTATION,
            "variables": variables
        }
        
        # Make request with retries
        response_data = self._make_request_with_retry(payload)
        
        # Parse response
        return self._parse_response(response_data)
    
    def _make_request_with_retry(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make HTTP request with exponential backoff retry.
        
        Args:
            payload: Request payload
            
        Returns:
            Response data
            
        Raises:
            NetworkError: If all retries fail
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key
        }
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"Request attempt {attempt + 1}/{self.max_retries}",
                    extra={"attempt": attempt + 1}
                )
                
                response = requests.post(
                    self.server_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                return response.json()
                
            except requests.Timeout as e:
                last_error = e
                logger.warning(
                    f"Request timeout (attempt {attempt + 1})",
                    extra={"attempt": attempt + 1}
                )
                
            except requests.RequestException as e:
                last_error = e
                logger.warning(
                    f"Request failed (attempt {attempt + 1}): {e}",
                    extra={"attempt": attempt + 1, "error": str(e)}
                )
            
            # Exponential backoff: 1s, 2s, 4s
            if attempt < self.max_retries - 1:
                sleep_time = 2 ** attempt
                logger.debug(f"Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
        
        # All retries failed
        raise NetworkError(
            f"Failed after {self.max_retries} attempts: {last_error}"
        )
    
    def _parse_response(
        self,
        response_data: Dict[str, Any]
    ) -> HashnodeResponse:
        """
        Parse Hashnode API response.
        
        Args:
            response_data: Raw response data
            
        Returns:
            HashnodeResponse object
        """
        # Check for GraphQL errors
        errors = response_data.get("errors")
        if errors:
            logger.error(
                "GraphQL errors in response",
                extra={"errors": errors}
            )
            return HashnodeResponse(
                post_id=None,
                slug=None,
                title=None,
                errors=errors
            )
        
        # Extract post data
        data = response_data.get("data", {})
        publish_post = data.get("publishPost", {})
        post = publish_post.get("post")
        
        if not post:
            logger.error("No post data in response")
            return HashnodeResponse(
                post_id=None,
                slug=None,
                title=None,
                errors=["No post data in response"]
            )
        
        return HashnodeResponse(
            post_id=post.get("id"),
            slug=post.get("slug"),
            title=post.get("title"),
            errors=None
        )
