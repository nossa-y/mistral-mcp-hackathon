# Le Chat HTTP MCP Server Configuration

## HTTP MCP Server Setup

The Social MCP Server now supports HTTP transport for Le Chat integration!

### 1. Start HTTP Server

```bash
# Basic HTTP server (no authentication)
uv run social-mcp-server --http

# With custom port
uv run social-mcp-server --http --port 9000

# With debug logging
uv run social-mcp-server --http --debug

# With authentication (recommended)
export SERVER_TOKEN="your-secure-token-here"
export APIFY_TOKEN="your-apify-token-here"
uv run social-mcp-server --http
```

### 2. Server Endpoints

Once started, the server provides:

- **MCP Endpoint**: `http://localhost:8000/mcp`
- **Health Check**: `http://localhost:8000/health`
- **Readiness Check**: `http://localhost:8000/readiness`

### 3. Le Chat Configuration

#### Option A: No Authentication (Development)
```json
{
  "mcpServers": {
    "social-mcp": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
      }
    }
  }
}
```

#### Option B: With Bearer Token (Recommended)
```json
{
  "mcpServers": {
    "social-mcp": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "Authorization": "Bearer your-secure-token-here",
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
      }
    }
  }
}
```

### 4. Environment Variables

Set these environment variables before starting the server:

```bash
# Required for API functionality
export APIFY_TOKEN="your-apify-token-here"

# Optional for authentication
export SERVER_TOKEN="your-secure-token-here"

# Optional customization
export HOST="127.0.0.1"
export PORT="8000"
export ALLOWED_ORIGINS="https://chat.mistral.ai,https://le-chat.mistral.ai"

# Optional Apify actor overrides
export APIFY_TWITTER_ACTOR="apidojo/tweet-scraper"
export APIFY_LINKEDIN_POSTS_ACTOR="your_linkedin_posts_actor"
```

### 5. Available Tools

Once connected, Le Chat will have access to:

- **get_x_posts**: Fetch recent posts from X/Twitter
  - Parameters: `handle` (string), `limit` (int, default: 20)
  - Example: `get_x_posts("elonmusk", 10)`

- **get_linkedin_posts**: Fetch recent posts from LinkedIn
  - Parameters: `profile_url` (string), `limit` (int, default: 10)
  - Example: `get_linkedin_posts("https://linkedin.com/in/username", 5)`

### 6. Testing the Setup

You can test the server is working:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test readiness with details
curl http://localhost:8000/readiness

# Test MCP endpoint (with auth if enabled)
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }'
```

### 7. Production Deployment

For production deployment (e.g., on Alpic):

1. Set `HOST="0.0.0.0"` to accept external connections
2. Always set `SERVER_TOKEN` for security
3. Configure `ALLOWED_ORIGINS` for your domain
4. Use a reverse proxy (nginx) for HTTPS termination
5. Set up health check monitoring on `/health`

### 8. Troubleshooting

Common issues:

- **Connection refused**: Check if server is running and port is correct
- **401 Unauthorized**: Set `SERVER_TOKEN` and include `Authorization` header
- **CORS errors**: Add your domain to `ALLOWED_ORIGINS`
- **No tools available**: Check server logs for tool registration errors

### 9. Development vs Production

**Development** (local testing):
- Use HTTP (http://localhost:8000)
- Authentication optional
- Single origin allowed

**Production** (deployed):
- Use HTTPS with proper certificates
- Authentication required (`SERVER_TOKEN`)
- Multiple origins allowed
- Health checks enabled
- Proper logging configured

## Benefits of HTTP Transport

- ✅ **No command-line dependencies**: Le Chat connects via URL
- ✅ **Better error handling**: HTTP status codes and JSON responses
- ✅ **Health monitoring**: Built-in health check endpoints
- ✅ **Authentication**: Bearer token security
- ✅ **CORS support**: Proper cross-origin handling
- ✅ **Scalable**: Can be deployed on cloud platforms
- ✅ **Debuggable**: Easy to test with curl/Postman