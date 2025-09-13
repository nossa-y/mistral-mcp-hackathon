#!/usr/bin/env python3
"""
Test Apify functions locally without MCP wrapper
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from apify_client import ApifyClient

# Load environment variables
load_dotenv()

def test_apify_client():
    """Test basic Apify client functionality"""
    print("🔧 Testing Apify Client Setup")
    print("=" * 40)

    token = os.getenv("APIFY_TOKEN")
    if not token:
        print("❌ APIFY_TOKEN not found in environment")
        return False

    print(f"✅ APIFY_TOKEN loaded: {token[:20]}...")

    try:
        client = ApifyClient(token)
        print("✅ Apify client initialized successfully")
        return client
    except Exception as e:
        print(f"❌ Failed to initialize Apify client: {e}")
        return None

def test_twitter_actor_directly(client, handle="elonmusk", limit=3):
    """Test Twitter actor directly"""
    print(f"\n🐦 Testing Twitter Actor Directly")
    print("=" * 40)

    actor_id = os.getenv("APIFY_TWITTER_ACTOR", "apidojo/tweet-scraper")
    print(f"📡 Using actor: {actor_id}")

    actor_input = {
        "handles": [handle],
        "tweetsPerQuery": limit,
        "includeReplies": False,
        "includeRetweets": False
    }

    print(f"📤 Input: {actor_input}")

    try:
        print("🚀 Starting actor run...")
        run = client.actor(actor_id).call(run_input=actor_input)

        print(f"✅ Actor run completed")
        print(f"📊 Run ID: {run.get('id')}")
        print(f"📊 Status: {run.get('status')}")

        # Get the dataset items
        dataset_id = run["defaultDatasetId"]
        print(f"📊 Dataset ID: {dataset_id}")

        items = list(client.dataset(dataset_id).iterate_items())
        print(f"📝 Retrieved {len(items)} items")

        # Show first item structure
        if items:
            first_item = items[0]
            print(f"\n📋 First item keys: {list(first_item.keys())}")
            print(f"📋 Tweet text: {first_item.get('text', 'N/A')[:100]}...")
            print(f"📋 Created at: {first_item.get('createdAt', 'N/A')}")
            print(f"📋 Like count: {first_item.get('likeCount', 'N/A')}")

        return items

    except Exception as e:
        print(f"❌ Actor run failed: {e}")
        return None

def main():
    """Test everything locally"""
    print("🧪 LOCAL APIFY FUNCTION TESTING")
    print("=" * 50)

    # Test 1: Client setup
    client = test_apify_client()
    if not client:
        return

    # Test 2: Twitter actor
    items = test_twitter_actor_directly(client)

    if items:
        print(f"\n✅ SUCCESS: Retrieved {len(items)} real tweets from Apify!")
        print("🎯 This proves the Apify integration works")
    else:
        print(f"\n❌ FAILED: No data retrieved")
        print("🔍 Check your Apify token and actor permissions")

if __name__ == "__main__":
    main()