"""Entry point for social_mcp_server module"""
from .server import mcp

if __name__ == "__main__":
    mcp.run()