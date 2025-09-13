#!/usr/bin/env python3
"""
Simple test to verify MCP servers are working.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_linkedin_server():
    """Test LinkedIn server functionality"""
    print("🔗 Testing LinkedIn MCP Server...")

    try:
        from mcp_servers.mcp_linkedin.server import extract_linkedin_username, normalize_linkedin_post, ErrorType

        # Test username extraction
        username = extract_linkedin_username("https://linkedin.com/in/reidhoffman")
        print(f"✅ Username extraction works: {username}")

        # Test post normalization
        sample_post = {
            "postId": "123",
            "postUrl": "https://linkedin.com/posts/test",
            "text": "This is a test LinkedIn post #networking",
            "postedAt": "2024-01-01T12:00:00Z",
            "likesCount": 42,
            "commentsCount": 5,
            "sharesCount": 2
        }

        post = normalize_linkedin_post(sample_post, "https://linkedin.com/in/reidhoffman")
        print(f"✅ Post normalization works: Platform={post.platform}, ID={post.post_id}")

        print("✅ LinkedIn server tests passed!\n")
        return True

    except Exception as e:
        print(f"❌ LinkedIn server test failed: {e}\n")
        return False

def test_x_server():
    """Test X/Twitter server functionality"""
    print("🐦 Testing X/Twitter MCP Server...")

    try:
        from mcp_servers.mcp_x.server import normalize_x_post, ErrorType

        # Test post normalization
        sample_post = {
            "id": "123456789",
            "text": "This is a test tweet #testing @username",
            "createdAt": "2024-01-01T12:00:00Z",
            "likeCount": 100,
            "retweetCount": 25,
            "replyCount": 10,
            "quoteCount": 5,
            "entities": {
                "hashtags": [{"text": "testing"}],
                "user_mentions": [{"screen_name": "username"}]
            }
        }

        post = normalize_x_post(sample_post, "testuser")
        print(f"✅ Post normalization works: Platform={post.platform}, ID={post.post_id}")
        print(f"✅ Hashtags extracted: {post.hashtags}")
        print(f"✅ Mentions extracted: {post.mentions}")

        print("✅ X/Twitter server tests passed!\n")
        return True

    except Exception as e:
        print(f"❌ X/Twitter server test failed: {e}\n")
        return False

def test_shared_models():
    """Test shared models"""
    print("📦 Testing Shared Models...")

    try:
        from shared.models import Bundle, Person, Post, Meta, Platform

        # Create a test person
        person = Person(
            name="Test User",
            platform=Platform.LINKEDIN,
            profile_url="https://linkedin.com/in/testuser",
            headline_or_bio="Test bio"
        )

        # Create a test post
        post = Post(
            platform=Platform.LINKEDIN,
            post_id="123",
            url="https://linkedin.com/posts/test",
            created_at_iso="2024-01-01T12:00:00Z",
            text="Test post",
            hashtags=["#test"],
            mentions=["@user"],
            engagement={"likes": 10},
            inferred_themes=[]
        )

        # Create metadata
        meta = Meta(
            source="test",
            fetched_at_iso="2024-01-01T12:00:00Z",
            limit=10,
            total_found=1
        )

        # Create bundle
        bundle = Bundle(
            person=person,
            posts=[post],
            meta=meta
        )

        # Test JSON serialization
        json_data = bundle.model_dump_json()
        print(f"✅ Bundle serialization works: {len(json_data)} chars")

        print("✅ Shared models tests passed!\n")
        return True

    except Exception as e:
        print(f"❌ Shared models test failed: {e}\n")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing MCP Servers for ColdOpen Coach\n")

    results = []
    results.append(test_shared_models())
    results.append(test_linkedin_server())
    results.append(test_x_server())

    if all(results):
        print("🎉 All tests passed! The MCP servers are ready to use.")
        print("\n📋 Available servers:")
        print("• LinkedIn MCP Server: python -m mcp_servers.mcp_linkedin.server")
        print("• X/Twitter MCP Server: python -m mcp_servers.mcp_x.server")
        print("\n💡 Use 'fastmcp dev' to interactively test the servers.")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()