#!/usr/bin/env python3
"""
Real MCP Server Testing Script
Test LinkedIn and X/Twitter MCP servers with actual data
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_servers'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def test_x_server():
    """Test X/Twitter MCP server with real data"""
    print("=" * 60)
    print("🐦 TESTING X/TWITTER MCP SERVER")
    print("=" * 60)

    try:
        from mcp_servers.mcp_x.server import mcp as x_mcp

        # Test with a well-known public Twitter account
        test_handle = "elonmusk"  # High activity, public account
        limit = 5

        print(f"📡 Fetching recent posts for @{test_handle} (limit: {limit})")
        print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")

        # Get the tool function directly
        tools = x_mcp.get_tools()
        get_posts_tool = None

        for tool in tools:
            if tool.name == "get_recent_posts":
                # Get the actual function from the tool manager
                get_posts_tool = x_mcp._tool_manager._tools[tool.name]
                break

        if not get_posts_tool:
            print("❌ ERROR: get_recent_posts tool not found")
            print(f"Available tools: {[t.name for t in tools]}")
            return False

        # Call the function
        result = get_posts_tool(handle=test_handle, limit=limit)

        print(f"⏰ Completed at: {datetime.now().strftime('%H:%M:%S')}")

        # Check if result is an error
        if result.startswith("Error:"):
            print(f"❌ X Server Error: {result}")
            return False

        # Parse and display results
        try:
            data = json.loads(result)
            posts_count = len(data.get('posts', []))
            person = data.get('person', {})
            meta = data.get('meta', {})

            print(f"✅ SUCCESS! Retrieved {posts_count} posts")
            print(f"👤 Profile: {person.get('name', 'Unknown')}")
            print(f"🔗 URL: {person.get('profile_url', 'Unknown')}")
            print(f"📊 Source: {meta.get('source', 'Unknown')}")

            # Show first post as sample
            if data.get('posts'):
                first_post = data['posts'][0]
                print(f"\n📝 Sample Post:")
                print(f"   Text: {first_post.get('text', '')[:100]}...")
                print(f"   Engagement: {first_post.get('engagement', {})}")
                print(f"   Themes: {first_post.get('inferred_themes', [])}")

            return True

        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Raw result: {result[:200]}...")
            return False

    except Exception as e:
        print(f"❌ X Server Test Failed: {e}")
        return False

def test_linkedin_server():
    """Test LinkedIn MCP server with real data"""
    print("\n" + "=" * 60)
    print("💼 TESTING LINKEDIN MCP SERVER")
    print("=" * 60)

    try:
        from mcp_servers.mcp_linkedin.server import mcp as linkedin_mcp

        # Test with a well-known public LinkedIn profile
        test_profile = "https://linkedin.com/in/reidhoffman"  # LinkedIn co-founder, public profile
        limit = 5

        print(f"📡 Fetching recent posts for {test_profile} (limit: {limit})")
        print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")

        # Get the tool function directly
        tools = linkedin_mcp.get_tools()
        get_posts_tool = None

        for tool in tools:
            if tool.name == "get_recent_posts":
                # Get the actual function from the tool manager
                get_posts_tool = linkedin_mcp._tool_manager._tools[tool.name]
                break

        if not get_posts_tool:
            print("❌ ERROR: get_recent_posts tool not found")
            print(f"Available tools: {[t.name for t in tools]}")
            return False

        # Call the function
        result = get_posts_tool(profile_url=test_profile, limit=limit)

        print(f"⏰ Completed at: {datetime.now().strftime('%H:%M:%S')}")

        # Check if result is an error
        if result.startswith("Error:"):
            print(f"❌ LinkedIn Server Error: {result}")
            return False

        # Parse and display results
        try:
            data = json.loads(result)
            posts_count = len(data.get('posts', []))
            person = data.get('person', {})
            meta = data.get('meta', {})

            print(f"✅ SUCCESS! Retrieved {posts_count} posts")
            print(f"👤 Profile: {person.get('name', 'Unknown')}")
            print(f"🔗 URL: {person.get('profile_url', 'Unknown')}")
            print(f"📊 Source: {meta.get('source', 'Unknown')}")

            # Show first post as sample
            if data.get('posts'):
                first_post = data['posts'][0]
                print(f"\n📝 Sample Post:")
                print(f"   Text: {first_post.get('text', '')[:100]}...")
                print(f"   Engagement: {first_post.get('engagement', {})}")
                print(f"   Themes: {first_post.get('inferred_themes', [])}")

            return True

        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Raw result: {result[:200]}...")
            return False

    except Exception as e:
        print(f"❌ LinkedIn Server Test Failed: {e}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    print("🔧 ENVIRONMENT CHECK")
    print("=" * 60)

    required_vars = {
        "APIFY_TOKEN": "Apify API token for both X and LinkedIn scraping"
    }

    missing_vars = []

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * (len(value) - 4) + value[-4:]} ({description})")
        else:
            print(f"❌ {var}: Not set ({description})")
            missing_vars.append(var)

    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file before running tests.")
        return False

    return True

def main():
    """Run all MCP server tests"""
    print("🚀 MCP SERVER REAL DATA TESTING")
    print("Testing with actual API calls - no mocks!")
    print("=" * 60)

    # Check environment first
    if not check_environment():
        print("\n❌ Environment check failed. Exiting.")
        return False

    results = []

    # Test X/Twitter server
    print("\n")
    x_success = test_x_server()
    results.append(("X/Twitter", x_success))

    # Test LinkedIn server
    print("\n")
    linkedin_success = test_linkedin_server()
    results.append(("LinkedIn", linkedin_success))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    for service, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{service:15} {status}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED! Both MCP servers are working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Check the error messages above.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)