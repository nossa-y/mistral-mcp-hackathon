"""
Normalized data structures for ColdOpen Coach.
Source-agnostic models for representing social media data.
Designed for Le Chat integration - MCP servers provide clean data, Le Chat handles conversation coaching.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum


class Platform(str, Enum):
    """Supported social media platforms"""
    X = "x"
    LINKEDIN = "linkedin"


class Person(BaseModel):
    """Represents a person across platforms"""
    name: str = Field(..., description="Display name or handle")
    platform: Platform = Field(..., description="Source platform")
    profile_url: Optional[str] = Field(None, description="Full profile URL")
    handle: Optional[str] = Field(None, description="Username/handle")
    headline_or_bio: str = Field(default="", description="Brief bio or headline")


class Post(BaseModel):
    """Represents a single social media post"""
    platform: Platform = Field(..., description="Source platform")
    post_id: str = Field(..., description="Unique post identifier")
    url: str = Field(..., description="Direct link to post")
    created_at_iso: str = Field(..., description="ISO 8601 creation timestamp")
    text: str = Field(..., description="Post content")
    hashtags: List[str] = Field(default_factory=list, description="Extracted hashtags")
    mentions: List[str] = Field(default_factory=list, description="Mentioned users")
    engagement: Dict[str, int] = Field(default_factory=dict, description="Like/retweet counts")
    inferred_themes: List[str] = Field(default_factory=list, description="Detected themes")


class Meta(BaseModel):
    """Metadata about the data fetch"""
    source: str = Field(..., description="MCP server name that fetched data")
    fetched_at_iso: str = Field(..., description="ISO 8601 fetch timestamp")
    limit: int = Field(..., description="Requested post limit")
    total_found: int = Field(default=0, description="Total posts found")


class Bundle(BaseModel):
    """Complete normalized response bundle - ready for Le Chat consumption"""
    person: Person = Field(..., description="Person information")
    posts: List[Post] = Field(default_factory=list, description="Recent posts")
    meta: Meta = Field(..., description="Fetch metadata")