# Social Snapshot Hub - MCP Server

A Model Context Protocol (MCP) server that orchestrates social media data collection and generates personalized cold outreach suggestions by integrating with Apify (Twitter/X), LinkedIn, and Apollo.io APIs.

## Features

- **Multi-platform Social Data**: Fetch recent posts from Twitter/X (via Apify) and LinkedIn
- **Professional Context**: Gather candidate information from Apollo.io
- **Smart Suggestions**: Generate contextual cold outreach messages in casual, professional, and playful tones
- **Privacy-First**: Ephemeral data storage with configurable TTL (24h default)
- **Compliance**: Built-in consent flows and ToS warnings for LinkedIn usage

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- API keys for:
  - [Apify](https://apify.com/) (for Twitter/X scraping)
  - [Apollo.io](https://apollo.io/) (for professional data)
  - LinkedIn `li_at` cookie (for LinkedIn access)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
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

### 3. Environment Configuration

Create a `.env` file in the `coldopen-coach` directory:

```bash
cp .env.example .env  # If available, or create manually
```

Add your API credentials:

```env
# Required API Keys
APIFY_TOKEN=your_apify_token_here
APOLLO_IO_API_KEY=your_apollo_api_key_here
LINKEDIN_COOKIE=li_at=your_linkedin_cookie_here

# Server Configuration
PORT=8080
SERVER_TOKEN=your_secure_server_token_here
ALLOWED_ORIGINS=https://chat.mistral.ai

# Cache & Storage
CACHE_TTL_HOURS=24
MAX_TWEETS_DEFAULT=50
STORAGE_BACKEND=memory

# Optional: File/S3 storage
# DISK_PATH=/var/lib/social-snapshot
# S3_BUCKET=your-bucket
# S3_REGION=us-east-1
# S3_PREFIX=snapshots/
```

### 4. Run the Server

Using uv:

```bash
# Activate the virtual environment and run
uv run python main.py
```

Or alternatively:

```bash
# Activate virtual environment manually
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python main.py
```

The server will start on `http://localhost:8080` (or the port specified in your `.env` file).

## API Endpoints

### Health Checks
- `GET /healthz` - Health check endpoint
- `GET /readyz` - Readiness check endpoint
- `GET /metrics` - Prometheus metrics (optional)

### MCP Tools

The server exposes several MCP tools under different namespaces:

#### Social Context Tools
- `social.fetch_contexts` - Fetch LinkedIn and Apollo contexts in parallel
- `social.fetch_posts` - Get recent posts from Twitter/X and LinkedIn
- `social.suggest_openers` - Generate personalized cold outreach suggestions

#### Apollo Tools
- `apollo.search_candidates` - Search for candidates using Apollo.io

#### Vision Tools
- `vision.face_match_placeholder` - Placeholder for face recognition (non-functional)

## Usage Examples

### Basic Usage with Le Chat (Mistral AI)

Configure Le Chat to connect to your MCP server:

```json
{
  "mcpServers": {
    "social-snapshot": {
      "url": "http://localhost:8080/mcp",
      "headers": {
        "Authorization": "Bearer your_server_token_here"
      }
    }
  }
}
```

### Fetch Social Contexts

```python
# Example tool call
{
  "tool": "social.fetch_contexts",
  "arguments": {
    "first_name": "John",
    "last_name": "Doe",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "organization_name": "Acme Corp",
    "apollo_limit": 2
  }
}
```

### Generate Cold Outreach Suggestions

```python
{
  "tool": "social.suggest_openers",
  "arguments": {
    "linkedin_context_resource": "resource://contexts/linkedin/abc123.md",
    "apollo_context_resource": "resource://contexts/apollo/def456.md",
    "tone_options": ["casual", "professional", "playful"]
  }
}
```

## Development

### Project Structure

```
coldopen-coach/
├── main.py              # Main server entry point
├── mcp_servers/         # MCP server implementations
│   ├── mcp_x/          # Twitter/X integration
│   ├── mcp_linkedin/   # LinkedIn integration
│   └── mcp_approach_coach/ # Cold outreach logic
├── shared/             # Shared models and utilities
│   ├── models.py       # Data models
│   └── theme_inference.py # Theme analysis
├── demo/               # Demo scripts
└── pyproject.toml      # Project dependencies
```

### Running Tests

```bash
# Run basic tests
uv run python test_basic.py

# Run demo
uv run python demo/run_demo.py
```

### Development Server

For development with auto-reload:

```bash
# Install development dependencies
uv add --dev watchdog

# Run with auto-reload (if implemented)
uv run python main.py --reload
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

### Getting LinkedIn Cookie
1. Log into LinkedIn in your browser
2. Open Developer Tools (F12) → Application → Cookies
3. Find the `li_at` cookie value and add it to your `.env` file as `LINKEDIN_COOKIE=li_at=your_cookie_value`

⚠️ **Warning**: LinkedIn scraping may violate their Terms of Service. Use responsibly and ensure you have proper consent.

## Compliance & Privacy

- **Data Retention**: Default 24-hour TTL for all cached data
- **No Contact Harvesting**: Only public profile information is collected
- **Consent Required**: LinkedIn integration requires explicit user opt-in
- **Cost Transparency**: Apify costs are estimated before execution

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t social-snapshot-hub .

# Run container
docker run -p 8080:8080 --env-file .env social-snapshot-hub
```

### Production Considerations

- Use a secure `SERVER_TOKEN`
- Configure `ALLOWED_ORIGINS` for your domain
- Set up proper logging and monitoring
- Consider using Redis for distributed caching
- Implement rate limiting for production traffic

## Troubleshooting

### Common Issues

1. **LinkedIn Cookie Expired**: Update your `li_at` cookie value in `.env`
2. **Apify Rate Limits**: Check your Apify plan limits and usage
3. **Apollo API Errors**: Verify your API key and subscription status
4. **Port Already in Use**: Change the `PORT` in your `.env` file

### Logs

The server uses structured JSON logging. Check logs for detailed error information and API call traces.

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