# ColdOpen Coach

At events, it's often awkward to approach someone you recognize from LinkedIn or X but don't know how to start the conversation. **ColdOpen Coach** solves this by fetching a person's latest public posts and generating:

- **A short, natural opener** that echoes the theme of their most recent post (without sounding scripted)
- **A light follow-up question** that keeps the conversation flowing
- **A quick coaching note** on tone and delivery

The result: anyone can type in a name, the app pulls their fresh public signals, and instantly gives you a respectful, human-sounding way to break the ice.

## Architecture

ColdOpen Coach is built using **Model Context Protocol (MCP)** servers that wrap Apify APIs:

- `mcp_x` → tool: `x.get_recent_posts`
- `mcp_linkedin` → tool: `linkedin.get_recent_posts`
- `mcp_approach_coach` → tool: `approach.build_prompt`

## Features

- ✅ **Fresh data**: Fetches posts from the last 30 days (configurable)
- ✅ **No caching**: Every call hits Apify directly for real-time data
- ✅ **Theme detection**: Automatically categorizes posts by topics (AI, hiring, shipping, etc.)
- ✅ **Fallback handling**: Graceful degradation when no recent posts are found
- ✅ **Error handling**: Clear messages for rate limits, private profiles, invalid inputs
- ✅ **Normalized data**: Source-agnostic data structures across platforms

## Quick Start

### 1. Setup

```bash
# Clone and navigate to the project
cd coldopen-coach

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your APIFY_TOKEN
```

### 2. Configure Apify

You'll need:
- An [Apify](https://apify.com) account and API token
- Access to Twitter/X and LinkedIn post scraping actors

Add to your `.env`:
```bash
APIFY_TOKEN=your_apify_token_here
APIFY_TWITTER_ACTOR=apidojo/tweet-scraper
APIFY_LINKEDIN_POSTS_ACTOR=your_linkedin_posts_actor
```

### 3. Run Demo

```bash
# Twitter only
python demo/run_demo.py --twitter-handle elonmusk --your-name "Alex"

# LinkedIn only
python demo/run_demo.py --linkedin-url "https://linkedin.com/in/username" --your-name "Alex"

# Both platforms
python demo/run_demo.py --twitter-handle elonmusk --linkedin-url "https://linkedin.com/in/username" --your-name "Alex"
```

### 4. MCP Server Usage

Each server can be run independently:

```bash
# X/Twitter server
python mcp_servers/mcp_x/server.py

# LinkedIn server
python mcp_servers/mcp_linkedin/server.py

# Approach coach orchestrator
python mcp_servers/mcp_approach_coach/server.py
```

## API Reference

### X Server: `x.get_recent_posts`

**Input:**
```json
{
  "handle": "elonmusk",
  "limit": 20
}
```

**Output:** Normalized bundle with person info, posts, and metadata

### LinkedIn Server: `linkedin.get_recent_posts`

**Input:**
```json
{
  "profile_url": "https://linkedin.com/in/username",
  "limit": 10
}
```

**Output:** Normalized bundle with person info, posts, and metadata

### Orchestrator: `approach.build_prompt`

**Input:**
```json
{
  "bundles": [/* array of bundles from X/LinkedIn servers */],
  "user_context": {
    "your_name": "Alex",
    "shared_signals": "Both work in AI",
    "event_context": "Tech conference"
  },
  "preferences": {
    "tone": "friendly",
    "language": "en",
    "freshness_days": 30
  }
}
```

**Output:** Structured prompt blocks for Claude with system/developer/user instructions

## Data Models

### Normalized Post Structure
```python
{
  "platform": "x" | "linkedin",
  "post_id": "unique_identifier",
  "url": "direct_link_to_post",
  "created_at_iso": "2024-01-15T10:30:00Z",
  "text": "Post content...",
  "hashtags": ["#AI", "#DevTools"],
  "mentions": ["@username"],
  "engagement": {"likes": 245, "retweets": 67},
  "inferred_themes": ["ai_agents", "shipping_quality"]
}
```

### Theme Categories

The system automatically detects these themes:
- `ai_agents` - AI, LLM, ChatGPT, Claude, etc.
- `shipping_quality` - Deploy, launch, testing, bugs
- `product_experiments` - A/B tests, MVPs, user research
- `fundraising` - Funding, investors, Series A/B
- `hiring` - Recruiting, job openings, team building
- `open_source` - OSS, GitHub, contributions
- `design_systems` - UI/UX, component libraries
- `sports` - Football, basketball, Olympics
- `crypto` - Bitcoin, blockchain, DeFi
- `career` - Job search, networking, growth

## Error Handling

The system provides clear error classification:

- `NOT_FOUND` - No posts found for the profile
- `RATE_LIMITED` - Apify API throttling
- `SCHEMA_MISMATCH` - Actor response format changed
- `PRIVATE_PROFILE` - Profile is not public
- `INVALID_INPUT` - Invalid handle or URL
- `API_ERROR` - General API or network error

## Project Structure

```
coldopen-coach/
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── shared/                   # Common data structures
│   ├── models.py            # Pydantic models
│   └── theme_inference.py   # Theme detection engine
├── mcp_servers/             # MCP server implementations
│   ├── mcp_x/
│   │   └── server.py        # X/Twitter MCP server
│   ├── mcp_linkedin/
│   │   └── server.py        # LinkedIn MCP server
│   └── mcp_approach_coach/
│       └── server.py        # Orchestrator MCP server
├── demo/
│   └── run_demo.py          # Demo script
└── README.md               # This file
```

## Development

### Adding New Platforms

1. Create new MCP server in `mcp_servers/mcp_[platform]/`
2. Implement `[platform].get_recent_posts` tool
3. Add normalization logic for platform-specific data
4. Update theme inference if needed

### Extending Theme Detection

Edit `shared/theme_inference.py` and add new keywords to `THEME_KEYWORDS` dictionary.

### Custom Apify Actors

Override default actors in `.env`:
```bash
APIFY_TWITTER_ACTOR=your_custom_actor
APIFY_LINKEDIN_POSTS_ACTOR=your_linkedin_actor
```

## Limitations

- **No caching**: Each request hits Apify directly (by design for freshness)
- **Rate limits**: Subject to Apify actor rate limiting
- **Public posts only**: Cannot access private or protected content
- **Theme detection**: Simple keyword matching (no ML/AI inference)
- **Demo data**: Current demo uses mock data for illustration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

**ColdOpen Coach** - Making networking conversations natural and respectful, one post at a time. 🤝