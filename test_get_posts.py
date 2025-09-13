#!/usr/bin/env python3
"""Test MCP server tool calls via SSE"""

import json
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test_get_x_posts():
    """Test getting X posts from Arthur Mensch"""

    # Connect to the SSE server
    url = "http://127.0.0.1:8080/sse"

    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            print("Testing get_x_posts for Arthur Mensch (@arthurmensch)")

            # Call the get_x_posts tool
            result = await session.call_tool(
                "get_x_posts",
                arguments={
                    "handle": "arthurmensch",
                    "limit": 5
                }
            )

            print("Result:")
            for content in result.content:
                if hasattr(content, 'text'):
                    print(content.text)
                else:
                    print(str(content))

if __name__ == "__main__":
    asyncio.run(test_get_x_posts())