#!/usr/bin/env python
"""Simple test to verify tools are working"""

import asyncio
import os
from fastmcp import FastMCP
from social_mcp_server.tools.x_tools import register_x_tools
from social_mcp_server.tools.linkedin_tools import register_linkedin_tools

async def test_tools():
    print("🔧 Testing MCP Tools Registration and Functionality")
    print("=" * 60)

    # Create fresh instance
    test_mcp = FastMCP('Test Server')
    register_x_tools(test_mcp)
    register_linkedin_tools(test_mcp)

    # Get registered tools
    tools = await test_mcp.get_tools()
    print(f"\n✅ Tools registered: {len(tools)}")

    for name, tool in tools.items():
        print(f"\n📋 Tool: {name}")
        print(f"   Description: {tool.description.split('.')[0]}...")
        print(f"   Enabled: {tool.enabled}")

        # Check if tool has proper input schema
        if hasattr(tool, 'input_schema'):
            schema = tool.input_schema
            if hasattr(schema, 'model_fields'):
                fields = list(schema.model_fields.keys())
                print(f"   Parameters: {', '.join(fields)}")

    # Test if tools can be called (without actually calling external APIs)
    print(f"\n🧪 Testing tool call capability...")

    # Test without APIFY_TOKEN to see if validation works
    has_token = bool(os.getenv("APIFY_TOKEN"))
    print(f"   APIFY_TOKEN present: {has_token}")

    if not has_token:
        print("   ⚠️  No APIFY_TOKEN - tools will return error (this is expected)")

        # Try calling a tool to see if it handles missing token properly
        try:
            get_x_posts = tools['get_x_posts'].fn
            result = get_x_posts("test_handle", 5)
            print(f"   Tool response (no token): {result[:100]}...")
            if "APIFY_TOKEN" in result:
                print("   ✅ Tool correctly validates token requirement")
        except Exception as e:
            print(f"   Tool call error: {e}")
    else:
        print("   ✅ APIFY_TOKEN available - tools should work with real data")

    return True

if __name__ == "__main__":
    asyncio.run(test_tools())