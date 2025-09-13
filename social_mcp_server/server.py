"""
Social MCP Server for ColdOpen Coach using FastMCP.
Consolidated server that fetches recent posts from both X/Twitter and LinkedIn using Apify.
Returns normalized data for Le Chat integration.
"""

import logging
from fastmcp import FastMCP
from .tools.x_tools import register_x_tools
from .tools.linkedin_tools import register_linkedin_tools

logger = logging.getLogger(__name__)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server instance"""
    logger.info("Creating Social MCP Server...")

    # Initialize FastMCP server
    mcp = FastMCP("Social MCP Server")

    # Register tools
    logger.info("Registering X/Twitter tools...")
    register_x_tools(mcp)

    logger.info("Registering LinkedIn tools...")
    register_linkedin_tools(mcp)

    logger.info("Social MCP Server created successfully with tools registered")
    return mcp


# Create server instance for module-level access
mcp = create_mcp_server()

# Export the FastMCP instance for Lambda usage
app = mcp


def main():
    """Entry point for the CLI script"""
    mcp.run()


if __name__ == "__main__":
    main()