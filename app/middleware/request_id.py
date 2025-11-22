"""
Request ID middleware for the BillFusion Auth Service
Adds unique request IDs for tracing and logging
"""

from fastapi import Request
import uuid
import structlog

logger = structlog.get_logger()


class RequestIDMiddleware:
    """
    Middleware to add unique request IDs for tracing
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Generate unique request ID
            request_id = self._generate_request_id()
            
            # Add to scope for access by other middleware/handlers
            scope["request_id"] = request_id
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    # Add request ID to response headers
                    headers = dict(message.get("headers", []))
                    headers[b"X-Request-ID"] = request_id.encode()
                    message["headers"] = list(headers.items())
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID"""
        return str(uuid.uuid4())
