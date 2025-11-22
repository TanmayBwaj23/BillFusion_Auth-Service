"""
Rate limiting middleware for the BillFusion Auth Service
Provides request rate limiting based on IP and user roles
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from typing import Dict, Optional
import structlog

logger = structlog.get_logger()


class RateLimitMiddleware:
    """
    Rate limiting middleware to prevent abuse and DoS attacks
    """
    
    def __init__(self, app):
        self.app = app
        # In-memory store for rate limiting (use Redis in production)
        self.requests: Dict[str, list] = {}
        self.default_requests_per_minute = 100
        self.default_window_seconds = 60
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Check rate limit
            if not self._check_rate_limit(client_ip):
                response = JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "message": "Rate limit exceeded. Please try again later.",
                        "retry_after": self.default_window_seconds
                    }
                )
                await response(scope, receive, send)
                return
        
        await self.app(scope, receive, send)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded IP headers (from load balancers/proxies)
        forwarded_ip = request.headers.get("X-Forwarded-For")
        if forwarded_ip:
            return forwarded_ip.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limit"""
        current_time = time.time()
        window_start = current_time - self.default_window_seconds
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier] 
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # Check if within limit
        if len(self.requests[identifier]) >= self.default_requests_per_minute:
            logger.warning(
                "Rate limit exceeded",
                client=identifier,
                requests_count=len(self.requests[identifier]),
                window_seconds=self.default_window_seconds
            )
            return False
        
        # Add current request
        self.requests[identifier].append(current_time)
        return True
