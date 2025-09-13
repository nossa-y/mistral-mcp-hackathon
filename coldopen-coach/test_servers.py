#!/usr/bin/env python3
"""
Simple test script to demonstrate MCP server functionality.
"""

import asyncio
import json
from mcp import ClientSession, stdio_client
from mcp.client.stdio import stdio_client

async def test_linkedin_server():
    """Test the LinkedIn MCP server"""
    print("🔗 Testing LinkedIn MCP Server...")

    # Start the server
    server_process = await asyncio.create_subprocess_exec(
        "python", "-m", "mcp_servers.mcp_linkedin.server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        # Connect to the server
        read_stream = server_process.stdout
        write_stream = server_process.stdin

        async with stdio_client(read_stream, write_stream) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                # List available tools
                tools_result = await session.list_tools()
                print(f"Available tools: {[tool.name for tool in tools_result.tools]}")

                # Test calling a tool (this will fail without real LinkedIn API access)
                try:
                    result = await session.call_tool(
                        "get_recent_posts",
                        {"profile_url": "https://linkedin.com/in/reidhoffman", "limit": 5}
                    )
                    print(f"Tool result: {result}")
                except Exception as e:
                    print(f"Tool call failed (expected): {e}")

    finally:
        server_process.terminate()
        await server_process.wait()

async def test_x_server():
    """Test the X/Twitter MCP server"""
    print("\n🐦 Testing X/Twitter MCP Server...")

    # Start the server
    server_process = await asyncio.create_subprocess_exec(
        "python", "-m", "mcp_servers.mcp_x.server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        # Connect to the server
        read_stream = server_process.stdout
        write_stream = server_process.stdin

        async with stdio_client(read_stream, write_stream) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                # List available tools
                tools_result = await session.list_tools()
                print(f"Available tools: {[tool.name for tool in tools_result.tools]}")

                # Test calling a tool (this will fail without real Apify API access)
                try:
                    result = await session.call_tool(
                        "get_recent_posts",
                        {"handle": "elonmusk", "limit": 5}
                    )
                    print(f"Tool result: {result}")
                except Exception as e:
                    print(f"Tool call failed (expected): {e}")

    finally:
        server_process.terminate()
        await server_process.wait()

async def main():
    """Run all tests"""
    print("🚀 Testing MCP Servers for ColdOpen Coach\n")

    await test_linkedin_server()
    await test_x_server()

    print("\n✅ Server tests completed!")

if __name__ == "__main__":
    asyncio.run(main())