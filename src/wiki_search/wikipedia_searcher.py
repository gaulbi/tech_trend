"""
Wikipedia search and content retrieval.
"""

import logging
import time
from typing import List, Optional, Set, Tuple
from urllib.parse import quote

import wikipedia

from .logger import log_error_with_context
from .content_cleaner import ContentCleaner

logger = logging.getLogger("wiki_search")


class WikipediaSearcher:
    """Handles Wikipedia search and content retrieval with retry logic."""

    MAX_RETRIES = 3
    BACKOFF_DELAYS = [1, 2, 4]  # Exponential backoff in seconds

    def __init__(self, max_results: int) -> None:
        """
        Initialize Wikipedia searcher.

        Args:
            max_results: Maximum number of search results per query
        """
        self.max_results = max_results
        self.cleaner = ContentCleaner()

    def search_and_fetch(
        self,
        keyword: str,
        topic: str
    ) -> List[Tuple[str, str, str]]:
        """
        Search Wikipedia and fetch content for all results.

        Args:
            keyword: Search keyword to query
            topic: Original topic for logging context

        Returns:
            List of tuples: (query_used, page_url, cleaned_content)
        """
        titles = self._search_with_retry(keyword, topic)

        if not titles:
            logger.debug(
                f"No Wikipedia results found for keyword: '{keyword}' "
                f"(topic: '{topic}')"
            )
            return []

        results = []
        for title in titles:
            content = self._fetch_page_with_retry(title, keyword, topic)
            if content:
                page_url = self._get_page_url(title)
                cleaned_content = self.cleaner.clean(content)
                results.append((keyword, page_url, cleaned_content))

        logger.info(
            f"Successfully fetched {len(results)}/{len(titles)} pages "
            f"for keyword: '{keyword}' (topic: '{topic}')"
        )

        return results

    def _search_with_retry(
        self,
        keyword: str,
        topic: str
    ) -> List[str]:
        """
        Search Wikipedia with retry logic.

        Args:
            keyword: Search keyword
            topic: Topic for context in logging

        Returns:
            List of page titles (empty if search fails)
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                titles = wikipedia.search(keyword, results=self.max_results)
                logger.info(
                    f"Search found {len(titles)} results for '{keyword}' "
                    f"(topic: '{topic}')"
                )
                return titles
            except wikipedia.exceptions.WikipediaException as e:
                log_error_with_context(
                    logger,
                    f"Wikipedia search error",
                    context={
                        "keyword": keyword,
                        "topic": topic,
                        "attempt": f"{attempt + 1}/{self.MAX_RETRIES}",
                        "error": str(e)
                    },
                    exc_info=False
                )
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.BACKOFF_DELAYS[attempt])
            except Exception as e:
                log_error_with_context(
                    logger,
                    f"Unexpected error searching Wikipedia",
                    context={"keyword": keyword, "topic": topic}
                )
                break

        return []

    def _fetch_page_with_retry(
        self,
        title: str,
        keyword: str,
        topic: str,
        visited_titles: Optional[Set[str]] = None
    ) -> Optional[str]:
        """
        Fetch Wikipedia page content with retry logic.

        Args:
            title: Wikipedia page title
            keyword: Search keyword for context
            topic: Topic for context in logging
            visited_titles: Set of already visited titles to prevent loops

        Returns:
            Page content or None if fetch fails
        """
        if visited_titles is None:
            visited_titles = set()

        # Prevent infinite loops in disambiguation chains
        if title in visited_titles:
            logger.debug(
                f"Circular disambiguation detected for '{title}' "
                f"(keyword: '{keyword}', topic: '{topic}')"
            )
            return None

        if len(visited_titles) >= 5:
            logger.debug(
                f"Max disambiguation depth reached for '{title}' "
                f"(keyword: '{keyword}', topic: '{topic}')"
            )
            return None

        visited_titles.add(title)

        for attempt in range(self.MAX_RETRIES):
            try:
                page = wikipedia.page(title, auto_suggest=False)
                return page.content
            except wikipedia.exceptions.DisambiguationError as e:
                # Pick first option from disambiguation page
                if e.options:
                    first_option = e.options[0]
                    logger.debug(
                        f"Disambiguation for '{title}', "
                        f"trying: '{first_option}' "
                        f"(keyword: '{keyword}', topic: '{topic}')"
                    )
                    # Recursive call with visited set to prevent loops
                    return self._fetch_page_with_retry(
                        first_option,
                        keyword,
                        topic,
                        visited_titles
                    )
                else:
                    logger.debug(
                        f"Disambiguation for '{title}' with no options "
                        f"(keyword: '{keyword}', topic: '{topic}')"
                    )
                    return None
            except wikipedia.exceptions.PageError:
                logger.debug(
                    f"Page not found: '{title}' "
                    f"(keyword: '{keyword}', topic: '{topic}')"
                )
                return None
            except wikipedia.exceptions.WikipediaException as e:
                log_error_with_context(
                    logger,
                    f"Wikipedia fetch error",
                    context={
                        "title": title,
                        "keyword": keyword,
                        "topic": topic,
                        "attempt": f"{attempt + 1}/{self.MAX_RETRIES}",
                        "error": str(e)
                    },
                    exc_info=False
                )
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.BACKOFF_DELAYS[attempt])
            except Exception as e:
                log_error_with_context(
                    logger,
                    f"Unexpected error fetching page",
                    context={"title": title, "keyword": keyword, "topic": topic}
                )
                break

        return None

    @staticmethod
    def _get_page_url(title: str) -> str:
        """
        Construct Wikipedia page URL from title.

        Args:
            title: Page title

        Returns:
            Full Wikipedia URL with proper encoding
        """
        # Properly encode the title for URL
        encoded_title = quote(title.replace(" ", "_"), safe='/:')
        return f"https://en.wikipedia.org/wiki/{encoded_title}"