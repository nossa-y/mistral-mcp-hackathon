"""
X/Twitter MCP Server for ColdOpen Coach using FastMCP.
Fetches recent posts using Apify and returns normalized data.
"""

import os
from datetime import datetime, timezone
from typing import Dict, Any

from apify_client import ApifyClient
from fastmcp import FastMCP

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models import Bundle, Person, Post, Meta, Platform
from shared.theme_inference import ThemeInferenceEngine

# Initialize FastMCP server
mcp = FastMCP("X/Twitter MCP Server")

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


def normalize_x_post(item: Dict[str, Any], handle: str) -> Post:
    """Convert Apify X/Twitter actor response item to normalized Post."""
    post_id = str(item.get("id", ""))
    tweet_url = item.get("url", f"https://twitter.com/{handle}/status/{post_id}")
    text = item.get("text", "")
    created_at = item.get("createdAt", "")

    # Handle date format - Apify usually returns ISO format
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

    return Post(
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


@mcp.tool()
def get_recent_posts(handle: str, limit: int = 20) -> str:
    """
    Fetch recent posts from X/Twitter using Apify.

    Args:
        handle: Twitter handle (without @)
        limit: Maximum number of posts to fetch (default: 20)

    Returns:
        JSON string with the Bundle containing person info, posts, and metadata
    """
    handle = handle.strip().replace("@", "")

    if not handle:
        return f"Error: {ErrorType.INVALID_INPUT} - Handle is required"

    try:
        # Get Apify configuration
        client = get_apify_client()
        actor_id = os.getenv("APIFY_TWITTER_ACTOR", "apidojo/tweet-scraper")

        # Prepare actor input
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
            return f"Error: {ErrorType.NOT_FOUND} - No recent posts found for @{handle}"

        # Convert to normalized format
        posts = []
        for item in items:
            try:
                post = normalize_x_post(item, handle)
                posts.append(post)
            except Exception as e:
                print(f"Warning: Failed to normalize post: {e}")
                continue

        if not posts:
            return f"Error: {ErrorType.SCHEMA_MISMATCH} - Could not parse any posts"

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
            source="mcp_x_fastmcp",
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

        return bundle.model_dump_json(indent=2)

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

        return f"Error: {error_type} - {error_msg}"

# Export the FastMCP instance for Lambda usage
app = mcp

if __name__ == "__main__":
    mcp.run()