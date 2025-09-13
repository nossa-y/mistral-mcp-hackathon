# ColdOpen Coach - MCP Server Collection

## Current Implementation Status (Python)

This project currently consists of **separate Python MCP servers** for the Mistral MCP Hackathon:

- **mcp_x** - Twitter/X integration via Apify
- **mcp_linkedin** - LinkedIn integration (optional)
- **mcp_approach_coach** - Cold outreach coaching logic

Each server runs independently using stdio transport and can be configured in MCP clients like Claude Desktop or Le Chat.

## Future HTTP Specification (Node.js/TypeScript)

The specification below outlines a **future consolidated HTTP MCP server** ("Social Snapshot Hub") for Le Chat deployment on Alpic. This would replace the current separate Python servers with a single HTTP-exposed server.

---

# HTTP MCP Server Specification (Future Implementation)

Purpose: A single HTTP‑exposed MCP server that Mistral Le Chat connects to. The hub would orchestrate:
- Apify Tweet Scraper V2 (X/Twitter recent posts)
- LinkedIn MCP (recent activity/posts only)
- Apollo.io MCP (multi‑profile candidate search; use top two)
- Face Recognition Placeholder (non‑functional, consent‑gated stub)

1) Product Scope & Guardrails (Step‑1+)
In scope
Fetch recent posts only from X (via Apify) and LinkedIn (visible recent activity) for up to two Apollo‑selected candidates.


Build a posts‑only context and produce 3 grounded cold‑open suggestions (casual / professional / playful), each with a one‑line rationale.


Optional soft verification using Apollo (name ↔ org/domain plausibility).


Out of scope
CV/employment history scraping, contact discovery, any real face recognition or identity stitching.


Compliance
LinkedIn scraping may violate ToS: require explicit opt‑in, user supplies their own li_at cookie.


Apify calls show an estimated cost before execution.


Default retention: ephemeral (24h TTL; configurable down to 0).


FR remains placeholder only in this Step‑1+ release.



2) Transport: HTTP MCP Server (not stdio)
Implement MCP HTTP transport per MCP SDK/HTTP guide.


Expose a single base URL (e.g., https://social-snapshot.<alpic-domain>/mcp).


Require Authorization: Bearer <SERVER_TOKEN> header on all MCP endpoints.


Provide /healthz (200 OK) and /readyz (200 OK) non‑MCP endpoints for probes.


Enable CORS only for configured Le Chat origins (env ALLOWED_ORIGINS).


Le Chat (Mistral) client config
{
  "mcpServers": {
    "social-snapshot": {
      "url": "https://social-snapshot.<alpic-domain>/mcp",
      "headers": { "Authorization": "Bearer <SERVER_TOKEN>" }
    }
  }
}


3) Tools Exposed by the Central Server (HTTP MCP)
All tools are under the social.*, apollo.*, and vision.* namespaces. Inputs/outputs are JSON validated with Zod schema.
Key change: LinkedIn and Apollo are called in parallel, and the server returns two separate context resources (one per provider) plus an optional combined context. These contexts can be fed directly into Le Chat as grounding.
3.1 social.fetch_contexts — NEW (Parallel LI + Apollo)
Build two profile contexts in parallel: one from LinkedIn MCP (visible profile/recents) and one from Apollo MCP (public org/title/domain signals). No contact discovery. Posts are optional and handled by social.fetch_posts.
Input schema
{
  "type": "object",
  "properties": {
    "first_name": { "type": "string" },
    "last_name": { "type": "string" },
    "linkedin_url": { "type": "string" },
    "organization_name": { "type": "string" },
    "domain": { "type": "string" },
    "apollo_limit": { "type": "integer", "minimum": 1, "maximum": 3, "default": 1 },
    "include_recent_posts_summary": { "type": "boolean", "default": true }
  },
  "required": ["first_name", "last_name"]
}

Behavior
Run in parallel:


