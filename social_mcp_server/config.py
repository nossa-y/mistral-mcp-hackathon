"""Configuration management for Social MCP Server"""

import os
from typing import Optional
from pydantic import BaseModel, Field
try:
    from python_dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional
    pass


class Config(BaseModel):
    """Configuration settings for the Social MCP Server"""

    # Apify configuration
    apify_token: Optional[str] = Field(
        default=None,
        description="Apify API token for scraping social media data"
    )

    apify_twitter_actor: str = Field(
        default="apidojo/tweet-scraper",
        description="Apify actor ID for Twitter scraping"
    )

    apify_linkedin_posts_actor: str = Field(
        default="your_linkedin_posts_actor",
        description="Apify actor ID for LinkedIn posts scraping"
    )

    # Server configuration
    server_name: str = Field(
        default="Social MCP Server",
        description="Name of the MCP server"
    )

    # HTTP server configuration
    host: str = Field(
        default="127.0.0.1",
        description="HTTP server host address"
    )

    port: int = Field(
        default=8000,
        description="HTTP server port"
    )

    server_token: Optional[str] = Field(
        default=None,
        description="Bearer token for server authentication"
    )

    allowed_origins: str = Field(
        default="https://chat.mistral.ai",
        description="Comma-separated list of allowed CORS origins"
    )

    # Default limits
    default_freshness_days: int = Field(
        default=30,
        description="Default number of days to look back for posts"
    )

    default_post_limit_x: int = Field(
        default=20,
        description="Default limit for X/Twitter posts"
    )

    default_post_limit_linkedin: int = Field(
        default=10,
        description="Default limit for LinkedIn posts"
    )

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables"""
        return cls(
            apify_token=os.getenv("APIFY_TOKEN"),
            apify_twitter_actor=os.getenv("APIFY_TWITTER_ACTOR", "apidojo/tweet-scraper"),
            apify_linkedin_posts_actor=os.getenv("APIFY_LINKEDIN_POSTS_ACTOR", "your_linkedin_posts_actor"),
            server_name=os.getenv("SERVER_NAME", "Social MCP Server"),
            host=os.getenv("HOST", "127.0.0.1"),
            port=int(os.getenv("PORT", "8000")),
            server_token=os.getenv("SERVER_TOKEN"),
            allowed_origins=os.getenv("ALLOWED_ORIGINS", "https://chat.mistral.ai"),
            default_freshness_days=int(os.getenv("DEFAULT_FRESHNESS_DAYS", "30")),
            default_post_limit_x=int(os.getenv("DEFAULT_POST_LIMIT_X", "20")),
            default_post_limit_linkedin=int(os.getenv("DEFAULT_POST_LIMIT_LINKEDIN", "10")),
        )


# Global configuration instance
config = Config.from_env()