#!/usr/bin/env python3
"""
Direct test of Twitter data fetching for @Nossa_ym
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from apify_client import ApifyClient

# Load environment variables
load_dotenv()

def test_nossa_twitter():
    """Test fetching data for @bhorowitz directly via Apify"""
    print("🐦 Testing Twitter data fetch for @bhorowitz")
    print("=" * 50)

    # Initialize Apify client
    token = os.getenv("APIFY_TOKEN")
    if not token:
        print("❌ APIFY_TOKEN not found in environment")
        return False

    print(f"🔑 Using Apify token: ...{token[-8:]}")
    client = ApifyClient(token)

    try:
        # Use Twitter Scraper actor
        print("🚀 Starting Twitter scraper...")

        run_input = {
            "searchTerms": ["from:bhorowitz"],  # Modern format using search terms
            "sort": "Latest",
            "tweetLanguage": "en"
        }

        print(f"📊 Input parameters: {json.dumps(run_input, indent=2)}")

        # Run the actor synchronously using the modern Twitter scraper
        print("⏳ Running Apify actor (this may take 30-60 seconds)...")
        run = client.actor("apidojo/tweet-scraper").call(run_input=run_input)

        # Fetch the results
        print("📥 Fetching results...")
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        print(f"✅ Successfully fetched {len(items)} items")
        print("=" * 50)

        # Display the results
        for i, item in enumerate(items, 1):
            print(f"\n📝 Tweet {i}:")
            print(f"   Author: @{item.get('author', {}).get('userName', 'unknown')}")
            print(f"   Date: {item.get('createdAt', 'unknown')}")
            print(f"   Text: {item.get('text', 'No text')[:100]}...")
            print(f"   URL: {item.get('url', 'No URL')}")

            # Show engagement metrics
            if 'replyCount' in item or 'retweetCount' in item or 'likeCount' in item:
                metrics = []
                if item.get('likeCount'):
                    metrics.append(f"❤️ {item['likeCount']}")
                if item.get('retweetCount'):
                    metrics.append(f"🔄 {item['retweetCount']}")
                if item.get('replyCount'):
                    metrics.append(f"💬 {item['replyCount']}")
                if metrics:
                    print(f"   Engagement: {' | '.join(metrics)}")

        # Save raw data
        filename = "nossa_twitter_raw.json"
        with open(filename, 'w') as f:
            json.dump(items, f, indent=2, default=str)
        print(f"\n💾 Raw data saved to: {filename}")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    success = test_nossa_twitter()
    print(f"\n⏰ Finished at: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🎯 Result: {'SUCCESS' if success else 'FAILED'}")