LinkedIn MCP get_person_profile using linkedin_url if provided (otherwise best‑effort name match if supported). Extract headline/about and, if include_recent_posts_summary=true, a short recents summary (topics only; no deep CV scraping).


Apollo MCP people_search constrained by organization_name/domain where provided; take top apollo_limit (default 1) and synthesize a public‑signals context (name, org, domain, title, industry—no contact details).


Emit two Markdown context resources:


resource://contexts/linkedin/<id>.md


resource://contexts/apollo/<id>.md


Also emit an optional combined resource resource://contexts/combined/<id>.md (clearly labeled sections: “From LinkedIn”, “From Apollo”).


Output
{
  "linkedin_context": "resource://contexts/linkedin/<id>.md",
  "apollo_context": "resource://contexts/apollo/<id>.md",
  "combined_context": "resource://contexts/combined/<id>.md",
  "apollo_candidates": [
    {
      "candidate_id": "<uuid>",
      "full_name": "Jane Doe",
      "organization_name": "Acme Inc",
      "domain": "acme.com",
      "linkedin_url": "https://www.linkedin.com/in/jane-doe/",
      "confidence": 0.87
    }
  ],
  "warnings": []
}

Guardrails in each context
Header line: “This context is derived from LinkedIn/Apollo. Use only facts present here; do not infer private data. Employment history beyond top‑level public info is out of scope for Step‑1+.”



3.2 apollo.search_candidates
Find up to N Apollo candidates for the person; returns normalized candidates. (Can be used standalone if needed.)
Input schema — same as before; default limit=2.
Output — normalized candidates[] with confidence.

3.3 social.resolve_target
Select top two candidates for downstream fetches (unchanged). Useful if apollo_limit > 1.

3.4 social.fetch_posts (optional)
Fetch recent X/LinkedIn posts per candidate (unchanged). Use this if you want a posts‑only grounding in addition to the LI/Apollo profile contexts.

3.5 social.build_posts_context (optional)
Create combined/per‑candidate posts digests (unchanged). Can be used alongside the two provider contexts returned by social.fetch_contexts.

3.6 social.suggest_openers
Produce 3 openers grounded in any combination of:
the LinkedIn context,


the Apollo context, and


optional posts summaries (if provided).


Input schema
{
  "type": "object",
  "properties": {
    "linkedin_context_resource": { "type": "string" },
    "apollo_context_resource": { "type": "string" },
    "posts_combined_summary": { "type": "string" },
    "tone_options": {
      "type": "array",
      "items": { "type": "string" },
      "default": ["casual", "professional", "playful"]
    }
  },
  "required": ["linkedin_context_resource", "apollo_context_resource"]
}

Output
{
  "openers": [
    { "tone": "casual", "text": "…", "why": "…" },
    { "tone": "professional", "text": "…", "why": "…" },
    { "tone": "playful", "text": "…", "why": "…" }
  ],
  "warnings": []
}

Grounding rule
If a claim is not present in either the LinkedIn or Apollo contexts (or posts summary if provided), the model must say it doesn’t know.



3.7 vision.face_match_placeholder (disabled stub)
Unchanged: returns gating guidance; performs no recognition.

4) Data Models & Resources
type CandidateProfile = {
  candidate_id: string;   // UUID per session
  full_name: string;
  organization_name?: string;
  domain?: string;
  linkedin_url?: string;
  x_handle?: string;      // without '@'
  confidence: number;     // 0..1
  source: 'apollo' | 'manual';
};

type Post = {
  id: string;
  platform: 'linkedin' | 'x';
  author: string;
  text: string;           // URLs stripped where possible
  created_at: string;     // ISO8601
  urls?: string[];
  metrics?: { likes?: number; replies?: number; reposts?: number; views?: number };
  candidate_id?: string;
};

Resource storage
Posts per candidate: resource://posts/<candidate_id>/x.jsonl and .../linkedin.jsonl


