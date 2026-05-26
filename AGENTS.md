# agentbridge — Bridge any API to AI agents

Turn any API artifact into AI-agent-ready **MCP tools + prompts** — zero MCP expertise required.

## Demo (Live)

| Service | URL |
|---------|-----|
| **Dashboard** | https://agentbridge-one.vercel.app |
| **MCP Endpoint** | https://agentbridge-demo.onrender.com/mcp/ |
| **API Health** | https://agentbridge-demo.onrender.com/health |
| **GitHub** | https://github.com/maugomez77/agentbridge |

Connect any MCP agent to `https://agentbridge-demo.onrender.com/mcp/` for 5 tools + 5 prompts instantly.

## Quick Start

```bash
agentbridge init                     # Create project
agentbridge add ./openapi.yaml       # Ingest OpenAPI spec
agentbridge add ./controller.java    # Ingest Spring MVC controller
agentbridge serve                    # Start MCP server
agentbridge dashboard                # Open web UI
```

## Monetization Tiers

| Feature | Free | Pro ($29/mo) | Enterprise ($99/mo) |
|---------|------|-------------|-------------------|
| Endpoints | 3 | 50 | Unlimited |
| Teams | 1 | 5 | Unlimited |
| MCP Endpoints | Public only | Private | Private |
| Custom Branding | No | Yes | Yes |
| SSO / SAML | No | No | Yes |
| Audit Logs | No | No | Yes |
| Priority Support | No | No | Yes |

## Authentication

- **JWT** — Bearer tokens via `/api/auth/login` and `/api/auth/register`
- **API Keys** — Programmatic access via `X-API-Key` header (`/api/auth/api-keys`)
- **Neon PostgreSQL** — Persistent user, team, subscription, and usage data (file-based fallback when no DATABASE_URL)

## Deployment

- **Frontend** — Vercel (`frontend/` via `vercel.json`)
- **Backend** — Render Docker (`src/agentbridge/api/main.py:app`)
- **Database** — Neon PostgreSQL (pass `DATABASE_URL` env var; defaults to JSON files)

## Supported Artifacts (8 types)

| Type | Files | Extracts |
|------|-------|----------|
| OpenAPI | `.yaml` `.json` | REST endpoints, params |
| Spring MVC | `.java` | `@RestController`, `@GetMapping`, params |
| gRPC | `.proto` | Services, RPCs, messages |
| WSDL | `.wsdl` | SOAP operations |
| GraphQL | `.graphql` | Queries, mutations |
| Postman | `.json` | Collections |
| DB Schema | `.sql` `.prisma` | Tables, models |
| Docs | `.md` | Endpoint docs |

## MCP Protocol

Each project exposes:
- **Tools** — each API endpoint becomes a typed MCP tool
- **Prompts** — workflow guides teaching agents how to use the API
- **Resources** — per-endpoint reference docs

## Connect From Any Agent

```json
{
  "mcpServers": {
    "agentbridge": {
      "url": "https://agentbridge-demo.onrender.com/mcp/"
    }
  }
}
```

## API Endpoints

### Auth
- `POST /api/auth/register` — Create account
- `POST /api/auth/login` — Get JWT token
- `GET /api/auth/me` — Get current user
- `POST /api/auth/api-keys` — Generate API key
- `DELETE /api/auth/api-keys` — Revoke API key

### Billing
- `GET /api/billing/subscription` — Get current subscription
- `GET /api/billing/tiers` — List all tiers
- `POST /api/billing/upgrade` — Upgrade tier
- `POST /api/billing/downgrade` — Downgrade to free
- `POST /api/billing/cancel` — Cancel subscription

### Projects & Artifacts
- `GET/POST /api/projects` — Project CRUD
- `POST /api/artifacts` — Ingest API spec
- `GET /api/endpoints/by-project/:id` — Get MCP tools
- `GET /api/status` — Overall stats
