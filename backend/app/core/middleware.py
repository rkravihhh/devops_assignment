"""
Custom middleware for the application.
"""

import time
import uuid
import hashlib
import hmac
from typing import Callable, Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
from app.core.config import settings

logger = structlog.get_logger()


class LoggingMiddleware:
    """Middleware for request/response logging."""
    
    def __init__(self, app: Any) -> None:
        self.app = app
    
    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        # Log request
        start_time = time.time()
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        # Process request
        async def send_wrapper(message) -> None:
            if message["type"] == "http.response.start":
                # Calculate processing time
                process_time = time.time() - start_time
                
                # Log response
                logger.info(
                    "Request completed",
                    status_code=message["status"],
                    process_time=process_time
                )
                
                # Add request ID to response headers
                if "headers" not in message:
                    message["headers"] = []
                message["headers"].append([b"x-request-id", request_id.encode()])
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


class SecurityHeadersMiddleware:
    """Middleware for adding security headers."""
    
    def __init__(self, app: Any) -> None:
        self.app = app
    
    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_wrapper(message) -> None:
            if message["type"] == "http.response.start":
                # Add security headers
                if "headers" not in message:
                    message["headers"] = []
                
                message["headers"].extend([
                    [b"x-content-type-options", b"nosniff"],
                    [b"x-frame-options", b"DENY"],
                    [b"x-xss-protection", b"1; mode=block"],
                    [b"strict-transport-security", b"max-age=31536000; includeSubDomains"],
                    [b"referrer-policy", b"strict-origin-when-cross-origin"]
                ])
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)