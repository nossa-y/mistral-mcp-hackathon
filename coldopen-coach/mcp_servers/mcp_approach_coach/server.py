"""
Approach Coach MCP Server for ColdOpen Coach.
Orchestrates social media data and generates conversation approach prompts.
"""

import os
import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Sequence

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models import Bundle, Post, ApproachRequest, ApproachResponse, Platform


app = Server("mcp_approach_coach")


class PromptOrchestrator:
    """Orchestrates social media data into structured prompts for Claude"""

    @staticmethod
    def filter_fresh_posts(posts: List[Post], freshness_days: int = 30) -> List[Post]:
        """Filter posts to only include fresh ones within the specified window"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=freshness_days)
        fresh_posts = []

        for post in posts:
            try:
                post_date = datetime.fromisoformat(post.created_at_iso.replace('Z', '+00:00'))
                if post_date >= cutoff_date:
                    fresh_posts.append(post)
            except ValueError:
                # If we can't parse the date, include it to be safe
                fresh_posts.append(post)

        # Sort by recency (most recent first)
        fresh_posts.sort(key=lambda p: p.created_at_iso, reverse=True)
        return fresh_posts

    @staticmethod
    def merge_bundles(bundles: List[Bundle]) -> List[Post]:
        """Merge posts from all bundles"""
        all_posts = []
        for bundle in bundles:
            all_posts.extend(bundle.posts)

        # Sort by recency
        all_posts.sort(key=lambda p: p.created_at_iso, reverse=True)
        return all_posts

    @staticmethod
    def extract_themes(posts: List[Post]) -> List[str]:
        """Extract unique themes from posts"""
        all_themes = set()
        for post in posts:
            all_themes.update(post.inferred_themes)
        return sorted(list(all_themes))

    @staticmethod
    def build_prompt_blocks(
        bundles: List[Bundle],
        user_context: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build structured prompt blocks for Claude.

        Returns:
            Dictionary with system, developer, and user prompt blocks
        """
        # Get preferences with defaults
        freshness_days = preferences.get("freshness_days", 30)
        tone = preferences.get("tone", "friendly")
        language = preferences.get("language", "en")

        # Merge and filter posts
        all_posts = PromptOrchestrator.merge_bundles(bundles)
        fresh_posts = PromptOrchestrator.filter_fresh_posts(all_posts, freshness_days)

        # Determine if fallback mode
        fallback_used = len(fresh_posts) == 0

        # Extract themes and prepare post summaries
        themes = PromptOrchestrator.extract_themes(fresh_posts) if fresh_posts else []
        post_summaries = []

        for i, post in enumerate(fresh_posts[:5]):  # Top 5 most recent
            summary = {
                "index": i + 1,
                "platform": post.platform,
                "date": post.created_at_iso[:10],  # Just the date part
                "text_preview": post.text[:200] + ("..." if len(post.text) > 200 else ""),
                "themes": post.inferred_themes,
                "url": post.url,
                "engagement": post.engagement
            }
            post_summaries.append(summary)

        # Build prompt blocks
        system_prompt = (
            "You are a conversation coach helping someone start a natural, respectful conversation "
            "at a networking event. Use only the provided public social media posts to craft your approach. "
            "Important rules:\n"
            "- Never say 'I saw your post' or reference seeing their content directly\n"
            "- Keep openers short and human-sounding, not scripted\n"
            "- Reference themes and interests, not specific posts\n"
            "- Be respectful and professional\n"
            "- Focus on shared interests or genuine curiosity"
        )

        developer_prompt = {
            "instructions": "Generate a conversation approach with exactly these fields:",
            "required_output": {
                "opener_bold": "1-2 sentence conversation starter (bold, natural tone)",
                "follow_up_question": "Light follow-up question to keep conversation flowing",
                "coaching_note": "Brief advice on tone and delivery",
                "rationale": {
                    "theme_used": "Primary theme that influenced the approach",
                    "source_refs": ["List of post URLs that informed this approach"],
                    "confidence": "high/medium/low - how well the posts inform this approach"
                },
                "fallback_used": "boolean - true if no recent posts were available"
            }
        }

        # User context and data
        user_prompt_data = {
            "person_context": {
                "your_name": user_context.get("your_name", ""),
                "shared_signals": user_context.get("shared_signals", ""),
                "event_context": user_context.get("event_context", "")
            },
            "recent_posts": post_summaries if not fallback_used else [],
            "detected_themes": themes,
            "posts_considered": len(fresh_posts),
            "freshness_window": f"{freshness_days} days",
            "preferences": {
                "tone": tone,
                "language": language
            },
            "fallback_mode": fallback_used
        }

        if fallback_used:
            user_prompt_data["fallback_note"] = (
                "No recent posts found within the freshness window. "
                "Use shared signals and general professional networking approach."
            )

        return {
            "system": system_prompt,
            "developer": json.dumps(developer_prompt, indent=2),
            "user": json.dumps(user_prompt_data, indent=2),
            "fallback_used": fallback_used
        }


@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="approach.build_prompt",
            description="Build structured prompt for generating conversation approaches",
            inputSchema={
                "type": "object",
                "properties": {
                    "bundles": {
                        "type": "array",
                        "description": "Array of social media data bundles",
                        "items": {
                            "type": "object",
                            "description": "Bundle object with person, posts, and meta data"
                        }
                    },
                    "user_context": {
                        "type": "object",
                        "description": "User context information",
                        "properties": {
                            "your_name": {"type": "string", "description": "Your name"},
                            "shared_signals": {"type": "string", "description": "Shared connections or interests"},
                            "event_context": {"type": "string", "description": "Event or meeting context"}
                        }
                    },
                    "preferences": {
                        "type": "object",
                        "description": "Generation preferences",
                        "properties": {
                            "tone": {"type": "string", "description": "Conversation tone", "default": "friendly"},
                            "language": {"type": "string", "description": "Language code", "default": "en"},
                            "freshness_days": {"type": "integer", "description": "Days for fresh content", "default": 30}
                        }
                    }
                },
                "required": ["bundles"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""

    if name != "approach.build_prompt":
        raise ValueError(f"Unknown tool: {name}")

    try:
        # Parse arguments
        bundles_data = arguments.get("bundles", [])
        user_context = arguments.get("user_context", {})
        preferences = arguments.get("preferences", {})

        # Convert bundle data to Bundle objects
        bundles = []
        for bundle_data in bundles_data:
            try:
                bundle = Bundle.model_validate(bundle_data)
                bundles.append(bundle)
            except Exception as e:
                print(f"Warning: Failed to parse bundle: {e}")
                continue

        if not bundles:
            return [TextContent(
                type="text",
                text="Error: No valid bundles provided"
            )]

        # Build prompt blocks
        prompt_blocks = PromptOrchestrator.build_prompt_blocks(
            bundles, user_context, preferences
        )

        return [TextContent(
            type="text",
            text=json.dumps(prompt_blocks, indent=2)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error building prompt: {str(e)}"
        )]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp_approach_coach",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())