# agentbridge — Turn any API artifact into an MCP server

Turn any API spec, database schema, or developer artifact into AI-agent-ready **MCP tools and resources** — with zero MCP expertise required.

## Demo (Live)

| Service | URL |
|---------|-----|
| **Dashboard** | https://frontend-pied-six-99.vercel.app |
| **MCP Endpoint** | https://agentbridge-demo.onrender.com/mcp/ |
| **API Health** | https://agentbridge-demo.onrender.com/health |

The demo is pre-seeded with a "Demo Store API" project using [FakeStoreAPI](https://fakestoreapi.com/).
Connect any MCP-compatible agent to `https://agentbridge-demo.onrender.com/mcp/` and get 5 tools instantly.

## Quick Start

```bash
uv run agentbridge init                    # Initialize project
uv run agentbridge add ./openapi.yaml      # Add an OpenAPI spec
uv run agentbridge add ./schema.sql        # Add a DB schema
uv run agentbridge serve                   # Start the MCP server
uv run agentbridge dashboard               # Open the web UI
```

## Architecture

```
agentbridge/
├── src/agentbridge/
│   ├── cli/              # Typer + Rich CLI interface
│   ├── api/              # FastAPI backend + MCP protocol
│   ├── ingestors/        # OpenAPI, Postman, GraphQL, DB schema parsers
│   ├── generators/       # MCP tool code generators + HTTP client
│   └── models/           # Pydantic models
├── frontend/             # React + Vite + TypeScript dashboard
├── templates/            # Demo specs + Spanish docs
├── Dockerfile            # Production container
├── render.yaml           # Render deployment
└── vercel.json           # Vercel deployment
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| CLI | `typer` + `rich` | Project management and interaction |
| Backend API | `fastapi` + `uvicorn` | Management API + MCP protocol server |
| MCP SDK | `mcp[cli]` | MCP protocol tool definitions |
| Parsing | `pyyaml`, `sqlglot` | Artifact ingestion |
| HTTP | `httpx` | Generated tool HTTP calls |
| Frontend | React 18 + TypeScript + Vite | Management dashboard |
| Styling | Tailwind v4 | Responsive design |
| Persistence | JSON file store (`~/.agentbridge/`) | Zero-config storage |
| Deployment | Docker + Render + Vercel | Free tier hosting |

## Key Design Principles

1. **Multiple artifact types:** OpenAPI/Swagger, Postman collections, GraphQL schemas, DB schemas (SQL, Prisma), plain documentation
2. **Self-hosted or SaaS:** Deploy via Docker or use the hosted version
3. **No MCP knowledge required:** Upload artifacts through CLI or web dashboard, get an MCP endpoint URL back
4. **Per-tool auth:** Each generated MCP tool can carry API keys, OAuth tokens, or basic auth for the upstream API
5. **i18n: English + Spanish** — targeting LatAm small businesses too

## MCP Protocol

The generated MCP server exposes:
- **Tools:** Each API endpoint becomes an MCP tool with typed parameters
- **Resources:** API schemas/models become MCP resources for agent context

Example: A small invoicing API with `GET /invoices` and `POST /invoices` becomes:
```
tools:
  - list_invoices(filters, page, per_page) -> list
  - create_invoice(customer_id, items, due_date) -> invoice
```

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

## Deployment

### Local development
```bash
uv pip install -e ".[dev]"
agentbridge dashboard  # Opens FastAPI + frontend
```

### Production
- **Frontend:** `cd frontend && vercel --prod`
- **API:** Deployed via Docker on Render (auto-deploy from GitHub)
