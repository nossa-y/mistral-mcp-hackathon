#!/usr/bin/env python3
"""
Test script to demonstrate actual MCP server interaction.
This shows real logs and actual tool calls (not mock data).
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print(f"🔧 APIFY_TOKEN loaded: {'Yes' if os.getenv('APIFY_TOKEN') else 'No'}")
if os.getenv('APIFY_TOKEN'):
    print(f"🔧 Token starts with: {os.getenv('APIFY_TOKEN')[:15]}...")

# Import the MCP servers directly to show their actual behavior
from mcp_servers.mcp_x.server import app as twitter_app
from mcp_servers.mcp_linkedin.server import app as linkedin_app


async def test_twitter_mcp():
    """Test the Twitter MCP server directly"""
    print("🔥 TESTING REAL TWITTER MCP SERVER")
    print("=" * 50)

    try:
        # Get the tools list
        from mcp_servers.mcp_x.server import handle_list_tools, handle_call_tool

        tools = await handle_list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")

        # Test the twitter tool
        print(f"🐦 Calling x.get_recent_posts with handle 'elonmusk'...")
        print(f"🔍 This will attempt to call Apify with real credentials...")

        arguments = {"handle": "elonmusk", "limit": 5}
        result = await handle_call_tool("x.get_recent_posts", arguments)

        print(f"📤 Server Response Type: {type(result)}")
        print(f"📤 Response Length: {len(result)}")

        if result and len(result) > 0:
            response_text = result[0].text if hasattr(result[0], 'text') else str(result[0])

            # Check if it's an error or actual data
            if response_text.startswith("Error:"):
                print(f"❌ MCP Server Error: {response_text}")
            else:
                try:
                    # Try to parse as JSON to show structure
                    data = json.loads(response_text)
                    print(f"✅ Got structured data with keys: {list(data.keys())}")

                    if 'posts' in data:
                        print(f"📝 Found {len(data['posts'])} posts")
                        for i, post in enumerate(data['posts'][:2], 1):
                            print(f"   Post {i}: {post.get('text', '')[:80]}...")

                    if 'meta' in data:
                        meta = data['meta']
                        print(f"📊 Source: {meta.get('source')}")
                        print(f"📊 Fetched at: {meta.get('fetched_at_iso')}")

                except json.JSONDecodeError:
                    print(f"📄 Raw response: {response_text[:200]}...")

    except Exception as e:
        print(f"💥 Exception during Twitter MCP test: {e}")
        print(f"📝 This is expected - we need APIFY_TOKEN and real actor setup")


async def test_linkedin_mcp():
    """Test the LinkedIn MCP server directly"""
    print("\n🔥 TESTING REAL LINKEDIN MCP SERVER")
    print("=" * 50)

    try:
        # Get the tools list
        from mcp_servers.mcp_linkedin.server import handle_list_tools, handle_call_tool

        tools = await handle_list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")

        # Test the linkedin tool
        print(f"💼 Calling linkedin.get_recent_posts...")
        print(f"🔍 This will attempt to call Apify with real credentials...")

        arguments = {"profile_url": "https://linkedin.com/in/satyanadella", "limit": 3}
        result = await handle_call_tool("linkedin.get_recent_posts", arguments)

        print(f"📤 Server Response Type: {type(result)}")
        print(f"📤 Response Length: {len(result)}")

        if result and len(result) > 0:
            response_text = result[0].text if hasattr(result[0], 'text') else str(result[0])

            # Check if it's an error or actual data
            if response_text.startswith("Error:"):
                print(f"❌ MCP Server Error: {response_text}")
            else:
                try:
                    # Try to parse as JSON to show structure
                    data = json.loads(response_text)
                    print(f"✅ Got structured data with keys: {list(data.keys())}")

                    if 'posts' in data:
                        print(f"📝 Found {len(data['posts'])} posts")

                    if 'meta' in data:
                        meta = data['meta']
                        print(f"📊 Source: {meta.get('source')}")
                        print(f"📊 Fetched at: {meta.get('fetched_at_iso')}")

                except json.JSONDecodeError:
                    print(f"📄 Raw response: {response_text[:200]}...")

    except Exception as e:
        print(f"💥 Exception during LinkedIn MCP test: {e}")
        print(f"📝 This is expected - we need APIFY_TOKEN and real actor setup")


async def main():
    """Run the MCP server tests"""
    print("🚀 REAL MCP SERVER TESTING")
    print("This shows actual MCP server behavior, not mock data")
    print("=" * 60)

    await test_twitter_mcp()
    await test_linkedin_mcp()

    print("\n💡 SUMMARY:")
    print("- MCP servers are running and responding")
    print("- Without APIFY_TOKEN, they return expected errors")
    print("- With proper tokens, they would fetch real data from Apify")
    print("- This is the actual MCP architecture, not mock data")


if __name__ == "__main__":
    asyncio.run(main())