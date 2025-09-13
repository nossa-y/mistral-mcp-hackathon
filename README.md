# ColdOpen Coach - MCP Server Collection

🤖 **AI-powered cold outreach coaching using social media insights**

Generate personalized conversation starters by analyzing public social media activity from Twitter/X and LinkedIn. Built as modular MCP servers for seamless integration with AI assistants like Claude Desktop and Mistral Le Chat.

## ✨ What This Does

ColdOpen Coach helps you create better cold outreach messages by:
- 🔍 **Analyzing recent social posts** from Twitter/X and LinkedIn
- 🎯 **Finding conversation starters** based on interests and activities
- 💬 **Generating personalized openers** in different tones (casual, professional, playful)
- 🔒 **Respecting privacy** - only uses public posts, no contact scraping

Perfect for sales professionals, recruiters, and networkers who want to make genuine connections.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (tested with 3.11, 3.12, and 3.13)
- An [Apify](https://apify.com/) account (free tier available)
- Optional: LinkedIn account for LinkedIn data

### 1️⃣ Install

```bash
# Clone the project
git clone https://github.com/nossa-y/mistral-mcp-hackathon.git
cd mistral-mcp-hackathon/coldopen-coach

# Install uv package manager (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

<details>
<summary>💡 Alternative: Using pip instead of uv</summary>

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
</details>

### 2️⃣ Get Your API Key

1. Sign up at [apify.com](https://apify.com) (free tier includes 10,000 credits)
2. Go to Settings → Integrations → API tokens
3. Create a new token and copy it

### 3️⃣ Configure

Create a `.env` file:

```bash
# In the coldopen-coach directory
echo "APIFY_TOKEN=your_apify_token_here" > .env
echo "DEBUG=true" >> .env
```

**Optional LinkedIn Setup:** Add your LinkedIn cookie to access LinkedIn profiles:
```bash
echo "LINKEDIN_COOKIE=li_at=your_linkedin_cookie_here" >> .env
```

<details>
<summary>🔍 How to find your LinkedIn cookie</summary>

1. Log into LinkedIn in your browser
2. Press F12 → Application tab → Cookies → linkedin.com
3. Copy the value of the `li_at` cookie

⚠️ **Note**: LinkedIn may restrict automated access. Use responsibly.
</details>

### 4️⃣ Test Your Setup

```bash
# Test the core X/Twitter server
uv run python -m mcp_servers.mcp_x.server

# Test with a simple demo
uv run python demo/fetch_data.py
```

If you see MCP server output without errors, you're ready to go! 🎉

## 💬 Using with AI Assistants

### Claude Desktop Configuration

Add this to your Claude Desktop MCP settings file:

```json
{
  "mcpServers": {
    "coldopen-x": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_servers.mcp_x.server"],
      "cwd": "/path/to/mistral-mcp-hackathon/coldopen-coach"
    },
    "coldopen-coach": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_servers.mcp_approach_coach.server"],
      "cwd": "/path/to/mistral-mcp-hackathon/coldopen-coach"
    }
  }
}
```

**Replace** `/path/to/` with your actual path to the project.

<details>
<summary>📁 Where to find your MCP settings file</summary>

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

</details>

### Example Workflow

1. **Fetch Data**: "Fetch recent posts from @elonmusk on Twitter"
2. **Analyze**: "Analyze these posts for conversation starters"
3. **Generate**: "Generate 3 cold outreach openers in professional tone"

## 🛠️ Available Tools

| **Server** | **Tool** | **What It Does** |
|------------|----------|------------------|
| **Twitter/X** | `fetch_recent_posts` | Get recent tweets from any public user |
| | `search_posts` | Search tweets by keywords/hashtags |
| **LinkedIn** | `get_person_profile` | Get public LinkedIn profile info |
| | `get_recent_activity` | Fetch recent LinkedIn posts |
| **Coach** | `analyze_social_context` | Find conversation topics from posts |
| | `generate_openers` | Create personalized outreach messages |
| | `suggest_themes` | Identify interests and themes |

## 📋 Example Use Cases

### Sales Professional
```
"Fetch recent posts from @prospect_twitter, analyze for business interests,
and generate 3 professional openers for a SaaS pitch"
```

### Recruiter
```
"Get LinkedIn activity for John Doe at TechCorp, identify recent projects,
and suggest casual conversation starters"
```

### Networker
```
"Find recent posts about 'AI' from @tech_leader, generate playful openers
that reference their interests"
```

## 📚 Detailed Usage Examples

### Working with Twitter/X Data

```bash
# In Claude Desktop or Le Chat, you can ask:
"Fetch the last 15 posts from @elonmusk and summarize his recent interests"

