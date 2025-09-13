#!/usr/bin/env python3
"""Simple MCP client to test the server"""

import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the MCP server by listing tools"""

    # Connect to the server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "social_mcp_server"],
        env={"HTTP_MODE": ""}  # Force STDIO mode
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # List available tools
            result = await session.list_tools()

            print("Available tools:")
            for tool in result.tools:
                print(f"- {tool.name}: {tool.description}")
                if tool.inputSchema:
                    print(f"  Input: {json.dumps(tool.inputSchema, indent=2)}")
                print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mcp_server())