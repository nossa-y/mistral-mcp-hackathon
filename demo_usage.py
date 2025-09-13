#!/usr/bin/env python3
"""
Demo showing exactly how the MCP servers should be called and what output they produce.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from mcp_servers.mcp_linkedin.server import get_recent_posts as linkedin_get_posts
from mcp_servers.mcp_x.server import get_recent_posts as twitter_get_posts

def demo_linkedin_call():
    """Demo LinkedIn MCP server call"""
    print("🔗 LinkedIn MCP Server Demo")
    print("=" * 50)

    # Input parameters
    profile_url = "https://linkedin.com/in/reidhoffman"
    limit = 5

    print(f"INPUT:")
    print(f"  profile_url: {profile_url}")
    print(f"  limit: {limit}")
    print()

    # This is what would happen (but will fail without real Apify access)
    print("EXPECTED OUTPUT (without real API):")
    mock_output = '''Error: API_ERROR - APIFY_TOKEN environment variable is required'''
    print(f"  {mock_output}")
    print()

    # Show what successful output would look like
    print("SUCCESSFUL OUTPUT WOULD BE:")
    print("  JSON Bundle with:")
    print("  - person: { name, platform, profile_url, headline_or_bio }")
    print("  - posts: [{ platform, post_id, url, text, hashtags, mentions, engagement }]")
    print("  - meta: { source, fetched_at_iso, limit, total_found }")
    print()

def demo_twitter_call():
    """Demo Twitter MCP server call"""
    print("🐦 Twitter MCP Server Demo")
    print("=" * 50)

    # Input parameters
    handle = "elonmusk"  # No @ symbol needed
    limit = 10

    print(f"INPUT:")
    print(f"  handle: {handle}")
    print(f"  limit: {limit}")
    print()

    print("EXPECTED OUTPUT (without real API):")
    mock_output = '''Error: API_ERROR - APIFY_TOKEN environment variable is required'''
    print(f"  {mock_output}")
    print()

    print("SUCCESSFUL OUTPUT WOULD BE:")
    print("  JSON Bundle with:")
    print("  - person: { name: '@elonmusk', platform: 'X', handle: 'elonmusk', profile_url }")
    print("  - posts: [{ platform: 'X', post_id, url, text, hashtags, mentions, engagement }]")
    print("  - meta: { source: 'mcp_x_fastmcp', fetched_at_iso, limit, total_found }")
    print()

def show_mcp_client_usage():
    """Show how an MCP client would call these servers"""
    print("📡 MCP Client Usage Example")
    print("=" * 50)

    print("When connected to the MCP servers, a client would call:")
    print()

    print("LINKEDIN SERVER:")
    print("  Method: call_tool")
    print("  Tool name: 'get_recent_posts'")
    print("  Arguments: {")
    print("    'profile_url': 'https://linkedin.com/in/reidhoffman',")
    print("    'limit': 10")
    print("  }")
    print()

    print("TWITTER SERVER:")
    print("  Method: call_tool")
    print("  Tool name: 'get_recent_posts'")
    print("  Arguments: {")
    print("    'handle': 'elonmusk',")
    print("    'limit': 20")
    print("  }")
    print()

    print("JSON-RPC format (over stdio):")
    print('''{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_recent_posts",
    "arguments": {
      "profile_url": "https://linkedin.com/in/reidhoffman",
      "limit": 10
    }
  }
}''')

def main():
    """Run all demos"""
    print("🚀 MCP Servers Input/Output Demo\n")

    demo_linkedin_call()
    demo_twitter_call()
    show_mcp_client_usage()

    print("\n" + "=" * 60)
    print("💡 To actually use these servers:")
    print("1. Set APIFY_TOKEN environment variable")
    print("2. Set APIFY_LINKEDIN_POSTS_ACTOR environment variable")
    print("3. Set APIFY_TWITTER_ACTOR environment variable (or use default)")
    print("4. Connect via MCP client (stdio transport)")
    print("5. Call tools with the parameters shown above")

if __name__ == "__main__":
    main()