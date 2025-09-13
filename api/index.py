"""Vercel serverless function entry point for MCP server"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from social_mcp_server.server import mcp

# Set environment for HTTP mode
os.environ["HTTP_MODE"] = "true"

# Export the FastMCP HTTP app for Vercel (modern alternative to deprecated sse_app)
app = mcp.http_app