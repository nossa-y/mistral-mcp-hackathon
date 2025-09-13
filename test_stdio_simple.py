#!/usr/bin/env python
"""Simple test of FastMCP stdio behavior"""

import asyncio
import json
import sys
from fastmcp import FastMCP

async def main():
    mcp = FastMCP("Test Server")

    @mcp.tool()
    def test_tool(message: str = "hello") -> str:
        """A simple test tool"""
        return f"Response: {message}"

    print("Starting test server with stdio...", file=sys.stderr)

    # This should handle stdio communication
    await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())