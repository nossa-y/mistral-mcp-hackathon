#!/usr/bin/env python3
"""Test MCP server via ngrok endpoint"""

import json
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test_ngrok_mcp():
    """Test MCP server via ngrok URL"""

    # Connect to the ngrok SSE server
    ngrok_url = "https://03e94b84827c.ngrok-free.app/sse"

    print(f"Testing MCP server via ngrok: {ngrok_url}")

    try:
        async with sse_client(ngrok_url) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                print("\n✅ Successfully connected to ngrok MCP server!")

                # List available tools
                tools_result = await session.list_tools()
                print(f"\n📋 Available tools ({len(tools_result.tools)}):")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")

                # Test X/Twitter tool
                print("\n🐦 Testing X/Twitter posts for @arthurmensch...")
                x_result = await session.call_tool(
                    "get_x_posts",
                    arguments={
                        "handle": "arthurmensch",
                        "limit": 2
                    }
                )

                print("✅ X/Twitter result received!")
                for content in x_result.content:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        print(f"  Found {len(data['posts'])} posts from @{data['person']['handle']}")
                        break

                # Test LinkedIn tool
                print("\n💼 Testing LinkedIn posts for Arthur Mensch...")
                linkedin_result = await session.call_tool(
                    "get_linkedin_posts",
                    arguments={
                        "profile_url": "https://www.linkedin.com/in/arthur-mensch/",
                        "limit": 2
                    }
                )

                print("✅ LinkedIn result received!")
                for content in linkedin_result.content:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        print(f"  Found {len(data['posts'])} posts from LinkedIn profile")
                        break

                print("\n🎉 All tests successful via ngrok!")

    except Exception as e:
        print(f"❌ Error connecting to ngrok MCP server: {e}")

if __name__ == "__main__":
    asyncio.run(test_ngrok_mcp())