# ==============================================================================
# FILE: src/article_publisher/hashnode_client.py
# ==============================================================================
"""Hashnode GraphQL API client."""

import json
import os
import re
import time
from typing import Any, Dict, Optional

import requests

from .exceptions import PublishError
from .logger import log_error


class HashnodeWithImageClient:
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
        logger,
        image_mapping_base_path: Optional[str] = None
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
            image_mapping_base_path: Base path for image URL mapping JSON files
        """
        self.api_key = api_key
        self.server_url = server_url
        self.header_name = header_name
        self.timeout = timeout
        self.retry_count = retry_count
        self.logger = logger
        self.image_mapping_base_path = image_mapping_base_path
    
    def _validate_path_components(
        self,
        feed_date: str,
        category: str
    ) -> bool:
        """
        Validate path components for security.
        
        Args:
            feed_date: Feed date in YYYY-MM-DD format
            category: Article category
            
        Returns:
            True if valid, False otherwise
        """
        # Validate feed_date format (YYYY-MM-DD)
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', feed_date):
            self.logger.warning(f"Invalid feed_date format: {feed_date}")
            return False
        
        # Validate category (alphanumeric + underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', category):
            self.logger.warning(f"Invalid category format: {category}")
            return False
        
        return True
    
    def _get_cover_image_url(
        self,
        article_filename: str,
        feed_date: str,
        category: str
    ) -> Optional[str]:
        """
        Get cover image URL from mapping JSON file.
        
        Args:
            article_filename: Name of the article file (e.g., "thunderbolt-5.md")
            feed_date: Feed date in YYYY-MM-DD format
            category: Article category
            
        Returns:
            Image URL from imgbb_url field, or None if not found
        """
        if not self.image_mapping_base_path:
            return None
        
        # Validate path components for security
        if not self._validate_path_components(feed_date, category):
            return None
        
        # Construct JSON file path
        json_path = os.path.join(
            self.image_mapping_base_path,
            feed_date,
            f"{category}.json"
        )
        
        # Check if file exists
        if not os.path.exists(json_path):
            self.logger.warning(
                f"Image mapping file not found: {json_path}"
            )
            return None
        
        try:
            # Read and parse JSON file
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # # Ensure data is an array
            # if not isinstance(data, list):
            #     self.logger.warning(
            #         f"Expected array in {json_path}, got {type(data).__name__}"
            #     )
            #     return None
            
            # Normalize article filename for comparison (strip extension)
            article_base = os.path.splitext(article_filename)[0]

            
            json_article_file = data.get('article_file', '')
            json_base = os.path.splitext(json_article_file)[0]
            
            if article_base == json_base:
                # Found matching article, extract imgbb_url
                imgbb_url = data.get('imgbb_url', '').strip()
                
                if not imgbb_url:
                    self.logger.warning(
                        f"Empty imgbb_url for '{article_filename}' in {json_path}"
                    )
                    return None
                
                # Validate URL format
                if not imgbb_url.startswith(('http://', 'https://')):
                    self.logger.warning(
                        f"Invalid image URL format for '{article_filename}': {imgbb_url}"
                    )
                    return None
                
                self.logger.info(
                    f"Found cover image for '{article_filename}': {imgbb_url}"
                )
                return imgbb_url
            
            # Search for matching article in array
            # for item in data:
            #     if not isinstance(item, dict):
            #         continue
                
            #     json_article_file = item.get('article_file', '')
            #     json_base = os.path.splitext(json_article_file)[0]
                
            #     if article_base == json_base:
            #         # Found matching article, extract imgbb_url
            #         imgbb_url = item.get('imgbb_url', '').strip()
                    
            #         if not imgbb_url:
            #             self.logger.warning(
            #                 f"Empty imgbb_url for '{article_filename}' in {json_path}"
            #             )
            #             return None
                    
            #         # Validate URL format
            #         if not imgbb_url.startswith(('http://', 'https://')):
            #             self.logger.warning(
            #                 f"Invalid image URL format for '{article_filename}': {imgbb_url}"
            #             )
            #             return None
                    
            #         self.logger.info(
            #             f"Found cover image for '{article_filename}': {imgbb_url}"
            #         )
            #         return imgbb_url
            
            # No matching article found in array
            self.logger.warning(
                f"No matching article found for '{article_filename}' in {json_path}"
            )
            return None
            
        except json.JSONDecodeError as e:
            self.logger.warning(
                f"Failed to parse JSON file {json_path}: {e}"
            )
            return None
        except Exception as e:
            self.logger.warning(
                f"Error reading image mapping file {json_path}: {e}"
            )
            return None
    
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
        publication_id: str,
        article_filename: Optional[str] = None,
        feed_date: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Publish article to Hashnode.
        
        Args:
            title: Article title
            content: Article content in Markdown
            publication_id: Hashnode publication ID
            article_filename: Name of the article file (e.g., "thunderbolt-5.md")
            feed_date: Feed date in YYYY-MM-DD format
            category: Article category
            
        Returns:
            Response data with post ID and slug, or None if failed
        """
        # Build input object
        input_data = {
            "title": title,
            "contentMarkdown": content,
            "publicationId": publication_id,
            "tags": []
        }
        
        # Try to get cover image URL
        # self.logger.info(f'article_filename: {article_filename}, feed_date: {feed_date}, category: {category}')
        # if article_filename and feed_date and category:
        #     cover_image_url = self._get_cover_image_url(
        #         article_filename,
        #         feed_date,
        #         category
        #     )
        #     self.logger.info(f'cover_image_url: {cover_image_url}')
        #     if cover_image_url:
        #         input_data["coverImageOptions"] = {
        #             "coverImageURL": cover_image_url
        #         }
        # cover_image_url = self._get_cover_image_url(
        #     article_filename,
        #     '2025-12-20',
        #     'software_engineering'
        # )
        cover_image_url = 'https://i.ibb.co/1f5Fggns/retrieval-augmented-generation.png'
        self.logger.info(f'cover_image_url: {cover_image_url}')
        if cover_image_url:
            input_data["coverImageOptions"] = {
                "coverImageURL": cover_image_url
            }
        
        variables = {
            "input": input_data
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