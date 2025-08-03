import time
from dataclasses import dataclass
from typing import Dict, Optional
import threading

@dataclass
class URLMapping:
    """Data class to represent a URL mapping with analytics"""
    original_url: str
    short_code: str
    created_at: float
    clicks: int = 0

class URLStore:
    """Thread-safe in-memory storage for URL mappings"""
    
    def __init__(self):
        self._mappings: Dict[str, URLMapping] = {}
        self._lock = threading.Lock()
    
    def add_mapping(self, short_code: str, original_url: str) -> URLMapping:
        """Add a new URL mapping"""
        with self._lock:
            mapping = URLMapping(
                original_url=original_url,
                short_code=short_code,
                created_at=time.time()
            )
            self._mappings[short_code] = mapping
            return mapping
    
    def get_mapping(self, short_code: str) -> Optional[URLMapping]:
        """Get a URL mapping by short code"""
        with self._lock:
            return self._mappings.get(short_code)
    
    def increment_clicks(self, short_code: str) -> bool:
        """Increment click count for a short code"""
        with self._lock:
            mapping = self._mappings.get(short_code)
            if mapping:
                mapping.clicks += 1
                return True
            return False
    
    def get_all_mappings(self) -> Dict[str, URLMapping]:
        """Get all mappings (for testing/debugging)"""
        with self._lock:
            return self._mappings.copy()

# Global instance
url_store = URLStore()