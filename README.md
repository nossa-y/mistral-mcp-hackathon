# ColdOpen Coach - Le Chat Integration

At events, it's often awkward to approach someone you recognize from LinkedIn or X but don't know how to start the conversation. **ColdOpen Coach** solves this by providing MCP servers that fetch a person's latest public posts, which **Mistral's Le Chat** can then use to generate:

- **A short, natural opener** that echoes the theme of their most recent post (without sounding scripted)
- **A light follow-up question** that keeps the conversation flowing
- **A quick coaching note** on tone and delivery

**Le Chat handles the conversation coaching - our MCP servers just provide clean, structured social media data.**

## Architecture

ColdOpen Coach provides **2 focused MCP servers** that integrate seamlessly with Le Chat:

- `mcp_x` → tool: `x.get_recent_posts` - Fetches Twitter/X posts via Apify
- `mcp_linkedin` → tool: `linkedin.get_recent_posts` - Fetches LinkedIn posts via Apify

**Le Chat orchestrates everything else** - data analysis, conversation generation, and coaching advice.

## Features

- ✅ **Clean MCP Integration**: Purpose-built tools for Le Chat consumption
- ✅ **Fresh Data**: Fetches posts from the last 30 days via Apify APIs
- ✅ **No Caching**: Real-time data on every request
- ✅ **Theme Detection**: Automatically categorizes posts (AI, hiring, fundraising, etc.)
- ✅ **Normalized Output**: Platform-agnostic JSON structures
- ✅ **Error Handling**: Clear messages for rate limits, private profiles, invalid inputs
- ✅ **Le Chat Ready**: Structured data that Le Chat can consume directly

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

### 3. Run MCP Servers

```bash
# Consolidated Social MCP server (includes both X and LinkedIn tools)
python social_mcp_server/server.py
```

### 4. Test Data Fetching

```bash
# Test Twitter data fetch
python demo/fetch_data.py --twitter-handle elonmusk

# Test LinkedIn data fetch
python demo/fetch_data.py --linkedin-url "https://linkedin.com/in/reidhoffman"
```

## Le Chat Integration

Once the MCP servers are running, Le Chat can use them directly:

### Example Le Chat Workflow:

1. **User**: "Help me start a conversation with @elonmusk at this conference"

2. **Le Chat**: *Calls `x.get_recent_posts` with handle "elonmusk"*

3. **MCP Server**: Returns clean JSON with recent posts, themes, engagement data

4. **Le Chat**: Analyzes the data and generates:
   ```
   **Opener**: "I'm curious about your thoughts on the current state of AI development tools -
   the space seems to be evolving incredibly fast."

   **Follow-up**: "What do you think developers need most that they're not getting yet?"

   **Coaching**: "Lead with genuine curiosity. He's clearly passionate about dev tooling
   and AI advancement, so focus on the intersection of those interests."
   ```

## MCP Tool Schemas

### X Server: `x.get_recent_posts`

**Input:**
```json
{
  "handle": "elonmusk",
  "limit": 20
}
```

**Output:**
```json
{
  "person": {
    "name": "@elonmusk",
    "platform": "x",
    "handle": "elonmusk",
    "profile_url": "https://twitter.com/elonmusk"
  },
  "posts": [
    {
      "platform": "x",
      "post_id": "1234567890",
      "url": "https://twitter.com/elonmusk/status/1234567890",
      "created_at_iso": "2024-01-15T10:30:00Z",
      "text": "Just shipped a new AI agent feature...",
      "hashtags": ["#AI", "#DevTools"],
      "engagement": {"likes": 245, "retweets": 67},
      "inferred_themes": ["ai_agents", "shipping_quality"]
    }
  ],
  "meta": {
    "source": "mcp_x",
    "fetched_at_iso": "2024-01-16T12:00:00Z",
    "limit": 20,
    "total_found": 2
  }
}
```

### LinkedIn Server: `linkedin.get_recent_posts`

**Input:**
```json
{
  "profile_url": "https://linkedin.com/in/username",
  "limit": 10
}
```

**Output:** Same structure as X server, but with `platform: "linkedin"`

## Data Structure

### Normalized Post
```json
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

### Detected Themes

The system automatically detects these themes:
- `ai_agents` - AI, LLM, ChatGPT, Claude, machine learning
- `shipping_quality` - Deploy, launch, testing, bugs, builds
- `product_experiments` - A/B tests, MVPs, user research, prototypes
- `fundraising` - Funding, investors, Series A/B, VC, pitch
- `hiring` - Recruiting, job openings, team building, engineers
- `open_source` - OSS, GitHub, contributions, pull requests
- `design_systems` - UI/UX, component libraries, Figma, wireframes
- `sports` - Football, basketball, Olympics, games, championships
- `crypto` - Bitcoin, blockchain, DeFi, NFTs, Web3
- `career` - Job search, networking, growth, mentorship

## Error Handling

Clear error classification for Le Chat:

- `NOT_FOUND` - No posts found for the profile
- `RATE_LIMITED` - Apify API throttling (retry later)
- `SCHEMA_MISMATCH` - Actor response format changed
- `PRIVATE_PROFILE` - Profile is not public
- `INVALID_INPUT` - Invalid handle or URL format
- `API_ERROR` - General API or network error

## Project Structure

```
coldopen-coach/
├── requirements.txt           # Minimal dependencies (MCP, Apify, Pydantic)
├── .env.example              # Environment template
├── shared/
│   ├── models.py            # Clean data models for Le Chat
│   └── theme_inference.py   # Theme detection engine
├── social_mcp_server/       # Consolidated social media MCP server
│   └── server.py            # Combined X/Twitter and LinkedIn MCP server
└── README.md               # This file
```

## Le Chat Conversation Prompts

Here are example prompts you can use with Le Chat once the servers are running:

### Basic Usage
```
"Help me start a conversation with [person] at this networking event.
Use the mcp_x server to get their recent tweets first."
```

### With Context
```
"I'm meeting [person] at a tech conference tomorrow. We both work in AI.
Fetch their recent LinkedIn posts and suggest a natural conversation opener."
```

### Specific Scenario
```
"I want to approach [person] who I know from Twitter. Get their recent posts
and help me find common ground for a respectful introduction at this startup event."
```

## Development

### Adding New Platforms

1. Add new tool to `social_mcp_server/server.py`
2. Implement `get_[platform]_posts` tool following existing patterns
3. Use the same Bundle/Post/Person data structure
4. Add platform to Platform enum in shared/models.py

### Extending Theme Detection

Edit `shared/theme_inference.py` and add keywords to `THEME_KEYWORDS`.

### Custom Apify Actors

Override default actors in `.env`:
```bash
APIFY_TWITTER_ACTOR=your_custom_actor
APIFY_LINKEDIN_POSTS_ACTOR=your_linkedin_actor
```

## Why This Architecture?

**🎯 Focused MCP Servers**: Each server does one thing well - fetch and normalize social data
**🧠 Le Chat Orchestration**: Advanced conversation coaching handled by Mistral's AI
**🔄 Clean Integration**: Standard MCP protocol, no custom APIs
**📊 Structured Output**: JSON that AI can easily consume and reason about
**⚡ Real-time**: No caching, fresh data every time
**🛡️ Error Resilient**: Clear error states for robust AI workflows

## License

MIT License - see LICENSE file for details.

---

**ColdOpen Coach** - Clean social data for Le Chat conversation coaching. 🤝