Contexts: resource://contexts/combined/<id>.md and resource://contexts/<candidate_id>.md


HTTP resource serving
Implement MCP resource read endpoint so Le Chat can fetch resources by URI.


Backed by in‑memory cache + optional disk/S3 storage (env‑configurable).



5) Provider Adapters
Apify (Tweet Scraper V2)
Prefer direct Apify REST actor run from server with APIFY_TOKEN (sync get dataset items).


Inputs: handles, tweetsDesired, since, until?, includeReplies, includeRetweets.


Cost estimate: $0.40/1000 * tweetsDesired (plan‑dependent).


Normalize to Post[] (strip tracking URLs, coerce timestamps to ISO).


LinkedIn MCP
Run LinkedIn MCP as a co‑deployed service (sidecar) reachable via stdio bridge or HTTP gateway.


Auth: LINKEDIN_COOKIE (li_at=...) passed via env.


Tool: get_person_profile → extract recent activity/posts only.


Apollo.io MCP
Co‑deployed service reachable via stdio bridge or HTTP; auth APOLLO_IO_API_KEY.


Use people_search (constrained by org/domain) and map to CandidateProfile.



6) AuthN/Z, Rate Limits, and Compliance
Inbound: Authorization: Bearer <SERVER_TOKEN> (env SERVER_TOKEN).


Outbound: APIFY_TOKEN, LINKEDIN_COOKIE, APOLLO_IO_API_KEY.


Rate limits (env‑configurable): per‑IP and per‑tool (default 60 req/min; burst 120).


PII/ToS: No contact discovery; do not persist PII beyond TTL. Show LinkedIn ToS warning on first LinkedIn call per session.



7) Observability & Errors
Logs: pino JSON logs with req_id, user_id?, tool, latency_ms, cost_estimate.


Metrics: Prometheus at /metrics (tool call count, error rates, Apify tweet count, TTL cache hits).


Error model: Structured errors with code, message, details:


cookieExpired, apifyRunError, apolloAuthError, insufficientData, rateLimited, invalidInput.


Partial results: Always return available resources plus warnings[].



8) Configuration & Environment
PORT=8080
SERVER_TOKEN=change-me
ALLOWED_ORIGINS=https://chat.mistral.ai
CACHE_TTL_HOURS=24
MAX_TWEETS_DEFAULT=50
APIFY_TOKEN=
LINKEDIN_COOKIE=li_at=...
APOLLO_IO_API_KEY=
STORAGE_BACKEND=memory   # memory | disk | s3
DISK_PATH=/var/lib/social-snapshot
S3_BUCKET=...
S3_REGION=...
S3_PREFIX=snapshots/


9) Build & Runtime (Node/TS) - Future Implementation
Language: TypeScript (Node 20+).


Core libs: @modelcontextprotocol/sdk (HTTP server), zod, axios/undici, pino, dayjs, uuid, optional ioredis (cache).

Note: Current implementation uses Python with separate MCP servers.


Structure


/src
  server.ts                 # HTTP MCP bootstrap
  httpAuth.ts               # bearer auth, CORS
  tools/
    apollo.search.ts        # search_candidates
    social.resolve.ts       # resolve_target
    social.fetch.ts         # fetch_posts
    social.context.ts       # build_posts_context
    social.openers.ts       # suggest_openers
    vision.frPlaceholder.ts # face_match_placeholder
  adapters/
    apify.ts                # Apify actor REST client
    linkedinMcp.ts          # bridge client to LinkedIn MCP
    apolloMcp.ts            # bridge client to Apollo MCP
  models/
    post.ts
    candidate.ts
  resources/
    store.ts                # memory/disk/S3 resource backends
  utils/
    normalize.ts            # post normalization, URL strip
    overlaps.ts             # overlap scoring
    cost.ts                 # Apify cost estimate


