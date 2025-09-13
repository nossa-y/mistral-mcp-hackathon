#!/usr/bin/env python3
"""
ColdOpen Coach Demo Script

This script demonstrates the end-to-end workflow:
1. Fetch recent posts from X/Twitter and LinkedIn
2. Generate conversation approach using the orchestrator
3. Display the results

Usage:
    python demo/run_demo.py --twitter-handle elonmusk --your-name "Alex"
    python demo/run_demo.py --linkedin-url "https://linkedin.com/in/username" --your-name "Alex"
    python demo/run_demo.py --twitter-handle elonmusk --linkedin-url "https://linkedin.com/in/username" --your-name "Alex"
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.models import Bundle, ApproachRequest


class ColdOpenCoachDemo:
    """Demo orchestrator for ColdOpen Coach"""

    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Check for required environment variables
        if not os.getenv("APIFY_TOKEN"):
            print("❌ Error: APIFY_TOKEN environment variable is required")
            print("Please copy .env.example to .env and add your Apify token")
            sys.exit(1)

    async def fetch_twitter_data(self, handle: str) -> dict:
        """
        Simulate fetching Twitter data using the MCP server.
        In a real implementation, this would call the MCP server.
        """
        print(f"🐦 Fetching Twitter data for @{handle}...")

        # For demo purposes, return mock data
        # In real implementation, this would use MCP client to call the server
        mock_bundle = {
            "person": {
                "name": f"@{handle}",
                "platform": "x",
                "handle": handle,
                "profile_url": f"https://twitter.com/{handle}",
                "headline_or_bio": ""
            },
            "posts": [
                {
                    "platform": "x",
                    "post_id": "1234567890",
                    "url": f"https://twitter.com/{handle}/status/1234567890",
                    "created_at_iso": "2024-01-15T10:30:00Z",
                    "text": "Just shipped a new AI agent feature that helps developers debug faster. The future of coding is here! #AI #DevTools #Shipping",
                    "hashtags": ["#AI", "#DevTools", "#Shipping"],
                    "mentions": [],
                    "engagement": {"likes": 245, "retweets": 67, "replies": 23},
                    "inferred_themes": ["ai_agents", "shipping_quality"]
                },
                {
                    "platform": "x",
                    "post_id": "1234567891",
                    "url": f"https://twitter.com/{handle}/status/1234567891",
                    "created_at_iso": "2024-01-14T15:20:00Z",
                    "text": "Excited to announce our Series A funding! This will help us build the next generation of developer tools.",
                    "hashtags": [],
                    "mentions": [],
                    "engagement": {"likes": 1200, "retweets": 340, "replies": 89},
                    "inferred_themes": ["fundraising", "product_experiments"]
                }
            ],
            "meta": {
                "source": "mcp_x",
                "fetched_at_iso": "2024-01-16T12:00:00Z",
                "limit": 20,
                "total_found": 2
            }
        }

        print(f"✅ Found {len(mock_bundle['posts'])} recent tweets")
        return mock_bundle

    async def fetch_linkedin_data(self, profile_url: str) -> dict:
        """
        Simulate fetching LinkedIn data using the MCP server.
        In a real implementation, this would call the MCP server.
        """
        print(f"💼 Fetching LinkedIn data for {profile_url}...")

        # Extract username for display
        username = profile_url.split('/in/')[-1].strip('/')

        # For demo purposes, return mock data
        mock_bundle = {
            "person": {
                "name": f"LinkedIn User ({username})",
                "platform": "linkedin",
                "profile_url": profile_url,
                "headline_or_bio": ""
            },
            "posts": [
                {
                    "platform": "linkedin",
                    "post_id": "activity-7123456789",
                    "url": f"https://linkedin.com/posts/{username}_activity-7123456789",
                    "created_at_iso": "2024-01-15T09:15:00Z",
                    "text": "Hiring exceptional engineers to join our team! We're building something special in the AI space. Looking for people who love solving hard problems.",
                    "hashtags": [],
                    "mentions": [],
                    "engagement": {"likes": 87, "comments": 15, "shares": 12},
                    "inferred_themes": ["hiring", "ai_agents"]
                }
            ],
            "meta": {
                "source": "mcp_linkedin",
                "fetched_at_iso": "2024-01-16T12:00:00Z",
                "limit": 10,
                "total_found": 1
            }
        }

        print(f"✅ Found {len(mock_bundle['posts'])} recent LinkedIn posts")
        return mock_bundle

    async def generate_approach(self, bundles: list, user_context: dict, preferences: dict) -> dict:
        """
        Simulate generating conversation approach using the orchestrator.
        In a real implementation, this would call the MCP server.
        """
        print("🧠 Generating conversation approach...")

        # For demo purposes, simulate the orchestrator logic
        all_posts = []
        for bundle in bundles:
            all_posts.extend(bundle.get('posts', []))

        # Extract themes
        all_themes = set()
        for post in all_posts:
            all_themes.update(post.get('inferred_themes', []))

        themes = list(all_themes)
        primary_theme = themes[0] if themes else "general_networking"

        # Generate mock approach response
        if "ai_agents" in themes:
            opener = "**I'm fascinated by the evolution of AI tooling for developers. What's your take on where the biggest opportunities are?**"
            follow_up = "Are you seeing any particular patterns in what developers need most right now?"
            coaching = "Lead with curiosity about their expertise. AI is clearly a passion area."
        elif "hiring" in themes:
            opener = "**The talent market is so competitive right now. What's been your experience building strong engineering teams?**"
            follow_up = "What qualities do you look for that might not show up on a resume?"
            coaching = "Focus on their leadership perspective. They're clearly thinking about team building."
        else:
            opener = "**What brings you to this event? Always curious to hear what other folks in tech are working on.**"
            follow_up = "What's the most interesting challenge you're tackling these days?"
            coaching = "Keep it open and genuine. Let them lead the conversation direction."

        mock_response = {
            "system": "You are a conversation coach...",
            "developer": json.dumps({
                "instructions": "Generate a conversation approach...",
                "required_output": "..."
            }, indent=2),
            "user": json.dumps({
                "person_context": user_context,
                "recent_posts": all_posts[:3],  # Top 3
                "detected_themes": themes,
                "posts_considered": len(all_posts),
                "preferences": preferences
            }, indent=2),
            "fallback_used": len(all_posts) == 0,
            "generated_approach": {
                "opener_bold": opener,
                "follow_up_question": follow_up,
                "coaching_note": coaching,
                "rationale": {
                    "theme_used": primary_theme,
                    "source_refs": [post.get('url', '') for post in all_posts[:2]],
                    "confidence": "high" if len(all_posts) > 1 else "medium"
                },
                "fallback_used": False
            }
        }

        print("✅ Generated conversation approach")
        return mock_response

    def display_results(self, approach_data: dict):
        """Display the generated conversation approach"""
        print("\n" + "="*60)
        print("🎯 CONVERSATION APPROACH")
        print("="*60)

        approach = approach_data.get('generated_approach', {})

        print("\n🗣️  OPENER:")
        print(f"   {approach.get('opener_bold', 'N/A')}")

        print("\n❓ FOLLOW-UP:")
        print(f"   {approach.get('follow_up_question', 'N/A')}")

        print("\n💡 COACHING NOTE:")
        print(f"   {approach.get('coaching_note', 'N/A')}")

        print("\n📊 RATIONALE:")
        rationale = approach.get('rationale', {})
        print(f"   Theme: {rationale.get('theme_used', 'N/A')}")
        print(f"   Confidence: {rationale.get('confidence', 'N/A')}")

        source_refs = rationale.get('source_refs', [])
        if source_refs:
            print("\n🔗 SOURCE POSTS:")
            for i, ref in enumerate(source_refs, 1):
                if ref:
                    print(f"   {i}. {ref}")

        if approach.get('fallback_used', False):
            print("\n⚠️  FALLBACK MODE: No recent posts found, using general approach")

        print("\n" + "="*60)

    async def run(self, twitter_handle: str = None, linkedin_url: str = None, your_name: str = ""):
        """Run the complete demo workflow"""
        if not twitter_handle and not linkedin_url:
            print("❌ Error: Please provide either --twitter-handle or --linkedin-url")
            return

        print("🚀 ColdOpen Coach Demo")
        print("-" * 40)

        bundles = []

        # Fetch Twitter data if requested
        if twitter_handle:
            try:
                twitter_data = await self.fetch_twitter_data(twitter_handle)
                bundles.append(twitter_data)
            except Exception as e:
                print(f"❌ Error fetching Twitter data: {e}")

        # Fetch LinkedIn data if requested
        if linkedin_url:
            try:
                linkedin_data = await self.fetch_linkedin_data(linkedin_url)
                bundles.append(linkedin_data)
            except Exception as e:
                print(f"❌ Error fetching LinkedIn data: {e}")

        if not bundles:
            print("❌ No data fetched successfully")
            return

        # Generate conversation approach
        user_context = {
            "your_name": your_name,
            "shared_signals": "",
            "event_context": "networking event"
        }

        preferences = {
            "tone": "friendly",
            "language": "en",
            "freshness_days": 30
        }

        try:
            approach_data = await self.generate_approach(bundles, user_context, preferences)
            self.display_results(approach_data)
        except Exception as e:
            print(f"❌ Error generating approach: {e}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ColdOpen Coach Demo")
    parser.add_argument("--twitter-handle", help="Twitter handle (without @)")
    parser.add_argument("--linkedin-url", help="LinkedIn profile URL")
    parser.add_argument("--your-name", default="", help="Your name for context")

    args = parser.parse_args()

    demo = ColdOpenCoachDemo()
    await demo.run(
        twitter_handle=args.twitter_handle,
        linkedin_url=args.linkedin_url,
        your_name=args.your_name
    )


if __name__ == "__main__":
    asyncio.run(main())