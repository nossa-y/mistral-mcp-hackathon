#!/usr/bin/env python
"""Test script to verify MCP server tools are available and working"""

import json
import subprocess
import sys

def send_mcp_request(request):
    """Send a request to the MCP server and get response"""
    process = subprocess.Popen(
        ["uv", "run", "python", "-m", "social_mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate(input=json.dumps(request))

    # Parse response lines (skip non-JSON output)
    responses = []
    for line in stdout.split('\n'):
        if line.strip().startswith('{'):
            try:
                responses.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return responses, stderr

def test_mcp_server():
    print("Testing MCP Server Tools Discovery\n" + "="*50)

    # 1. Initialize connection
    print("\n1. Initializing MCP connection...")
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0.0"}
        },
        "id": 1
    }

    # Create a combined request to get both init and tools list
    combined_input = json.dumps(init_request) + '\n' + json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    })

    process = subprocess.Popen(
        ["uv", "run", "python", "-m", "social_mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate(input=combined_input)

    # Parse all JSON responses
    responses = []
    for line in stdout.split('\n'):
        if line.strip().startswith('{'):
            try:
                responses.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Check initialization
    if responses:
        init_response = responses[0]
        if "result" in init_response:
            caps = init_response["result"].get("capabilities", {})
            tools_cap = caps.get("tools", {})
            print(f"✓ Server initialized successfully")
            print(f"  - Server: {init_response['result'].get('serverInfo', {}).get('name')}")
            print(f"  - Tools capability: {tools_cap}")
        else:
            print(f"✗ Initialization failed: {init_response}")
            return False

    # Check tools list
    if len(responses) > 1:
        tools_response = responses[1]
        if "result" in tools_response:
            tools = tools_response["result"].get("tools", [])
            print(f"\n2. Available tools: {len(tools)}")
            for tool in tools:
                print(f"  - {tool.get('name')}: {tool.get('description', 'No description')[:60]}...")
                if tool.get('inputSchema'):
                    params = tool['inputSchema'].get('properties', {}).keys()
                    print(f"    Parameters: {', '.join(params)}")

            if not tools:
                print("  ⚠️  No tools found - checking server implementation...")
                return False
            return True
        else:
            print(f"✗ Tools list failed: {tools_response}")
            return False
    else:
        print("✗ No tools response received")
        return False

def check_server_directly():
    """Check if tools are registered directly in Python"""
    print("\n3. Direct Python check...")
    try:
        from social_mcp_server.server import mcp

        # Try different ways to find tools
        checks = [
            ("_tools", lambda: hasattr(mcp, '_tools') and mcp._tools),
            ("tools", lambda: hasattr(mcp, 'tools') and mcp.tools),
            ("list_tools", lambda: hasattr(mcp, 'list_tools')),
            ("get_tools", lambda: hasattr(mcp, 'get_tools')),
        ]

        for attr_name, check in checks:
            if check():
                print(f"  ✓ Found {attr_name} attribute")
                if attr_name in ['_tools', 'tools']:
                    tools = getattr(mcp, attr_name)
                    if isinstance(tools, dict):
                        print(f"    Tools: {list(tools.keys())}")
            else:
                print(f"  ✗ No {attr_name} attribute")

        # Check if FastMCP version supports tools
        import fastmcp
        print(f"\n  FastMCP version: {fastmcp.__version__ if hasattr(fastmcp, '__version__') else 'unknown'}")

    except Exception as e:
        print(f"  Error checking server: {e}")

if __name__ == "__main__":
    success = test_mcp_server()
    check_server_directly()

    if success:
        print("\n✅ MCP server tools are available!")
    else:
        print("\n❌ MCP server tools are NOT available - troubleshooting needed")
        sys.exit(1)