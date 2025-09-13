#!/usr/bin/env python
"""Debug HTTP server issues"""

import requests
import json
import subprocess
import time
import sys


def test_mcp_endpoint():
    """Test MCP endpoint and show full error"""
    print("🔍 Debugging MCP Endpoint Issues")
    print("-" * 50)

    # Start server first
    process = subprocess.Popen(
        ["uv", "run", "social-mcp-server", "--http", "--port", "8002", "--debug"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"SERVER_TOKEN": "test-token-123"}
    )

    time.sleep(3)

    try:
        # Test 1: Simple health check
        print("1. Testing health endpoint...")
        health_response = requests.get("http://127.0.0.1:8002/health")
        print(f"   Health: {health_response.status_code} - {health_response.text}")

        # Test 2: MCP endpoint with minimal request
        print("\\n2. Testing MCP endpoint...")
        mcp_response = requests.post(
            "http://127.0.0.1:8002/mcp",
            data=json.dumps({
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"}
                },
                "id": 1
            }),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer test-token-123"
            }
        )

        print(f"   Status: {mcp_response.status_code}")
        print(f"   Headers: {dict(mcp_response.headers)}")
        print(f"   Body: {mcp_response.text}")

        # Test 3: CORS preflight
        print("\\n3. Testing CORS preflight...")
        cors_response = requests.options(
            "http://127.0.0.1:8002/mcp",
            headers={
                "Origin": "https://chat.mistral.ai",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
        )

        print(f"   CORS Status: {cors_response.status_code}")
        print(f"   CORS Headers: {dict(cors_response.headers)}")

        # Test 4: Check what methods are allowed
        print("\\n4. Testing allowed methods...")
        for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            try:
                resp = requests.request(method, "http://127.0.0.1:8002/mcp", timeout=1)
                print(f"   {method}: {resp.status_code}")
            except:
                print(f"   {method}: Failed")

    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except:
            process.kill()


if __name__ == "__main__":
    test_mcp_endpoint()