"""HTTP MCP Server implementation with FastMCP"""

import logging
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.middleware import Middleware

from .tools.x_tools import register_x_tools
from .tools.linkedin_tools import register_linkedin_tools
from .auth.middleware import create_cors_middleware, BearerTokenMiddleware
from .config import config

logger = logging.getLogger(__name__)


def create_http_mcp_server() -> FastMCP:
    """Create and configure the HTTP MCP server instance"""
    logger.info("Creating HTTP Social MCP Server...")

    # Initialize FastMCP server with HTTP configuration
    mcp = FastMCP(name=config.server_name)

    # Register MCP tools
    logger.info("Registering X/Twitter tools...")
    register_x_tools(mcp)

    logger.info("Registering LinkedIn tools...")
    register_linkedin_tools(mcp)

    # Add health check endpoints
    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> PlainTextResponse:
        """Basic health check endpoint"""
        return PlainTextResponse("OK")

    @mcp.custom_route("/healthz", methods=["GET"])
    async def health_check_k8s(request: Request) -> PlainTextResponse:
        """Kubernetes-style health check endpoint"""
        return PlainTextResponse("OK")

    @mcp.custom_route("/readiness", methods=["GET"])
    async def readiness_check(request: Request) -> JSONResponse:
        """Readiness check endpoint with detailed status"""
        status = {
            "status": "ready",
            "server": config.server_name,
            "tools": ["get_x_posts", "get_linkedin_posts"],
            "authentication": "enabled" if config.server_token else "disabled",
        }
        return JSONResponse(status)

    @mcp.custom_route("/readyz", methods=["GET"])
    async def readiness_check_k8s(request: Request) -> PlainTextResponse:
        """Kubernetes-style readiness check endpoint"""
        return PlainTextResponse("OK")

    logger.info(f"HTTP Social MCP Server created successfully")
    logger.info(f"Server will run on {config.host}:{config.port}")
    logger.info(f"MCP endpoint: http://{config.host}:{config.port}/mcp")
    logger.info(f"Health check: http://{config.host}:{config.port}/health")

    return mcp


def run_http_server():
    """Run the HTTP MCP server"""
    mcp = create_http_mcp_server()

    logger.info("Starting HTTP MCP server...")
    logger.info(f"Authentication: {'Enabled' if config.server_token else 'Disabled'}")
    logger.info(f"Allowed origins: {config.allowed_origins}")

    # Run HTTP server with Streamable HTTP transport
    try:
        mcp.run(
            transport="streamable-http",  # Use Streamable HTTP instead of legacy SSE
            host=config.host,
            port=config.port,
        )
    except Exception as e:
        logger.error(f"Failed to start HTTP server: {e}")
        # Fallback to regular http if streamable_http not available
        try:
            logger.warning("Streamable HTTP not available, trying regular HTTP transport...")
            mcp.run(
                transport="http",
                host=config.host,
                port=config.port,
            )
        except Exception as e2:
            logger.error(f"Both transports failed: {e2}")
            raise


if __name__ == "__main__":
    run_http_server()