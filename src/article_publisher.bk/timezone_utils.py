# ==============================================================================
# FILE: src/article_publisher/timezone_utils.py
# ==============================================================================
"""Timezone utilities and shared imports."""

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from .exceptions import ConfigurationError


def validate_timezone(timezone_str: str) -> None:
    """
    Validate that timezone string is valid.
    
    Args:
        timezone_str: Timezone string (e.g., 'America/New_York')
        
    Raises:
        ConfigurationError: If timezone is invalid
    """
    try:
        ZoneInfo(timezone_str)
    except Exception as e:
        raise ConfigurationError(
            f"Invalid timezone '{timezone_str}': {e}"
        )


def get_timezone(timezone_str: str) -> ZoneInfo:
    """
    Get ZoneInfo object for timezone string.
    
    Args:
        timezone_str: Timezone string (e.g., 'America/New_York')
        
    Returns:
        ZoneInfo object
    """
    return ZoneInfo(timezone_str)
