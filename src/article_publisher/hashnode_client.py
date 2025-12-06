# ==============================================================================
# FILE: src/article_publisher/hashnode_client.py
# ==============================================================================
"""Hashnode GraphQL API client."""

import time
from typing import Any, Dict, Optional

import requests

from .exceptions import PublishError
from .logger import log_error


class HashnodeClient:
    """Client for Hashnode GraphQL API."""
    
    CREATE_STORY_MUTATION = """
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
        api_key: str,
        server_url: str,
        header_name: str,
        timeout: int,
        retry_count: int,
        logger
    ):
        """
        Initialize Hashnode client.
        
        Args:
            api_key: API authentication key
            server_url: GraphQL server URL
            header_name: Name of authentication header
            timeout: Request timeout in seconds
            retry_count: Number of retry attempts
            logger: Logger instance
        """
        self.api_key = api_key
        self.server_url = server_url
        self.header_name = header_name
        self.timeout = timeout
        self.retry_count = retry_count
        self.logger = logger
    
    def _make_request(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        attempt: int
    ) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to Hashnode API.
        
        Args:
            payload: GraphQL query payload
            headers: HTTP headers
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Response data or None if failed
        """
        try:
            response = requests.post(
                self.server_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.Timeout:
            self.logger.warning(
                f"Request timeout (attempt {attempt + 1}/{self.retry_count})"
            )
            return None
            
        except requests.RequestException as e:
            self.logger.error(f"Network error: {e}")
            return None
    
    def _validate_response(
        self,
        data: Dict[str, Any],
        title: str
    ) -> Optional[Dict[str, str]]:
        """
        Validate GraphQL response structure.
        
        Args:
            data: Response data from API
            title: Article title (for logging)
            
        Returns:
            Post data with id and slug, or None if invalid
        """
        # Check for GraphQL errors
        if 'errors' in data:
            error_msgs = [
                e.get('message', str(e)) for e in data['errors']
            ]
            self.logger.error(
                f"GraphQL errors for '{title}': {'; '.join(error_msgs)}"
            )
            return None
        
        # Validate response structure
        post_data = data.get('data', {}).get('publishPost', {})
        if not post_data or 'post' not in post_data:
            self.logger.error(
                f"Invalid response structure for '{title}': "
                f"missing publishPost.post"
            )
            return None
        
        post = post_data['post']
        if not isinstance(post, dict) or 'id' not in post:
            self.logger.error(
                f"Invalid post data for '{title}': missing id field"
            )
            return None
        
        return post
    
    def publish_article(
        self,
        title: str,
        content: str,
        publication_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Publish article to Hashnode.
        
        Args:
            title: Article title
            content: Article content in Markdown
            publication_id: Hashnode publication ID
            
        Returns:
            Response data with post ID and slug, or None if failed
        """
        variables = {
            "input": {
                "title": title,
                "contentMarkdown": content,
                "publicationId": publication_id,
                "tags": []
            }
        }
        
        payload = {
            "query": self.CREATE_STORY_MUTATION,
            "variables": variables
        }
        
        headers = {
            "Content-Type": "application/json",
            #self.header_name: self.api_key
            "Authorization": self.api_key
        }
        
        # Retry loop for network errors only
        for attempt in range(self.retry_count):
            self.logger.debug(
                f"Publishing '{title}' (attempt {attempt + 1})"
            )
            
            data = self._make_request(payload, headers, attempt)
            
            if data is None:
                # Network error - retry with backoff
                if attempt < self.retry_count - 1:
                    sleep_time = 2 ** attempt
                    self.logger.debug(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                continue
            
            # Validate response
            post = self._validate_response(data, title)
            
            if post is None:
                # GraphQL error - don't retry
                return None
            
            # Success
            slug = post.get('slug', 'N/A')
            self.logger.info(
                f"Successfully published: {title} (slug: {slug})"
            )
            return post
        
        # All retries exhausted
        self.logger.error(
            f"Failed to publish '{title}' after "
            f"{self.retry_count} attempts"
        )
        return None