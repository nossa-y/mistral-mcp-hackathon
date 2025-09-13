#!/usr/bin/env python3
"""
Test the LinkedIn actor directly to see what data structure it returns
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from apify_client import ApifyClient

# Load environment variables
load_dotenv()

def test_linkedin_actor_directly(client, profile_url="https://linkedin.com/in/satyanadella", limit=3):
    """Test LinkedIn actor directly with curious_coder/linkedin-post-search-scraper"""
    print(f"\n💼 Testing LinkedIn Actor: curious_coder/linkedin-post-search-scraper")
    print("=" * 60)

    actor_id = "curious_coder/linkedin-post-search-scraper"
    print(f"📡 Using actor: {actor_id}")

    # This actor is for LinkedIn post search, let's try different input formats
    actor_input_formats = [
        # Format 1: Search by keyword
        {
            "searchKeywords": "AI artificial intelligence",
            "maxPosts": limit
        },
        # Format 2: Search by specific person posts
        {
            "searchKeywords": "Satya Nadella",
            "maxPosts": limit
        },
        # Format 3: Profile URL approach
        {
            "profileUrls": [profile_url],
            "maxPosts": limit
        }
    ]

    for i, actor_input in enumerate(actor_input_formats, 1):
        print(f"\n🔄 TRYING INPUT FORMAT {i}")
        print(f"📤 Input: {actor_input}")

        try:
            print("🚀 Starting LinkedIn actor run...")
            run = client.actor(actor_id).call(run_input=actor_input)

            print(f"✅ Actor run completed")
            print(f"📊 Run ID: {run.get('id')}")
            print(f"📊 Status: {run.get('status')}")

            # Get the dataset items
            dataset_id = run["defaultDatasetId"]
            print(f"📊 Dataset ID: {dataset_id}")

            items = list(client.dataset(dataset_id).iterate_items())
            print(f"📝 Retrieved {len(items)} items")

            if items:
                print(f"✅ SUCCESS with format {i}!")
                return items
            else:
                print(f"❌ No data with format {i}, trying next...")

        except Exception as e:
            print(f"❌ Format {i} failed: {e}")
            continue

    # If we get here, none of the formats worked
    print(f"❌ All input formats failed")
    return None

def main():
    """Test LinkedIn actor locally"""
    print("🧪 LOCAL LINKEDIN ACTOR TESTING")
    print("=" * 50)

    token = os.getenv("APIFY_TOKEN")
    if not token:
        print("❌ APIFY_TOKEN not found")
        return

    print(f"✅ APIFY_TOKEN loaded: {token[:20]}...")

    try:
        client = ApifyClient(token)
        print("✅ Apify client initialized")

        # Test LinkedIn actor
        items = test_linkedin_actor_directly(client)

        if items:
            print(f"\n✅ SUCCESS: Retrieved {len(items)} items from LinkedIn actor!")
            print("🎯 Now we know the data structure for MCP integration")
        else:
            print(f"\n❌ FAILED: No data retrieved from LinkedIn actor")

    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    main()