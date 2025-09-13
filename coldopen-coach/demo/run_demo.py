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
        Demo using mock data that represents what the MCP server would return.
        Shows the raw data structure returned by twitter.get_posts tool.
        """
        print(f"🐦 Calling MCP server tool: twitter.get_posts(handle='{handle}')")

        # Mock data representing actual MCP server response
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
                    "engagement": {"likes": 245, "retweets": 67, "replies": 23, "quotes": 12},
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
                    "engagement": {"likes": 1200, "retweets": 340, "replies": 89, "quotes": 45},
                    "inferred_themes": ["fundraising", "product_experiments"]
                }
            ],
            "meta": {
                "source": "twitter.get_posts",
                "fetched_at_iso": "2024-01-16T12:00:00Z",
                "limit": 20,
                "total_found": 2
            }
        }

        print(f"✅ Retrieved data bundle with {len(mock_bundle['posts'])} posts")
        return mock_bundle

    async def fetch_linkedin_data(self, profile_url: str) -> dict:
        """
        Demo using mock data that represents what the MCP server would return.
        Shows the raw data structure returned by linkedin.get_posts tool.
        """
        username = profile_url.split('/in/')[-1].strip('/')
        print(f"💼 Calling MCP server tool: linkedin.get_posts(profile_url='{profile_url}')")

        # Mock data representing actual MCP server response
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
                "source": "linkedin.get_posts",
                "fetched_at_iso": "2024-01-16T12:00:00Z",
                "limit": 10,
                "total_found": 1
            }
        }

        print(f"✅ Retrieved data bundle with {len(mock_bundle['posts'])} posts")
        return mock_bundle

    def analyze_retrieved_data(self, bundles: list) -> dict:
        """
        Analyze the raw data retrieved from MCP tools.
        This shows what analysis can be done on the retrieved data.
        """
        print("📊 Analyzing retrieved data...")

        # Combine all posts from all bundles
        all_posts = []
        platforms = set()
        for bundle in bundles:
            all_posts.extend(bundle.get('posts', []))
            platforms.add(bundle.get('person', {}).get('platform'))

        # Extract and analyze themes
        all_themes = set()
        theme_frequency = {}
        for post in all_posts:
            for theme in post.get('inferred_themes', []):
                all_themes.add(theme)
                theme_frequency[theme] = theme_frequency.get(theme, 0) + 1

        # Analyze engagement
        total_engagement = {
            "likes": sum(post.get('engagement', {}).get('likes', 0) for post in all_posts),
            "retweets": sum(post.get('engagement', {}).get('retweets', 0) for post in all_posts),
            "replies": sum(post.get('engagement', {}).get('replies', 0) for post in all_posts),
            "comments": sum(post.get('engagement', {}).get('comments', 0) for post in all_posts),
            "shares": sum(post.get('engagement', {}).get('shares', 0) for post in all_posts)
        }

        # Most recent posts
        recent_posts = sorted(all_posts, key=lambda p: p.get('created_at_iso', ''), reverse=True)[:3]

        analysis = {
            "summary": {
                "total_posts": len(all_posts),
                "platforms_covered": list(platforms),
                "unique_themes": len(all_themes),
                "most_recent_post_date": recent_posts[0].get('created_at_iso', '')[:10] if recent_posts else None
            },
            "theme_analysis": {
                "detected_themes": sorted(list(all_themes)),
                "theme_frequency": dict(sorted(theme_frequency.items(), key=lambda x: x[1], reverse=True))
            },
            "engagement_analysis": {
                "total_engagement": total_engagement,
                "average_likes_per_post": round(total_engagement['likes'] / len(all_posts), 1) if all_posts else 0
            },
            "recent_posts_preview": [
                {
                    "date": post.get('created_at_iso', '')[:10],
                    "platform": post.get('platform'),
                    "text_preview": post.get('text', '')[:100] + "..." if len(post.get('text', '')) > 100 else post.get('text', ''),
                    "themes": post.get('inferred_themes', []),
                    "engagement": post.get('engagement', {})
                } for post in recent_posts
            ]
        }

        print("✅ Data analysis complete")
        return analysis

    def display_retrieved_data(self, bundles: list):
        """Display the raw data retrieved from MCP tools"""
        print("\n" + "="*60)
        print("📦 RETRIEVED DATA FROM MCP TOOLS")
        print("="*60)

        for i, bundle in enumerate(bundles, 1):
            person = bundle.get('person', {})
            posts = bundle.get('posts', [])
            meta = bundle.get('meta', {})

            print(f"\n📋 BUNDLE {i}: {person.get('platform', '').upper()}")
            print(f"   Person: {person.get('name', 'Unknown')}")
            print(f"   Profile: {person.get('profile_url', 'N/A')}")
            print(f"   Source: {meta.get('source', 'N/A')}")
            print(f"   Fetched: {meta.get('fetched_at_iso', 'N/A')[:19]}")
            print(f"   Posts found: {len(posts)}")

            for j, post in enumerate(posts[:2], 1):  # Show first 2 posts
                print(f"\n   📝 POST {j}:")
                print(f"      Date: {post.get('created_at_iso', '')[:10]}")
                print(f"      Text: {post.get('text', '')[:120]}...")
                print(f"      Themes: {', '.join(post.get('inferred_themes', []))}")
                engagement = post.get('engagement', {})
                eng_str = ', '.join([f"{k}: {v}" for k, v in engagement.items() if v > 0])
                print(f"      Engagement: {eng_str}")

        print("\n" + "="*60)

    def display_analysis(self, analysis: dict):
        """Display analysis of the retrieved data"""
        print("\n" + "="*60)
        print("📊 DATA ANALYSIS RESULTS")
        print("="*60)

        summary = analysis.get('summary', {})
        print(f"\n📈 SUMMARY:")
        print(f"   Total posts: {summary.get('total_posts', 0)}")
        print(f"   Platforms: {', '.join(summary.get('platforms_covered', []))}")
        print(f"   Unique themes: {summary.get('unique_themes', 0)}")
        print(f"   Most recent: {summary.get('most_recent_post_date', 'N/A')}")

        themes = analysis.get('theme_analysis', {})
        print(f"\n🎯 THEMES DETECTED:")
        print(f"   All themes: {', '.join(themes.get('detected_themes', []))}")

        freq = themes.get('theme_frequency', {})
        if freq:
            print(f"   Most frequent:")
            for theme, count in list(freq.items())[:3]:
                print(f"      • {theme}: {count} posts")

        engagement = analysis.get('engagement_analysis', {})
        print(f"\n💡 ENGAGEMENT:")
        total = engagement.get('total_engagement', {})
        print(f"   Total likes: {total.get('likes', 0)}")
        print(f"   Average likes/post: {engagement.get('average_likes_per_post', 0)}")

        recent = analysis.get('recent_posts_preview', [])
        if recent:
            print(f"\n📝 RECENT POSTS:")
            for i, post in enumerate(recent[:2], 1):
                print(f"   {i}. [{post.get('date')}] {post.get('text_preview', '')}")
                print(f"      Themes: {', '.join(post.get('themes', []))}")

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

        # Display the raw retrieved data
        self.display_retrieved_data(bundles)

        # Analyze the retrieved data
        try:
            analysis = self.analyze_retrieved_data(bundles)
            self.display_analysis(analysis)
        except Exception as e:
            print(f"❌ Error analyzing data: {e}")

        print(f"\n💡 This data can now be used by any LLM to generate conversation starters!")
        print(f"📝 The MCP tools returned structured, normalized data ready for analysis.")


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