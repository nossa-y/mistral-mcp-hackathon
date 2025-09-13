"""
Theme inference system for ColdOpen Coach.
Deterministic keyword-based theme detection from social media posts.
"""

import re
from typing import List, Set
from .models import Post


class ThemeInferenceEngine:
    """Simple keyword-based theme detection"""

    # Theme keywords mapping
    THEME_KEYWORDS = {
        "ai_agents": [
            "ai agent", "ai agents", "llm", "gpt", "claude", "chatgpt",
            "artificial intelligence", "machine learning", "ml", "neural network"
        ],
        "shipping_quality": [
            "ship", "shipping", "deploy", "deployment", "launch", "release",
            "quality", "testing", "qa", "bug", "fix", "build"
        ],
        "product_experiments": [
            "experiment", "a/b test", "feature flag", "mvp", "prototype",
            "user research", "product", "feedback", "iterate", "validation"
        ],
        "fundraising": [
            "fundraising", "funding", "investor", "series a", "series b", "seed",
            "vc", "venture capital", "pitch", "valuation", "raise"
        ],
        "hiring": [
            "hiring", "recruiting", "job", "position", "team", "engineer",
            "developer", "designer", "pm", "product manager", "we're hiring"
        ],
        "open_source": [
            "open source", "oss", "github", "contribution", "maintainer",
            "pull request", "pr", "commit", "repository", "license"
        ],
        "design_systems": [
            "design system", "ui", "ux", "user interface", "user experience",
            "component library", "figma", "design", "prototype", "wireframe"
        ],
        "sports": [
            "football", "basketball", "soccer", "baseball", "tennis", "golf",
            "olympics", "championship", "game", "match", "season", "playoffs"
        ],
        "crypto": [
            "bitcoin", "ethereum", "crypto", "cryptocurrency", "blockchain",
            "defi", "nft", "web3", "dao", "smart contract"
        ],
        "career": [
            "career", "job search", "interview", "resume", "linkedin",
            "networking", "promotion", "skills", "growth", "mentor"
        ]
    }

    @classmethod
    def infer_themes(cls, post: Post, max_themes: int = 5) -> List[str]:
        """
        Infer themes from a post using keyword matching.

        Args:
            post: Post to analyze
            max_themes: Maximum number of themes to return

        Returns:
            List of detected theme names
        """
        if not post.text:
            return []

        text_lower = post.text.lower()
        detected_themes: Set[str] = set()

        for theme_name, keywords in cls.THEME_KEYWORDS.items():
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    detected_themes.add(theme_name)
                    break  # Found one keyword for this theme, move to next theme

        # Also check hashtags for additional themes
        for hashtag in post.hashtags:
            hashtag_lower = hashtag.lower().replace('#', '')
            for theme_name, keywords in cls.THEME_KEYWORDS.items():
                for keyword in keywords:
                    keyword_normalized = keyword.replace(' ', '').lower()
                    if hashtag_lower == keyword_normalized or keyword_normalized in hashtag_lower:
                        detected_themes.add(theme_name)

        # Return sorted list, limited to max_themes
        return sorted(list(detected_themes))[:max_themes]

    @classmethod
    def infer_themes_bulk(cls, posts: List[Post], max_themes: int = 5) -> List[Post]:
        """
        Infer themes for multiple posts and update them in place.

        Args:
            posts: List of posts to analyze
            max_themes: Maximum themes per post

        Returns:
            List of posts with updated inferred_themes
        """
        for post in posts:
            post.inferred_themes = cls.infer_themes(post, max_themes)
        return posts