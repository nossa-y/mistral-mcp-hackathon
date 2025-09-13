"""
Social Data MCP Server for ColdOpen Coach.
Single MCP server with two tools: twitter.get_posts and linkedin.get_posts
Both use Apify directly and return raw normalized data.
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
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.models import Bundle, Person, Post, Meta, Platform
from shared.theme_inference import ThemeInferenceEngine


app = Server("social_data")

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


def normalize_twitter_post(item: Dict[str, Any], handle: str) -> Post:
    """Convert Apify Twitter response to normalized Post"""
    post_id = str(item.get("id", ""))
    tweet_url = item.get("url", f"https://twitter.com/{handle}/status/{post_id}")
    text = item.get("text", "")
    created_at = item.get("createdAt", "")

    # Handle date format
    if created_at and not created_at.endswith('Z'):
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            created_at = dt.isoformat()
        except ValueError:
            created_at = datetime.now(timezone.utc).isoformat()

    # Extract hashtags and mentions
    hashtags = []
    mentions = []
    entities = item.get("entities", {})

    if "hashtags" in entities:
        hashtags = [tag.get("text", "") for tag in entities["hashtags"]]
    if "user_mentions" in entities:
        mentions = [mention.get("screen_name", "") for mention in entities["user_mentions"]]

    # Extract engagement metrics
    engagement = {
        "likes": item.get("likeCount", 0),
        "retweets": item.get("retweetCount", 0),
        "replies": item.get("replyCount", 0),
        "quotes": item.get("quoteCount", 0)
    }

    post = Post(
        platform=Platform.X,
        post_id=post_id,
        url=tweet_url,
        created_at_iso=created_at,
        text=text,
        hashtags=hashtags,
        mentions=mentions,
        engagement=engagement,
        inferred_themes=[]
    )

    return post


def normalize_linkedin_post(item: Dict[str, Any], profile_url: str) -> Post:
    """Convert Apify LinkedIn response to normalized Post"""
    post_id = str(item.get("postId", item.get("id", "")))
    post_url = item.get("postUrl", item.get("url", ""))
    text = item.get("text", item.get("content", ""))
    created_at = item.get("postedAt", item.get("publishedAt", item.get("createdAt", "")))

    # Handle date format
    if created_at:
        try:
            if isinstance(created_at, str):
                if not created_at.endswith('Z') and '+' not in created_at:
                    created_at = created_at + 'Z'
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_at = dt.isoformat()
        except ValueError:
            created_at = datetime.now(timezone.utc).isoformat()
    else:
        created_at = datetime.now(timezone.utc).isoformat()

    # Extract hashtags and mentions from text
    hashtags = []
    mentions = []
    if text:
        hashtag_matches = re.findall(r'#(\w+)', text)
        hashtags = [f"#{tag}" for tag in hashtag_matches]
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
        inferred_themes=[]
    )

    return post


def extract_linkedin_username(profile_url: str) -> Optional[str]:
    """Extract LinkedIn username from profile URL"""
    try:
        if not profile_url.startswith(('http://', 'https://')):
            profile_url = f"https://{profile_url}"

        parsed = urlparse(profile_url)
        if 'linkedin.com' not in parsed.netloc:
            return None

        path = parsed.path.strip('/')
        if path.startswith('in/'):
            username = path[3:].strip('/')
            return username if username else None

        return None
    except:
        return None


@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="twitter.get_posts",
            description="Fetch recent posts from Twitter/X using Apify",
            inputSchema={
                "type": "object",
                "properties": {
                    "handle": {
                        "type": "string",
                        "description": "Twitter handle (without @)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of posts to fetch",
                        "default": 20
                    }
                },
                "required": ["handle"]
            }
        ),
        Tool(
            name="linkedin.get_posts",
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

    if name == "twitter.get_posts":
        return await handle_twitter_posts(arguments)
    elif name == "linkedin.get_posts":
        return await handle_linkedin_posts(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_twitter_posts(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle Twitter posts fetching"""
    handle = arguments.get("handle", "").strip().replace("@", "")
    limit = arguments.get("limit", 20)

    if not handle:
        return [TextContent(
            type="text",
            text=f"Error: {ErrorType.INVALID_INPUT} - Handle is required"
        )]

    try:
        client = get_apify_client()
        actor_id = os.getenv("APIFY_TWITTER_ACTOR", "apidojo/tweet-scraper")

        actor_input = {
            "handles": [handle],
            "tweetsPerQuery": limit,
            "includeReplies": False,
            "includeRetweets": False
        }

        # Run the actor
        run = client.actor(actor_id).call(run_input=actor_input)

        # Get the dataset items
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not items:
            return [TextContent(
                type="text",
                text=f"Error: {ErrorType.NOT_FOUND} - No recent posts found for @{handle}"
            )]

        # Convert to normalized format
        posts = []
        for item in items:
            try:
                post = normalize_twitter_post(item, handle)
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
            name=f"@{handle}",
            platform=Platform.X,
            handle=handle,
            profile_url=f"https://twitter.com/{handle}",
            headline_or_bio=""
        )

        # Create metadata
        meta = Meta(
            source="twitter.get_posts",
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


async def handle_linkedin_posts(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle LinkedIn posts fetching"""
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
        client = get_apify_client()
        actor_id = os.getenv("APIFY_LINKEDIN_POSTS_ACTOR", "your_linkedin_posts_actor")

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
            source="linkedin.get_posts",
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
                server_name="social_data",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())