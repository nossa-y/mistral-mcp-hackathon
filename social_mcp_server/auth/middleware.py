"""Authentication middleware for HTTP MCP server"""

import logging
from typing import List, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from ..config import config

logger = logging.getLogger(__name__)


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """Middleware to validate Bearer tokens for MCP endpoints"""

    def __init__(self, app, server_token: Optional[str] = None):
        super().__init__(app)
        self.server_token = server_token or config.server_token

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for health endpoints
        if request.url.path in ["/health", "/healthz", "/readiness", "/readyz"]:
            return await call_next(request)

        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # For MCP endpoints, check bearer token
        if request.url.path.startswith("/mcp"):
            if not self.server_token:
                logger.warning("No SERVER_TOKEN configured - allowing all requests")
                return await call_next(request)

            auth_header = request.headers.get("Authorization")
            if not auth_header:
                logger.warning("Missing Authorization header")
                return JSONResponse(
                    {"error": "Missing Authorization header"},
                    status_code=401
                )

            if not auth_header.startswith("Bearer "):
                logger.warning("Invalid Authorization header format")
                return JSONResponse(
                    {"error": "Invalid Authorization header format"},
                    status_code=401
                )

            token = auth_header[7:]  # Remove "Bearer " prefix
            if token != self.server_token:
                logger.warning("Invalid bearer token provided")
                return JSONResponse(
                    {"error": "Invalid token"},
                    status_code=403
                )

            logger.debug("Bearer token validated successfully")

        return await call_next(request)


def create_cors_middleware(allowed_origins: str) -> CORSMiddleware:
    """Create CORS middleware with configuration"""
    # Parse allowed origins
    origins = [origin.strip() for origin in allowed_origins.split(",")]

    return CORSMiddleware(
        allow_origins=origins,
        allow_credentials=True,  # Required for Bearer tokens
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "User-Agent",
        ],
        expose_headers=["Content-Type"],
    )


def get_middleware_stack() -> List[Middleware]:
    """Get the complete middleware stack for the HTTP server"""
    middleware = []

    # Add CORS middleware first
    middleware.append(
        Middleware(
            CORSMiddleware,
            allow_origins=[origin.strip() for origin in config.allowed_origins.split(",")],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "User-Agent"],
            expose_headers=["Content-Type"],
        )
    )

    # Add Bearer token authentication
    middleware.append(
        Middleware(BearerTokenMiddleware, server_token=config.server_token)
    )

    return middleware