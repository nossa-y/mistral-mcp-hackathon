"""
LinkedIn MCP Server for ColdOpen Coach using FastMCP.
Fetches recent posts using Apify and returns normalized data.
"""

import os
import re
from datetime import datetime, timezone
from typing import Dict, Any
from urllib.parse import urlparse

from apify_client import ApifyClient
from fastmcp import FastMCP

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models import Bundle, Person, Post, Meta, Platform
from shared.theme_inference import ThemeInferenceEngine

# Initialize FastMCP server
mcp = FastMCP("LinkedIn MCP Server")

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


def extract_linkedin_username(profile_url: str) -> str:
    """Extract LinkedIn username from profile URL."""
    try:
        if not profile_url.startswith(('http://', 'https://')):
            profile_url = f"https://{profile_url}"

        parsed = urlparse(profile_url)
        if 'linkedin.com' not in parsed.netloc:
            raise ValueError("Invalid LinkedIn URL")

        path = parsed.path.strip('/')
        if path.startswith('in/'):
            username = path[3:].strip('/')
            if username:
                return username

        raise ValueError("Could not extract username from LinkedIn URL")
    except Exception as e:
        raise ValueError(f"Invalid LinkedIn profile URL: {e}")


def normalize_linkedin_post(item: Dict[str, Any], profile_url: str) -> Post:
    """Convert Apify LinkedIn actor response item to normalized Post."""
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

    # Extract hashtags and mentions
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

    return Post(
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


@mcp.tool()
def get_recent_posts(profile_url: str, limit: int = 10) -> str:
    """
    Fetch recent posts from LinkedIn using Apify.

    Args:
        profile_url: LinkedIn profile URL (e.g., https://linkedin.com/in/username)
        limit: Maximum number of posts to fetch (default: 10)

    Returns:
        JSON string with the Bundle containing person info, posts, and metadata
    """
    if not profile_url.strip():
        return f"Error: {ErrorType.INVALID_INPUT} - Profile URL is required"

    try:
        username = extract_linkedin_username(profile_url)
    except ValueError as e:
        return f"Error: {ErrorType.INVALID_INPUT} - {e}"

    try:
        # Get Apify configuration
        client = get_apify_client()
        actor_id = os.getenv("APIFY_LINKEDIN_POSTS_ACTOR", "your_linkedin_posts_actor")

        # Prepare actor input
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
            return f"Error: {ErrorType.NOT_FOUND} - No recent posts found for profile"

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
            return f"Error: {ErrorType.SCHEMA_MISMATCH} - Could not parse any posts"

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
            source="mcp_linkedin_fastmcp",
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

if __name__ == "__main__":
    mcp.run()