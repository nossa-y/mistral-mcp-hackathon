#!/usr/bin/env python
"""Comprehensive validation script for Le Chat integration"""

import json
import asyncio
import subprocess
import sys
from pathlib import Path


def test_server_startup():
    """Test that the server starts correctly"""
    print("🚀 Testing Server Startup")
    print("-" * 40)

    try:
        # Test main module startup
        result = subprocess.run(
            ["uv", "run", "python", "-c", "from social_mcp_server.server import mcp; print('✓ Server imports successfully')"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("✅ Server module imports correctly")
        else:
            print(f"❌ Server import failed: {result.stderr}")
            return False

        # Test CLI entry point
        result = subprocess.run(
            ["uv", "run", "social-mcp-server", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("✅ CLI entry point works")
            print(f"   Version: {result.stdout.strip()}")
        else:
            print(f"❌ CLI entry point failed: {result.stderr}")
            return False

        return True

    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False


async def test_tools_registration():
    """Test that tools are properly registered"""
    print("\\n🔧 Testing Tools Registration")
    print("-" * 40)

    try:
        from social_mcp_server.server import create_mcp_server

        # Create fresh server instance
        mcp = create_mcp_server()

        # Get registered tools
        tools = await mcp.get_tools()

        expected_tools = {"get_x_posts", "get_linkedin_posts"}
        found_tools = set(tools.keys())

        print(f"✅ Found {len(tools)} tools: {', '.join(found_tools)}")

        if expected_tools.issubset(found_tools):
            print("✅ All expected tools are registered")
        else:
            missing = expected_tools - found_tools
            print(f"❌ Missing tools: {missing}")
            return False

        # Test tool descriptions
        for name, tool in tools.items():
            if hasattr(tool, 'description') and tool.description:
                print(f"   - {name}: {tool.description[:50]}...")
            else:
                print(f"   - {name}: [No description]")

        return True

    except Exception as e:
        print(f"❌ Tools registration test failed: {e}")
        return False


def test_lechat_config():
    """Test Le Chat configuration format"""
    print("\\n📋 Le Chat Configuration")
    print("-" * 40)

    config = {
        "mcpServers": {
            "social-mcp": {
                "command": "uv",
                "args": ["run", "python", "-m", "social_mcp_server"],
                "cwd": str(Path.cwd()),
                "env": {
                    "APIFY_TOKEN": "${APIFY_TOKEN}"
                }
            }
        }
    }

    print("✅ Le Chat configuration format:")
    print(json.dumps(config, indent=2))

    # Alternative with CLI entry point
    config_cli = {
        "mcpServers": {
            "social-mcp": {
                "command": "uv",
                "args": ["run", "social-mcp-server"],
                "cwd": str(Path.cwd()),
                "env": {
                    "APIFY_TOKEN": "${APIFY_TOKEN}"
                }
            }
        }
    }

    print("\\n✅ Alternative with CLI entry point:")
    print(json.dumps(config_cli, indent=2))

    return True


def test_environment_setup():
    """Test environment variable setup"""
    print("\\n🌍 Environment Setup")
    print("-" * 40)

    import os
    from social_mcp_server.config import config

    print("Environment Variables:")
    print(f"   APIFY_TOKEN: {'✅ Set' if config.apify_token else '❌ Missing'}")
    print(f"   APIFY_TWITTER_ACTOR: {config.apify_twitter_actor}")
    print(f"   APIFY_LINKEDIN_POSTS_ACTOR: {config.apify_linkedin_posts_actor}")

    if not config.apify_token:
        print("\\n⚠️  To use with real data, set APIFY_TOKEN:")
        print("   export APIFY_TOKEN=your_token_here")
        print("   # Then restart Le Chat")

    return True


async def run_all_tests():
    """Run all validation tests"""
    print("🧪 Social MCP Server - Le Chat Integration Validation")
    print("=" * 60)

    tests = [
        ("Server Startup", test_server_startup),
        ("Tools Registration", test_tools_registration),
        ("Le Chat Config", test_lechat_config),
        ("Environment Setup", test_environment_setup),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("\\n🎉 All tests passed! Server is ready for Le Chat integration.")
        print("\\nNext steps:")
        print("1. Set APIFY_TOKEN environment variable")
        print("2. Add the configuration to Le Chat")
        print("3. Restart Le Chat to load the server")
        return True
    else:
        print(f"\\n💥 {total - passed} test(s) failed. Please fix issues before using with Le Chat.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)