#!/usr/bin/env python3
"""Debug Apify response directly"""

import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

def debug_apify_twitter():
    """Debug the Apify Twitter scraper directly"""

    client = ApifyClient(os.getenv("APIFY_TOKEN"))
    actor_id = os.getenv("APIFY_TWITTER_ACTOR", "apidojo/tweet-scraper")

    print(f"Using actor: {actor_id}")
    print(f"Testing with handle: elonmusk")

    # Try different input formats
    actor_inputs = [
        # Format 1: Original
        {
            "handles": ["elonmusk"],
            "tweetsPerQuery": 3,
            "includeReplies": False,
            "includeRetweets": False
        },
        # Format 2: Search term based
        {
            "searchTerms": ["from:elonmusk"],
            "maxTweets": 3,
            "includeReplies": False,
            "includeRetweets": False
        },
        # Format 3: Simple profile URL
        {
            "urls": ["https://twitter.com/elonmusk"],
            "maxTweets": 3
        }
    ]

    for i, actor_input in enumerate(actor_inputs):
        print(f"\n=== Testing Format {i+1} ===")
        print(f"Actor input: {actor_input}")

        try:
            run = client.actor(actor_id).call(run_input=actor_input)
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            print(f"Number of items returned: {len(items)}")

            if items:
                print("✅ SUCCESS! First item:")
                print(items[0])
                break  # Stop on first success
            else:
                print("❌ No items returned")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("All formats tested.")

if __name__ == "__main__":
    debug_apify_twitter()