10) Deployment on Alpic
Containerize: Multi‑stage Docker (Node 20‑alpine).


Ingress: Alpic HTTP ingress with TLS; map /mcp to app PORT.


Secrets: APIFY_TOKEN, LINKEDIN_COOKIE, APOLLO_IO_API_KEY, SERVER_TOKEN via Alpic secrets manager.


Scaling: HPA based on CPU (70%) and p95 latency; sticky sessions not required.


Probes: /healthz (liveness), /readyz (readiness), /metrics (optional).


Reverse proxy (if needed): NGINX with client_max_body_size 2m, keepalive_timeout 65, proxy_read_timeout 90.


Dockerfile (outline)
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm i --frozen-lockfile

FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
EXPOSE 8080
CMD ["node","dist/server.js"]


11) Orchestration Flow (Le Chat)
Primary flow (two contexts, parallel):
User provides: first_name, last_name, optional linkedin_url, plus optional organization_name/domain.


Call social.fetch_contexts → returns linkedin_context, apollo_context, and combined_context.


Call social.suggest_openers with the two context resources (and optionally a posts summary from step 5 below).


Present 3 openers with rationale. Offer to save contexts (TTL 24h by default).


Optional posts enrichment:
 5) If the user also wants recents from X/LI, run social.fetch_posts (per‑candidate), then social.build_posts_context, and pass posts_combined_summary into social.suggest_openers to refine suggestions.
FR placeholder:
 6) If asked about face matching, call vision.face_match_placeholder and present the gating note.

12) Test Cases (Acceptance)
Happy path: Two candidates; ≥20 combined posts; combined context ≤300 words; 3 distinct openers with rationales.


Private/empty feeds: insufficientData with suggestion to try other handle or enable Apollo verification.


Expired LinkedIn cookie: cookieExpired error with remediation note.


Apify failure: apifyRunError + partial results where possible.


Rate limit: returns rateLimited with retry_after_ms.



13) Security & Privacy Checklist
Inbound bearer auth required; rotate SERVER_TOKEN periodically.


Never store Apollo or LinkedIn responses beyond TTL unless user explicitly saves.


No contact data exposure; no FR.


Log redaction for tokens and cookies.



End of HTTP Spec — For Future Implementation

---

## Current Python Implementation Details

### Project Structure
```
coldopen-coach/
├── mcp_servers/
│   ├── mcp_x/
│   │   └── server.py          # Twitter/X MCP server
│   ├── mcp_linkedin/
│   │   └── server.py          # LinkedIn MCP server
│   └── mcp_approach_coach/
│       └── server.py          # Coaching MCP server
├── shared/
│   ├── models.py              # Normalized data models
│   └── theme_inference.py     # Theme analysis
├── demo/
│   └── fetch_data.py          # Demo scripts
└── requirements.txt           # Python dependencies
```

### Current MCP Tools Available

#### mcp_x server (Twitter/X)
- `fetch_recent_posts` - Get recent posts from X/Twitter user
- `search_posts` - Search posts by keywords/hashtags

#### mcp_linkedin server (LinkedIn)
- `get_person_profile` - Get LinkedIn profile information
- `get_recent_activity` - Fetch recent LinkedIn activity

#### mcp_approach_coach server (Coaching)
- `analyze_social_context` - Analyze posts for conversation starters
- `generate_openers` - Create personalized outreach messages
- `suggest_themes` - Identify common themes and interests

### Environment Configuration
```env
APIFY_TOKEN=your_apify_token_here
LINKEDIN_COOKIE=li_at=your_linkedin_cookie_here  # Optional
DEBUG=true
```

### Running Current Implementation
```bash
# Install dependencies
uv sync

# Run individual servers
uv run python -m mcp_servers.mcp_x.server
uv run python -m mcp_servers.mcp_linkedin.server
uv run python -m mcp_servers.mcp_approach_coach.server
```

### MCP Client Configuration (Claude Desktop)
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

