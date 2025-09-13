#!/usr/bin/env python3
"""Debug the new LinkedIn actor data structure"""

import os
import json
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

def debug_new_linkedin():
    """Debug the new LinkedIn actor"""

    client = ApifyClient(os.getenv("APIFY_TOKEN"))
    actor_id = "supreme_coder/linkedin-post"

    print(f"Using actor: {actor_id}")
    print(f"Testing with profile: arthur-mensch")

    actor_input = {
        "urls": ["https://www.linkedin.com/in/arthur-mensch/"],
        "limitPerSource": 3
    }

    print(f"Actor input: {actor_input}")

    try:
        run = client.actor(actor_id).call(run_input=actor_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        print(f"Number of items returned: {len(items)}")

        if items:
            print("First item structure:")
            print(json.dumps(items[0], indent=2))

            print("\nAll item keys:")
            for i, item in enumerate(items):
                print(f"Item {i} keys: {list(item.keys())}")
        else:
            print("No items returned")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_new_linkedin()