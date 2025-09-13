"""
Social MCP Server for ColdOpen Coach using FastMCP.
Consolidated server that fetches recent posts from both X/Twitter and LinkedIn using Apify.
Returns normalized data for Le Chat integration.
"""

import os
import re
from datetime import datetime, timezone
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from urllib.parse import urlparse

from apify_client import ApifyClient
from fastmcp import FastMCP

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.models import Bundle, Person, Post, Meta, Platform
from shared.theme_inference import ThemeInferenceEngine

# Initialize FastMCP server
mcp = FastMCP("Social MCP Server")

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
def get_x_posts(handle: str, limit: int = 20) -> Dict[str, Any]:
    """Fetch recent posts from X/Twitter using Apify."""
    handle = handle.strip().replace("@", "")

    if not handle:
        raise ValueError("Handle is required")

    try:
        client = get_apify_client()
        actor_id = os.getenv("APIFY_TWITTER_ACTOR", "apidojo/tweet-scraper")

        actor_input = {
            "handles": [handle],
            "tweetsPerQuery": limit,
            "includeReplies": False,
            "includeRetweets": False
        }

        run = client.actor(actor_id).call(run_input=actor_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not items:
            raise ValueError(f"No recent posts found for @{handle}")

        # Convert to normalized format
        posts = []
        for item in items:
            try:
                post = normalize_x_post(item, handle)
                posts.append(post)
            except Exception as e:
                continue

        if not posts:
            raise ValueError("Could not parse any posts")

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
            source="social_mcp_server",
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

        # Return dict, not JSON string
        return bundle.model_dump()  # ✅ This is the key fix!

    except Exception as e:
        raise ValueError(f"Failed to fetch X posts: {str(e)}")


@mcp.tool()
def get_linkedin_posts(profile_url: str, limit: int = 10) -> Dict[str, Any]:
    """Fetch recent posts from LinkedIn using Apify."""
    if not profile_url.strip():
        raise ValueError("Profile URL is required")

    try:
        username = extract_linkedin_username(profile_url)
    except ValueError as e:
        raise ValueError(str(e))

    try:
        client = get_apify_client()
        actor_id = os.getenv("APIFY_LINKEDIN_POSTS_ACTOR", "your_linkedin_posts_actor")

        actor_input = {
            "profiles": [profile_url],
            "postsPerProfile": limit,
            "includeComments": False
        }

        run = client.actor(actor_id).call(run_input=actor_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not items:
            raise ValueError("No recent posts found for profile")

        # Convert to normalized format
        posts = []
        for item in items:
            try:
                post = normalize_linkedin_post(item, profile_url)
                posts.append(post)
            except Exception as e:
                continue

        if not posts:
            raise ValueError("Could not parse any posts")

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
            source="social_mcp_server",
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

        # Return dict, not JSON string  
        return bundle.model_dump()  # ✅ This is the key fix!

    except Exception as e:
        raise ValueError(f"Failed to fetch LinkedIn posts: {str(e)}")
# Export the FastMCP instance for Lambda usage
app = mcp


def main():
    """Entry point for the CLI script"""
    if os.getenv("HTTP_MODE"):
        mcp.run(transport="sse", port=int(os.getenv("PORT", 8080)))
    else:
        mcp.run()


if __name__ == "__main__":
    if os.getenv("HTTP_MODE"):
        mcp.run(transport="sse", port=int(os.getenv("PORT", 8080)))
    else:
        mcp.run()  # STDIO for local testing