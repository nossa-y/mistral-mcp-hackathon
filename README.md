# ColdOpen Coach - MCP Server Collection

A collection of Model Context Protocol (MCP) servers for the Mistral MCP Hackathon that helps generate personalized cold outreach suggestions by collecting social media data from Twitter/X and LinkedIn.

## Features

- **Multi-platform Social Data**: Fetch recent posts from Twitter/X (via Apify) and LinkedIn
- **Normalized Data Models**: Clean, structured data ready for AI conversation coaching
- **Modular MCP Architecture**: Separate servers for X, LinkedIn, and coaching logic
- **Theme Detection**: Automatic inference of conversation topics from social posts
- **Privacy-First**: No contact harvesting, focused on public social content only

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- API keys for:
  - [Apify](https://apify.com/) (for Twitter/X scraping)
  - LinkedIn `li_at` cookie (for LinkedIn access - optional)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/nossa-y/mistral-mcp-hackathon.git
cd mistral-mcp-hackathon/coldopen-coach
```

### 2. Install Dependencies

Using uv (recommended):

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and create virtual environment
uv sync
```

Or using pip:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the `coldopen-coach` directory:

```bash
cp .env.example .env  # If available, or create manually
```

Add your API credentials:

```env
# Required API Keys
APIFY_TOKEN=your_apify_token_here

# Optional: LinkedIn Access (for LinkedIn MCP server)
LINKEDIN_COOKIE=li_at=your_linkedin_cookie_here

# Development settings
DEBUG=true
```

### 4. Run the MCP Servers

This project contains multiple MCP servers. You can run them individually:

#### Twitter/X MCP Server
```bash
# Using uv
uv run python -m mcp_servers.mcp_x.server

# Or with activated venv
source .venv/bin/activate
python -m mcp_servers.mcp_x.server
```

#### LinkedIn MCP Server (optional)
```bash
# Using uv
uv run python -m mcp_servers.mcp_linkedin.server

# Or with activated venv
source .venv/bin/activate
python -m mcp_servers.mcp_linkedin.server
```

#### Approach Coach MCP Server
```bash
# Using uv
uv run python -m mcp_servers.mcp_approach_coach.server

# Or with activated venv
source .venv/bin/activate
python -m mcp_servers.mcp_approach_coach.server
```

## MCP Tools Available

The project provides several MCP servers, each exposing different tools:

### Twitter/X MCP Server
- `fetch_recent_posts` - Get recent posts from a Twitter/X user
- `search_posts` - Search for posts by keywords or hashtags

### LinkedIn MCP Server
- `get_person_profile` - Get LinkedIn profile information
- `get_recent_activity` - Fetch recent LinkedIn posts and activity

### Approach Coach MCP Server
- `analyze_social_context` - Analyze social media posts for conversation starters
- `generate_openers` - Create personalized outreach messages
- `suggest_themes` - Identify common themes and interests

## Usage Examples

### Basic Usage with Claude Desktop or Le Chat

Configure your MCP client to connect to the servers:

```json
{
  "mcpServers": {
    "coldopen-x": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_servers.mcp_x.server"],
      "cwd": "/path/to/mistral-mcp-hackathon/coldopen-coach"
    },
    "coldopen-linkedin": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_servers.mcp_linkedin.server"],
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

### Fetch Recent Posts

```python
# Fetch Twitter/X posts
{
  "tool": "fetch_recent_posts",
  "arguments": {
    "username": "elonmusk",
    "limit": 10
  }
}
```

### Generate Conversation Starters

```python
# Analyze social context and generate openers
{
  "tool": "generate_openers",
  "arguments": {
    "social_data": "[normalized social media posts]",
    "tone": "professional",
    "count": 3
  }
}
```

## Development

### Project Structure

```
coldopen-coach/
├── mcp_servers/         # MCP server implementations
│   ├── mcp_x/          # Twitter/X integration (Apify)
│   │   └── server.py   # X/Twitter MCP server
│   ├── mcp_linkedin/   # LinkedIn integration
│   │   └── server.py   # LinkedIn MCP server
│   └── mcp_approach_coach/ # Cold outreach coaching logic
│       └── server.py   # Approach coach MCP server
├── shared/             # Shared models and utilities
│   ├── models.py       # Normalized data models
│   └── theme_inference.py # Theme analysis utilities
├── demo/               # Demo scripts and examples
│   └── fetch_data.py   # Example data fetching
├── test_basic.py       # Basic tests
├── requirements.txt    # Python dependencies
└── pyproject.toml      # Project configuration
```

### Running Tests

```bash
# Run basic tests
uv run python test_basic.py

# Run demo
uv run python demo/fetch_data.py
```

### Testing Individual Servers

You can test each MCP server individually:

```bash
# Test the X/Twitter server
echo '{"method": "tools/list", "params": {}}' | uv run python -m mcp_servers.mcp_x.server

# Test the LinkedIn server
echo '{"method": "tools/list", "params": {}}' | uv run python -m mcp_servers.mcp_linkedin.server

# Test the approach coach server
echo '{"method": "tools/list", "params": {}}' | uv run python -m mcp_servers.mcp_approach_coach.server
```

## API Keys Setup

### Getting Your Apify Token
1. Sign up at [apify.com](https://apify.com)
2. Go to Settings → Integrations → API tokens
3. Create a new token and copy it to your `.env` file

### Getting Your Apollo.io API Key
1. Sign up at [apollo.io](https://apollo.io)
2. Go to Settings → API
3. Generate an API key and add it to your `.env` file

### Getting LinkedIn Cookie (Optional)
1. Log into LinkedIn in your browser
2. Open Developer Tools (F12) → Application → Cookies
3. Find the `li_at` cookie value and add it to your `.env` file as `LINKEDIN_COOKIE=li_at=your_cookie_value`

⚠️ **Warning**: LinkedIn scraping may violate their Terms of Service. Use responsibly and ensure you have proper consent. The LinkedIn server is optional and not required for basic functionality.

## Compliance & Privacy

- **Public Data Only**: Only collects publicly available social media posts
- **No Contact Harvesting**: Does not collect private contact information
- **Consent Required**: LinkedIn integration requires explicit user opt-in with cookie
- **Cost Transparency**: Apify usage costs are transparent via their pricing
- **Ethical AI**: Designed for legitimate networking and relationship building

## Deployment

### Running in Production

For production deployment, each MCP server should be run as a separate service:

```bash
# Using systemd or process manager
# Start each server with proper environment variables
APYFY_TOKEN=your_token python -m mcp_servers.mcp_x.server
LINKEDIN_COOKIE=your_cookie python -m mcp_servers.mcp_linkedin.server
python -m mcp_servers.mcp_approach_coach.server
```

### Production Considerations

- Set proper environment variables for API keys
- Configure logging levels appropriately
- Monitor API usage and costs (especially Apify)
- Implement proper error handling and retries
- Consider rate limiting for API calls

## Troubleshooting

### Common Issues

1. **LinkedIn Cookie Expired**: Update your `li_at` cookie value in `.env`
2. **Apify Rate Limits**: Check your Apify plan limits and usage
3. **MCP Connection Issues**: Verify your MCP client configuration
4. **Missing Dependencies**: Run `uv sync` or `pip install -r requirements.txt`
5. **Environment Variables**: Ensure `.env` file is in the correct directory

### Debugging

Each MCP server provides detailed logging. Check the console output when running the servers for detailed error information and API call traces.

You can also test the demo scripts:
```bash
# Test data fetching
uv run python demo/fetch_data.py

# Run basic functionality tests
uv run python test_basic.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`uv run python test_basic.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
- Create an issue on GitHub
- Check the logs for detailed error messages
- Verify your API keys and environment configuration