# Or use the tools directly:
fetch_recent_posts(username="elonmusk", limit=15)
```

**Response format:**
```json
{
  "posts": [
    {
      "id": "1234567890",
      "text": "AI will transform everything...",
      "created_at": "2024-01-15T10:30:00Z",
      "metrics": {"likes": 5420, "retweets": 1200}
    }
  ],
  "user_info": {
    "username": "elonmusk",
    "followers": 150000000
  }
}
```

### LinkedIn Profile Analysis

```bash
# Ask Claude:
"Get LinkedIn profile for John Smith at TechCorp and identify recent activity"

# Direct tool usage:
get_person_profile(linkedin_url="https://linkedin.com/in/johnsmith")
```

### Complete Workflow Example

1. **Research Phase:**
   ```
   "Fetch recent posts from @prospect_handle on X and their LinkedIn activity"
   ```

2. **Analysis Phase:**
   ```
   "Based on this data, what are 3 conversation topics I could use for outreach?"
   ```

3. **Generate Openers:**
   ```
   "Write 3 cold outreach messages: one casual, one professional, one creative"
   ```

## 🔧 Development & Testing

### Project Structure

```
coldopen-coach/
├── mcp_servers/         # MCP server implementations
│   ├── mcp_x/          # Twitter/X via Apify
│   └── mcp_linkedin/   # LinkedIn via Apify
├── shared/             # Shared utilities
│   ├── models.py       # Pydantic data models
│   └── theme_inference.py # Theme analysis
├── demo/               # Demo scripts
├── pyproject.toml      # Modern Python config
└── uv.lock            # Dependency lock
```

### Testing Your Setup

```bash
# Run the demo
uv run python demo/fetch_data.py

# Test server directly
echo '{"method": "tools/list", "params": {}}' | uv run python -m mcp_servers.mcp_x.server

# Test dependencies
uv run python test_basic.py
```

## 🤝 Contributing & Support

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test them: `uv run python test_basic.py`
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push and create a Pull Request

### Support & Issues
- 🐛 **Bug reports**: Create an issue on GitHub
- 💡 **Feature requests**: Open a discussion
- 📖 **Documentation**: Check the inline code comments

## 🔒 Privacy & Ethics

- ✅ **Public data only** - No private information scraping
- ✅ **No contact harvesting** - Focuses on conversation starters, not emails/phones
- ✅ **Transparent costs** - Apify usage is clearly tracked
- ✅ **Legitimate use** - Designed for professional networking and relationship building

⚠️ **LinkedIn Note**: Uses Apify actors for LinkedIn data. Ensure compliance with LinkedIn's Terms of Service.

## 🚨 Troubleshooting

### Common Issues

| **Problem** | **Solution** |
|------------|-------------|
| `ModuleNotFoundError` | Run `uv sync` or `pip install -r requirements.txt` |
| LinkedIn "Access Denied" | Update your `li_at` cookie in `.env` file |
| Apify "Insufficient credits" | Check your [Apify usage](https://console.apify.com/billing) and upgrade if needed |
| MCP server won't start | Verify `.env` file exists and contains `APIFY_TOKEN=your_token` |
| "No such file or directory" | Check your working directory is `coldopen-coach/` |

### Quick Diagnostics

```bash
# Test your setup
uv run python -c "import apify_client; print('✅ Dependencies OK')"

# Check environment
uv run python -c "import os; print('✅ APIFY_TOKEN found' if os.getenv('APIFY_TOKEN') else '❌ Missing APIFY_TOKEN')"

# Test MCP server
echo '{"method": "tools/list", "params": {}}' | uv run python -m mcp_servers.mcp_x.server
```

### Still Having Issues?

1. **Check the logs** - Each server shows detailed error messages
2. **Test with demo** - Run `uv run python demo/fetch_data.py`
3. **Verify API keys** - Ensure your Apify token is valid and has credits

---

## 🎯 What's Next?

After setup, you can:
- **Start simple**: Ask Claude to "fetch recent posts from @anyone"
- **Go deeper**: "Analyze this person's interests and suggest conversation topics"
- **Get creative**: "Write personalized outreach messages based on their posts"

**Happy networking!** 🚀

---

*Built for the Mistral MCP Hackathon • Powered by Apify & FastMCP*