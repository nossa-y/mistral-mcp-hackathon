#!/usr/bin/env python
"""Test FastMCP HTTP server with proper SSE handling"""

import requests
import json
import subprocess
import time
import sys
from typing import Iterator


def test_sse_connection():
    """Test SSE connection to MCP server"""
    print("🌊 Testing FastMCP SSE Connection")
    print("-" * 50)

    # Start server
    process = subprocess.Popen(
        ["uv", "run", "social-mcp-server", "--http", "--port", "8003", "--debug"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(3)

    try:
        # Test health first
        health = requests.get("http://127.0.0.1:8003/health")
        print(f"✅ Health check: {health.status_code}")

        # Test SSE connection
        print("\\n🔗 Testing SSE MCP connection...")

        # Create a streaming request
        response = requests.post(
            "http://127.0.0.1:8003/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                },
                "id": 1
            },
            headers={
                "Accept": "text/event-stream",
                "Content-Type": "application/json",
            },
            stream=True,
            timeout=10
        )

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("\\n📡 SSE Data:")

            # Read SSE stream
            for i, line in enumerate(response.iter_lines(decode_unicode=True)):
                if i > 10:  # Limit output
                    break
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"❌ Failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except:
            process.kill()


def test_le_chat_config():
    """Show Le Chat configuration for SSE transport"""
    print("\\n📋 Le Chat Configuration for FastMCP SSE")
    print("-" * 50)

    config = {
        "mcpServers": {
            "social-mcp": {
                "url": "http://localhost:8000/mcp",
                "headers": {
                    "Accept": "text/event-stream",
                    "Content-Type": "application/json"
                }
            }
        }
    }

    print("Configuration for Le Chat:")
    print(json.dumps(config, indent=2))

    config_with_auth = {
        "mcpServers": {
            "social-mcp": {
                "url": "http://localhost:8000/mcp",
                "headers": {
                    "Accept": "text/event-stream",
                    "Content-Type": "application/json",
                    "Authorization": "Bearer your-token-here"
                }
            }
        }
    }

    print("\\nWith authentication:")
    print(json.dumps(config_with_auth, indent=2))


if __name__ == "__main__":
    test_sse_connection()
    test_le_chat_config()