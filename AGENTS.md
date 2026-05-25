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
