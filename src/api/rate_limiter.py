"""
Rate limiting middleware for VeriFAI LLM API.
Provides protection against API abuse and DoS attacks.
"""

import time
from collections import defaultdict
from functools import wraps
from threading import Lock
from typing import Callable, Dict, Optional, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse


class RateLimiter:
    """
    Thread-safe rate limiter using sliding window algorithm.
    
    Supports multiple rate limit rules (e.g., 10/minute, 100/hour).
    """
    
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = Lock()
    
    def _clean_old_requests(self, key: str, window_seconds: int) -> None:
        """Remove requests outside the current time window."""
        current_time = time.time()
        cutoff = current_time - window_seconds
        with self._lock:
            self._requests[key] = [
                timestamp for timestamp in self._requests[key]
                if timestamp > cutoff
            ]
    
    def is_rate_limited(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> Tuple[bool, int, int]:
        """
        Check if a request should be rate limited.
        
        Args:
            key: Unique identifier (e.g., IP address, user ID)
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_limited, remaining_requests, retry_after_seconds)
        """
        current_time = time.time()
        self._clean_old_requests(key, window_seconds)
        
        with self._lock:
            request_count = len(self._requests[key])
            
            if request_count >= max_requests:
                # Calculate retry after based on oldest request in window
                oldest_request = min(self._requests[key]) if self._requests[key] else current_time
                retry_after = int(oldest_request + window_seconds - current_time) + 1
                return True, 0, max(retry_after, 1)
            
            # Record this request
            self._requests[key].append(current_time)
            remaining = max_requests - request_count - 1
            return False, remaining, 0
    
    def get_rate_limit_headers(
        self, 
        remaining: int, 
        max_requests: int, 
        window_seconds: int
    ) -> Dict[str, str]:
        """Generate standard rate limit headers."""
        return {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": str(max_requests - remaining),
            "X-RateLimit-Reset": str(int(time.time()) + window_seconds),
        }


# Global rate limiter instance
rate_limiter = RateLimiter()

# Rate limit configurations
RATE_LIMITS = {
    "default": {"max_requests": 100, "window_seconds": 60},      # 100/minute
    "scan": {"max_requests": 10, "window_seconds": 60},           # 10 scans/minute  
    "auth": {"max_requests": 5, "window_seconds": 60},            # 5 auth attempts/minute
    "chat": {"max_requests": 30, "window_seconds": 60},           # 30 chat messages/minute
    "upload": {"max_requests": 20, "window_seconds": 60},         # 20 uploads/minute
}


def get_client_identifier(request: Request) -> str:
    """Extract client identifier from request (IP address or user ID)."""
    # Try to get user ID from authorization header first
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # Use first 16 chars of token as identifier
        return f"user:{token[:16]}"
    
    # Fall back to IP address
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        # Get the first IP in the chain
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    return f"ip:{client_ip}"


def rate_limit_middleware(category: str = "default"):
    """
    Decorator for rate limiting FastAPI route handlers.
    
    Args:
        category: Rate limit category (default, scan, auth, chat, upload)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the request from kwargs or args
            request: Optional[Request] = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if request is None:
                # If no request found, skip rate limiting
                return await func(*args, **kwargs)
            
            client_id = get_client_identifier(request)
            limit_config = RATE_LIMITS.get(category, RATE_LIMITS["default"])
            
            is_limited, remaining, retry_after = rate_limiter.is_rate_limited(
                client_id,
                limit_config["max_requests"],
                limit_config["window_seconds"]
            )
            
            if is_limited:
                headers = {
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit_config["max_requests"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + limit_config["window_seconds"]),
                }
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    headers=headers
                )
            
            # Call the actual function
            response = await func(*args, **kwargs)
            
            # Add rate limit headers to successful response
            if hasattr(response, "headers"):
                headers = rate_limiter.get_rate_limit_headers(
                    remaining,
                    limit_config["max_requests"],
                    limit_config["window_seconds"]
                )
                for key, value in headers.items():
                    response.headers[key] = value
            
            return response
        return wrapper
    return decorator


async def rate_limit_dependency(
    request: Request,
    category: str = "default"
) -> Dict[str, str]:
    """
    FastAPI dependency for rate limiting.
    Can be used with Depends() in route definitions.
    """
    client_id = get_client_identifier(request)
    limit_config = RATE_LIMITS.get(category, RATE_LIMITS["default"])
    
    is_limited, remaining, retry_after = rate_limiter.is_rate_limited(
        client_id,
        limit_config["max_requests"],
        limit_config["window_seconds"]
    )
    
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(limit_config["max_requests"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + limit_config["window_seconds"]),
            }
        )
    
    return {
        "X-RateLimit-Limit": str(limit_config["max_requests"]),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(time.time()) + limit_config["window_seconds"]),
    }