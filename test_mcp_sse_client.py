#!/usr/bin/env python3
"""Simple MCP SSE client to test the server"""

import json
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test_mcp_sse_server():
    """Test the MCP server via SSE by listing tools"""

    # Connect to the SSE server
    url = "http://127.0.0.1:8080/sse"

    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # List available tools
            result = await session.list_tools()

            print("Available tools (via SSE):")
            for tool in result.tools:
                print(f"- {tool.name}: {tool.description}")
                if tool.inputSchema:
                    print(f"  Input: {json.dumps(tool.inputSchema, indent=2)}")
                print()

if __name__ == "__main__":
    asyncio.run(test_mcp_sse_server())