import re
import random
import string
from urllib.parse import urlparse
from typing import Optional

def is_valid_url(url: str) -> bool:
    """
    Validate if a string is a proper URL
    
    Args:
        url: The URL string to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # Basic URL pattern validation - more permissive for testing
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)?$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def generate_short_code(length: int = 6) -> str:
    """
    Generate a random alphanumeric short code
    
    Args:
        length: Length of the short code (default: 6)
        
    Returns:
        str: Random alphanumeric string
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def format_timestamp(timestamp: float) -> str:
    """
    Format timestamp to ISO format string
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        str: ISO formatted timestamp string
    """
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).isoformat()

def sanitize_url(url: str) -> str:
    """
    Sanitize URL by ensuring it has a proper scheme
    
    Args:
        url: The URL to sanitize
        
    Returns:
        str: Sanitized URL with proper scheme
    """
    if not url.startswith(('http://', 'https://')):
        return f'https://{url}'
    return url