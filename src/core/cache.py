"""
Caching system for VeriFAI LLM to improve performance.
Provides in-memory caching for scan results and LLM responses.
"""

import hashlib
import json
import time
from collections import OrderedDict
from threading import Lock
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta


class LRUCache:
    """
    Thread-safe LRU (Least Recently Used) cache implementation.
    
    Automatically evicts least recently used items when capacity is reached.
    """
    
    def __init__(self, capacity: int = 100, default_ttl: int = 3600):
        """
        Initialize the LRU cache.
        
        Args:
            capacity: Maximum number of items to store
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._capacity = capacity
        self._default_ttl = default_ttl
        self._lock = Lock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a hash key from arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Retrieve an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Tuple of (found, value). If not found, value is None.
        """
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                
                # Check if item has expired
                if item.get("expires_at") and time.time() > item["expires_at"]:
                    del self._cache[key]
                    return False, None
                
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                return True, item["value"]
            
            return False, None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store an item in the cache.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (optional, uses default if not provided)
        """
        with self._lock:
            # If key exists, remove it first to update position
            if key in self._cache:
                del self._cache[key]
            
            # Evict oldest items if at capacity
            while len(self._cache) >= self._capacity:
                self._cache.popitem(last=False)
            
            # Calculate expiration time
            expires_at = time.time() + (ttl or self._default_ttl)
            
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time()
            }
    
    def delete(self, key: str) -> bool:
        """
        Delete an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if item was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """Get the current number of items in the cache."""
        with self._lock:
            return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            now = time.time()
            expired = sum(
                1 for item in self._cache.values()
                if item.get("expires_at") and now > item["expires_at"]
            )
            
            return {
                "capacity": self._capacity,
                "current_size": len(self._cache),
                "expired_items": expired,
                "active_items": len(self._cache) - expired,
                "memory_usage_estimate": f"~{len(self._cache) * 1024 / 1024:.1f}MB"  # Rough estimate
            }
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired items from the cache.
        
        Returns:
            Number of items removed
        """
        with self._lock:
            now = time.time()
            expired_keys = [
                key for key, item in self._cache.items()
                if item.get("expires_at") and now > item["expires_at"]
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)


# Global cache instances for different use cases
_scan_results_cache = LRUCache(capacity=50, default_ttl=1800)  # 30 minutes for scan results
_llm_response_cache = LRUCache(capacity=100, default_ttl=3600)  # 1 hour for LLM responses
_semgrep_cache = LRUCache(capacity=100, default_ttl=3600)  # 1 hour for Semgrep results


def get_scan_cache() -> LRUCache:
    """Get the cache for scan results."""
    return _scan_results_cache


def get_llm_cache() -> LRUCache:
    """Get the cache for LLM responses."""
    return _llm_response_cache


def get_semgrep_cache() -> LRUCache:
    """Get the cache for Semgrep results."""
    return _semgrep_cache


def cache_scan_result(code_hash: str, semgrep_results: dict, llm_analysis: str, patch: str) -> str:
    """
    Cache a complete scan result.
    
    Args:
        code_hash: Hash of the code being analyzed
        semgrep_results: Results from Semgrep scan
        llm_analysis: LLM analysis text
        patch: Generated patch suggestions
        
    Returns:
        Cache key for the stored result
    """
    result = {
        "semgrep_results": semgrep_results,
        "llm_analysis": llm_analysis,
        "patch": patch,
        "timestamp": datetime.now().isoformat()
    }
    
    cache_key = f"scan:{code_hash}"
    _scan_results_cache.set(cache_key, result, ttl=1800)  # 30 minutes
    
    return cache_key


def get_cached_scan(code_hash: str) -> Optional[dict]:
    """
    Retrieve a cached scan result.
    
    Args:
        code_hash: Hash of the code being analyzed
        
    Returns:
        Cached result dict if found, None otherwise
    """
    cache_key = f"scan:{code_hash}"
    found, result = _scan_results_cache.get(cache_key)
    
    if found:
        return result
    return None


def cache_semgrep_result(code_hash: str, semgrep_results: dict) -> str:
    """
    Cache Semgrep scan results.
    
    Args:
        code_hash: Hash of the code being analyzed
        semgrep_results: Results from Semgrep scan
        
    Returns:
        Cache key for the stored result
    """
    cache_key = f"semgrep:{code_hash}"
    _semgrep_cache.set(cache_key, semgrep_results, ttl=3600)  # 1 hour
    
    return cache_key


def get_cached_semgrep(code_hash: str) -> Optional[dict]:
    """
    Retrieve cached Semgrep results.
    
    Args:
        code_hash: Hash of the code being analyzed
        
    Returns:
        Cached Semgrep results if found, None otherwise
    """
    cache_key = f"semgrep:{code_hash}"
    found, result = _semgrep_cache.get(cache_key)
    
    if found:
        return result
    return None


def compute_code_hash(code: str) -> str:
    """
    Compute a hash for code content.
    
    Args:
        code: Code content to hash
        
    Returns:
        SHA256 hash of the code (first 32 chars)
    """
    return hashlib.sha256(code.encode()).hexdigest()[:32]


def should_use_cache(code: str, force_refresh: bool = False) -> Tuple[bool, str]:
    """
    Determine if cached results should be used for the given code.
    
    Args:
        code: Code content to check
        force_refresh: If True, always return False (don't use cache)
        
    Returns:
        Tuple of (should_use_cache, code_hash)
    """
    if force_refresh:
        return False, compute_code_hash(code)
    
    code_hash = compute_code_hash(code)
    cached_result = get_cached_scan(code_hash)
    
    return cached_result is not None, code_hash


def get_cache_stats() -> Dict[str, Dict[str, Any]]:
    """
    Get statistics for all caches.
    
    Returns:
        Dictionary with stats for each cache
    """
    return {
        "scan_results": get_scan_cache().stats(),
        "llm_responses": get_llm_cache().stats(),
        "semgrep_results": get_semgrep_cache().stats()
    }


def clear_all_caches() -> None:
    """Clear all cache instances."""
    get_scan_cache().clear()
    get_llm_cache().clear()
    get_semgrep_cache().clear()


def cleanup_all_expired() -> Dict[str, int]:
    """
    Clean up expired items from all caches.
    
    Returns:
        Dictionary with count of removed items per cache
    """
    return {
        "scan_results": get_scan_cache().cleanup_expired(),
        "llm_responses": get_llm_cache().cleanup_expired(),
        "semgrep_results": get_semgrep_cache().cleanup_expired()
    }