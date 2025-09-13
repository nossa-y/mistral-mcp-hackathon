#!/usr/bin/env python
"""Test MCP protocol communication with proper format"""

import json
import subprocess
import time
import signal
import os

def test_mcp_protocol():
    print("🔌 Testing MCP Protocol Communication")
    print("=" * 50)

    # Start the server process
    process = subprocess.Popen(
        ["uv", "run", "python", "-m", "social_mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # Line buffered
        universal_newlines=True
    )

    try:
        # Wait for server to start
        time.sleep(2)

        # Send initialization
        print("\n1. Sending initialization...")
        init_msg = json.dumps({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            },
            "id": 1
        }) + "\\n"

        process.stdin.write(init_msg)
        process.stdin.flush()

        # Send tools/list request
        print("2. Sending tools/list...")
        tools_msg = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }) + "\\n"

        process.stdin.write(tools_msg)
        process.stdin.flush()

        # Read responses with timeout
        print("3. Reading responses...")
        responses = []

        # Read for a few seconds
        for _ in range(10):
            line = process.stdout.readline()
            if line.strip():
                if line.startswith('{'):
                    try:
                        resp = json.loads(line)
                        responses.append(resp)
                        print(f"   Response: {json.dumps(resp, indent=2)}")
                    except json.JSONDecodeError:
                        pass
                else:
                    if "Starting MCP server" in line:
                        print("   ✓ Server started")
            if len(responses) >= 2:
                break

        # Check if we got tools list
        tools_response = None
        for resp in responses:
            if resp.get("id") == 2:  # tools/list response
                tools_response = resp
                break

        if tools_response:
            if "result" in tools_response:
                tools = tools_response["result"].get("tools", [])
                print(f"\\n✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool.get('name', 'unnamed')}")
                return True
            else:
                print(f"\\n❌ Tools request failed: {tools_response.get('error', 'unknown error')}")
                return False
        else:
            print("\\n❌ No tools response received")
            return False

    finally:
        # Clean up
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()

if __name__ == "__main__":
    success = test_mcp_protocol()
    if success:
        print("\\n🎉 MCP server is working correctly!")
    else:
        print("\\n💥 MCP server has issues")