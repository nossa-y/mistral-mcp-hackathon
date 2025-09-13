#!/usr/bin/env python3
"""
ColdOpen Coach - Direct MCP Tool Demo

This script demonstrates fetching social media data directly from MCP servers.
Le Chat can use this data to generate conversation approaches.

Usage:
    python demo/fetch_data.py --twitter-handle elonmusk
    python demo/fetch_data.py --linkedin-url "https://linkedin.com/in/reidhoffman"
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

from shared.models import Bundle


class DataFetcher:
    """Direct MCP data fetcher for Le Chat integration"""

    def __init__(self):
        load_dotenv()
        if not os.getenv("APIFY_TOKEN"):
            print("❌ Error: APIFY_TOKEN environment variable is required")
            print("Please copy .env.example to .env and add your Apify token")
            sys.exit(1)

    async def fetch_twitter_data(self, handle: str) -> dict:
        """Fetch Twitter data - in real usage, this would be called by Le Chat via MCP"""
        print(f"🐦 Fetching Twitter data for @{handle}...")

        # Mock data for demo - in reality this comes from mcp_x server
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
        """Fetch LinkedIn data - in real usage, this would be called by Le Chat via MCP"""
        print(f"💼 Fetching LinkedIn data for {profile_url}...")

        username = profile_url.split('/in/')[-1].strip('/')

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

    def display_bundle(self, bundle_data: dict):
        """Display the fetched data bundle"""
        bundle = Bundle.model_validate(bundle_data)

        print("\n" + "="*60)
        print(f"📊 DATA BUNDLE - {bundle.person.platform.upper()}")
        print("="*60)

        print(f"\n👤 PERSON:")
        print(f"   Name: {bundle.person.name}")
        print(f"   Platform: {bundle.person.platform}")
        print(f"   URL: {bundle.person.profile_url or bundle.person.handle}")

        print(f"\n📝 POSTS ({len(bundle.posts)}):")
        for i, post in enumerate(bundle.posts, 1):
            print(f"   {i}. {post.created_at_iso[:10]} - {post.text[:100]}...")
            if post.inferred_themes:
                print(f"      Themes: {', '.join(post.inferred_themes)}")
            if post.engagement:
                engagement_str = ', '.join([f"{k}: {v}" for k, v in post.engagement.items() if v > 0])
                if engagement_str:
                    print(f"      Engagement: {engagement_str}")
            print(f"      URL: {post.url}")

        print(f"\n📈 META:")
        print(f"   Source: {bundle.meta.source}")
        print(f"   Fetched: {bundle.meta.fetched_at_iso}")
        print(f"   Total found: {bundle.meta.total_found}")

        print("\n" + "="*60)
        print("💡 Le Chat Integration:")
        print("   - This JSON data can be consumed directly by Le Chat")
        print("   - Le Chat will analyze themes and generate conversation approaches")
        print("   - No separate orchestration server needed!")
        print("="*60)

    async def run(self, twitter_handle: str = None, linkedin_url: str = None):
        """Fetch data from specified platforms"""
        if not twitter_handle and not linkedin_url:
            print("❌ Error: Please provide either --twitter-handle or --linkedin-url")
            return

        print("🚀 ColdOpen Coach - Direct MCP Data Fetch")
        print("-" * 50)

        if twitter_handle:
            try:
                twitter_data = await self.fetch_twitter_data(twitter_handle)
                self.display_bundle(twitter_data)

                # Save to file for Le Chat reference
                with open(f"twitter_{twitter_handle}.json", "w") as f:
                    json.dump(twitter_data, f, indent=2)
                print(f"\n💾 Data saved to: twitter_{twitter_handle}.json")

            except Exception as e:
                print(f"❌ Error fetching Twitter data: {e}")

        if linkedin_url:
            try:
                linkedin_data = await self.fetch_linkedin_data(linkedin_url)
                self.display_bundle(linkedin_data)

                # Save to file for Le Chat reference
                username = linkedin_url.split('/in/')[-1].strip('/')
                with open(f"linkedin_{username}.json", "w") as f:
                    json.dump(linkedin_data, f, indent=2)
                print(f"\n💾 Data saved to: linkedin_{username}.json")

            except Exception as e:
                print(f"❌ Error fetching LinkedIn data: {e}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ColdOpen Coach - Direct MCP Data Fetch")
    parser.add_argument("--twitter-handle", help="Twitter handle (without @)")
    parser.add_argument("--linkedin-url", help="LinkedIn profile URL")

    args = parser.parse_args()

    fetcher = DataFetcher()
    await fetcher.run(
        twitter_handle=args.twitter_handle,
        linkedin_url=args.linkedin_url
    )


if __name__ == "__main__":
    asyncio.run(main())