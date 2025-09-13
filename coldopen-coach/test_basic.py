#!/usr/bin/env python3
"""
Basic functionality test for ColdOpen Coach
Tests the core components without requiring Apify token
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")

    try:
        from shared.models import Bundle, Person, Post, Meta, Platform
        print("✅ Shared models imported successfully")
    except Exception as e:
        print(f"❌ Failed to import shared models: {e}")
        return False

    try:
        from shared.theme_inference import ThemeInferenceEngine
        print("✅ Theme inference engine imported successfully")
    except Exception as e:
        print(f"❌ Failed to import theme inference: {e}")
        return False

    return True

def test_theme_inference():
    """Test theme inference functionality"""
    print("\nTesting theme inference...")

    from shared.models import Post, Platform
    from shared.theme_inference import ThemeInferenceEngine

    # Create test post
    test_post = Post(
        platform=Platform.X,
        post_id="test123",
        url="https://twitter.com/test/status/test123",
        created_at_iso="2024-01-15T10:30:00Z",
        text="Just shipped a new AI agent feature that helps developers debug faster. The future of coding is here! #AI #DevTools #Shipping",
        hashtags=["#AI", "#DevTools", "#Shipping"],
        mentions=[],
        engagement={"likes": 245, "retweets": 67}
    )

    # Test theme inference
    themes = ThemeInferenceEngine.infer_themes(test_post)
    print(f"Detected themes: {themes}")

    # Check expected themes
    expected_themes = ["ai_agents", "shipping_quality"]
    for theme in expected_themes:
        if theme in themes:
            print(f"✅ Correctly detected theme: {theme}")
        else:
            print(f"❌ Missing expected theme: {theme}")
            return False

    return True

def test_data_models():
    """Test data model validation"""
    print("\nTesting data models...")

    from shared.models import Bundle, Person, Post, Meta, Platform

    try:
        # Create test person
        person = Person(
            name="Test User",
            platform=Platform.X,
            handle="testuser",
            profile_url="https://twitter.com/testuser"
        )
        print("✅ Person model created successfully")

        # Create test post
        post = Post(
            platform=Platform.X,
            post_id="123",
            url="https://twitter.com/test/status/123",
            created_at_iso="2024-01-15T10:30:00Z",
            text="Test post content",
            hashtags=["#test"],
            mentions=[],
            engagement={"likes": 10}
        )
        print("✅ Post model created successfully")

        # Create test meta
        meta = Meta(
            source="test_server",
            fetched_at_iso="2024-01-16T12:00:00Z",
            limit=20,
            total_found=1
        )
        print("✅ Meta model created successfully")

        # Create test bundle
        bundle = Bundle(
            person=person,
            posts=[post],
            meta=meta
        )
        print("✅ Bundle model created successfully")

        # Test JSON serialization
        json_data = bundle.model_dump_json()
        print("✅ JSON serialization successful")

        return True

    except Exception as e:
        print(f"❌ Data model test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 ColdOpen Coach - Basic Functionality Test")
    print("=" * 50)

    tests = [
        test_imports,
        test_data_models,
        test_theme_inference
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED with exception: {e}")

    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! ColdOpen Coach is ready for demo.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")

    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)