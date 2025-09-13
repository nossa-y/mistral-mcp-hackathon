"""
Social MCP Server for ColdOpen Coach using FastMCP.
Consolidated server that fetches recent posts from both X/Twitter and LinkedIn using Apify.
Returns normalized data for Le Chat integration.
"""

from fastmcp import FastMCP
from social_mcp_server.tools.x_tools import register_x_tools
from social_mcp_server.tools.linkedin_tools import register_linkedin_tools

# Initialize FastMCP server
mcp = FastMCP("Social MCP Server")

# Register tools
register_x_tools(mcp)
register_linkedin_tools(mcp)

# Export the FastMCP instance for Lambda usage
app = mcp


def main():
    """Entry point for the CLI script"""
    mcp.run()


if __name__ == "__main__":
    main()