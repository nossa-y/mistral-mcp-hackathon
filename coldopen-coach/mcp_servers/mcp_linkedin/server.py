"""
LinkedIn MCP Server for ColdOpen Coach.
Fetches recent posts using Apify and returns normalized data.
"""

import os
import asyncio
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlparse

from apify_client import ApifyClient
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models import Bundle, Person, Post, Meta, Platform
from shared.theme_inference import ThemeInferenceEngine


app = Server("mcp_linkedin")

# Error handling constants
class ErrorType:
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMITED = "RATE_LIMITED"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    PRIVATE_PROFILE = "PRIVATE_PROFILE"
    INVALID_INPUT = "INVALID_INPUT"
    API_ERROR = "API_ERROR"


def get_apify_client() -> ApifyClient:
    """Initialize Apify client with token from environment"""
    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise ValueError("APIFY_TOKEN environment variable is required")
    return ApifyClient(token)


def extract_linkedin_username(profile_url: str) -> Optional[str]:
    """
    Extract LinkedIn username from profile URL.

    Args:
        profile_url: LinkedIn profile URL

    Returns:
        Username or None if invalid
    """
    try:
        # Handle various LinkedIn URL formats
        if not profile_url.startswith(('http://', 'https://')):
            profile_url = f"https://{profile_url}"

        parsed = urlparse(profile_url)
        if 'linkedin.com' not in parsed.netloc:
            return None

        # Extract username from path like /in/username/ or /in/username
        path = parsed.path.strip('/')
        if path.startswith('in/'):
            username = path[3:].strip('/')
            return username if username else None

        return None
    except:
        return None


def normalize_linkedin_post(item: Dict[str, Any], profile_url: str) -> Post:
    """
    Convert Apify LinkedIn actor response item to normalized Post.

    Args:
        item: Raw item from Apify dataset
        profile_url: LinkedIn profile URL for reference

    Returns:
        Normalized Post object
    """
    # Extract basic fields - LinkedIn post structure may vary by actor
    post_id = str(item.get("postId", item.get("id", "")))
    post_url = item.get("postUrl", item.get("url", ""))
    text = item.get("text", item.get("content", ""))
    created_at = item.get("postedAt", item.get("publishedAt", item.get("createdAt", "")))

    # Handle date format
    if created_at:
        try:
            # Try to parse various date formats
            if isinstance(created_at, str):
                if not created_at.endswith('Z') and '+' not in created_at:
                    # Assume UTC if no timezone info
                    created_at = created_at + 'Z'
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_at = dt.isoformat()
        except ValueError:
            # Fallback to current time if parsing fails
            created_at = datetime.now(timezone.utc).isoformat()
    else:
        created_at = datetime.now(timezone.utc).isoformat()

    # Extract hashtags from text
    hashtags = []
    if text:
        hashtag_matches = re.findall(r'#(\w+)', text)
        hashtags = [f"#{tag}" for tag in hashtag_matches]

    # Extract mentions from text
    mentions = []
    if text:
        mention_matches = re.findall(r'@(\w+)', text)
        mentions = mention_matches

    # Extract engagement metrics
    engagement = {
        "likes": item.get("likesCount", item.get("reactions", 0)),
        "comments": item.get("commentsCount", 0),
        "shares": item.get("sharesCount", item.get("reposts", 0))
    }

    post = Post(
        platform=Platform.LINKEDIN,
        post_id=post_id,
        url=post_url,
        created_at_iso=created_at,
        text=text,
        hashtags=hashtags,
        mentions=mentions,
        engagement=engagement,
        inferred_themes=[]  # Will be populated by theme inference
    )

    return post


@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="linkedin.get_recent_posts",
            description="Fetch recent posts from LinkedIn using Apify",
            inputSchema={
                "type": "object",
                "properties": {
                    "profile_url": {
                        "type": "string",
                        "description": "LinkedIn profile URL (e.g., https://linkedin.com/in/username)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of posts to fetch",
                        "default": 10
                    }
                },
                "required": ["profile_url"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""

    if name != "linkedin.get_recent_posts":
        raise ValueError(f"Unknown tool: {name}")

    profile_url = arguments.get("profile_url", "").strip()
    limit = arguments.get("limit", 10)

    if not profile_url:
        return [TextContent(
            type="text",
            text=f"Error: {ErrorType.INVALID_INPUT} - Profile URL is required"
        )]

    username = extract_linkedin_username(profile_url)
    if not username:
        return [TextContent(
            type="text",
            text=f"Error: {ErrorType.INVALID_INPUT} - Invalid LinkedIn profile URL"
        )]

    try:
        # Get Apify configuration
        client = get_apify_client()
        # Note: This is a placeholder actor - you'll need to specify the actual LinkedIn posts actor
        actor_id = os.getenv("APIFY_LINKEDIN_POSTS_ACTOR", "your_linkedin_posts_actor")

        # Prepare actor input - this will vary based on the specific LinkedIn actor
        actor_input = {
            "profiles": [profile_url],
            "postsPerProfile": limit,
            "includeComments": False
        }

        # Run the actor
        run = client.actor(actor_id).call(run_input=actor_input)

        # Get the dataset items
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not items:
            return [TextContent(
                type="text",
                text=f"Error: {ErrorType.NOT_FOUND} - No recent posts found for profile"
            )]

        # Convert to normalized format
        posts = []
        for item in items:
            try:
                post = normalize_linkedin_post(item, profile_url)
                posts.append(post)
            except Exception as e:
                print(f"Warning: Failed to normalize post: {e}")
                continue

        if not posts:
            return [TextContent(
                type="text",
                text=f"Error: {ErrorType.SCHEMA_MISMATCH} - Could not parse any posts"
            )]

        # Apply theme inference
        ThemeInferenceEngine.infer_themes_bulk(posts)

        # Create person object
        person = Person(
            name=f"LinkedIn User ({username})",
            platform=Platform.LINKEDIN,
            profile_url=profile_url,
            headline_or_bio=""
        )

        # Create metadata
        meta = Meta(
            source="mcp_linkedin",
            fetched_at_iso=datetime.now(timezone.utc).isoformat(),
            limit=limit,
            total_found=len(posts)
        )

        # Create bundle
        bundle = Bundle(
            person=person,
            posts=posts,
            meta=meta
        )

        return [TextContent(
            type="text",
            text=bundle.model_dump_json(indent=2)
        )]

    except Exception as e:
        error_msg = str(e)

        # Classify the error
        if "rate limit" in error_msg.lower():
            error_type = ErrorType.RATE_LIMITED
        elif "private" in error_msg.lower() or "protected" in error_msg.lower():
            error_type = ErrorType.PRIVATE_PROFILE
        elif "not found" in error_msg.lower():
            error_type = ErrorType.NOT_FOUND
        else:
            error_type = ErrorType.API_ERROR

        return [TextContent(
            type="text",
            text=f"Error: {error_type} - {error_msg}"
        )]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp_linkedin",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())