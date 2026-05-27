from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from agentbridge.api.auth import get_current_user, get_optional_user, router as auth_router
from agentbridge.api.billing import router as billing_router
from agentbridge.api.mcp import router as mcp_router, set_active_project
from agentbridge.api.routes import router as api_router
from agentbridge.api.seed import seed_demo
from agentbridge.api.teams import router as teams_router
from agentbridge.config import ensure_dirs, settings
from agentbridge.db import TIER_LIMITS, db, store
from agentbridge.models.user import SubscriptionTier, UsageRecord, User


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_dirs()
    await db.init_db()
    await seed_demo()
    projects = store.list_projects()
    if projects:
        set_active_project(projects[0].id)
    yield


app = FastAPI(
    title="agentbridge API",
    description="Turn any API artifact into an MCP server — with monetization, auth, and team features",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mcp_router)
app.include_router(api_router)
app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(teams_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.2.0"}


@app.get("/api/usage")
async def get_usage(
    days: int = Query(default=7, ge=1, le=365),
    user: User = Depends(get_current_user),
):
    daily = await db.get_usage_by_day(user.id, days)
    return daily


@app.get("/api/usage/count")
async def get_usage_count(
    user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total = await db.get_usage_count(user.id, month_start, now)
    limits = TIER_LIMITS.get(user.tier, TIER_LIMITS[SubscriptionTier.free])
    max_limit = limits.get("endpoints", 3)
    endpoint_limit = max_limit * 100
    remaining = max(0, endpoint_limit - total)
    return {"total": total, "limit": endpoint_limit, "remaining": remaining}


@app.post("/api/usage/record")
async def record_usage(
    tool_name: str = Query(default=""),
    project_id: str = Query(default=None),
    endpoint_id: str = Query(default=None),
    user: User | None = Depends(get_optional_user),
):
    record = UsageRecord(
        user_id=user.id if user else "anonymous",
        project_id=project_id,
        endpoint_id=endpoint_id,
        tool_name=tool_name,
        timestamp=datetime.utcnow(),
    )
    await db.record_usage(record)
    return {"recorded": True}


# ── LLMs.txt — Machine-readable AI agent discovery ──────────────


@app.get("/llms.txt", response_model=None)
@app.get("/llms.txt", include_in_schema=False)
async def llms_txt():
    """llms.txt standard endpoint — AI agents use this to discover AgentBridge capabilities."""
    base_url = settings.host if hasattr(settings, 'host') else "https://agentbridge-demo.onrender.com"

    lines = ["# agentbridge — Bridge any API to AI agents"]
    lines.append(f"# Base URL: {base_url}")
    lines.append("")

    # ── Connection ──
    lines.append("## Connect")
    lines.append(f"- MCP Endpoint: {base_url}/mcp/")
    lines.append(f"- OpenAPI Spec: {base_url}/openapi.json")
    lines.append("")

    # ── REST API ──
    lines.append("## REST API")
    lines.append("")
    lines.append("### Auth")
    lines.append(f"- POST {base_url}/api/auth/register | Register new account")
    lines.append(f"- POST {base_url}/api/auth/login | Login, returns JWT token")
    lines.append(f"- GET {base_url}/api/auth/me | Current user info")
    lines.append(f"- POST {base_url}/api/auth/api-keys | Generate API key")
    lines.append(f"- DELETE {base_url}/api/auth/api-keys | Revoke API key")
    lines.append("")
    lines.append("### Billing")
    lines.append(f"- GET {base_url}/api/billing/subscription | Current subscription")
    lines.append(f"- GET {base_url}/api/billing/tiers | All pricing tiers")
    lines.append(f"- POST {base_url}/api/billing/upgrade | Upgrade to Pro ($29/mo) or Enterprise ($99/mo)")
    lines.append(f"- POST {base_url}/api/billing/cancel | Cancel subscription")
    lines.append(f"- POST {base_url}/api/billing/reactivate | Reactivate subscription")
    lines.append(f"- POST {base_url}/api/billing/checkout | Stripe checkout session")
    lines.append("")
    lines.append("### Projects & Artifacts")
    lines.append(f"- POST {base_url}/api/artifacts | Ingest API artifact (OpenAPI, gRPC, GraphQL, WSDL, Postman, DB Schema, Docs)")
    lines.append(f"- GET {base_url}/api/projects | List projects")
    lines.append(f"- POST {base_url}/api/projects | Create project")
    lines.append(f"- GET {base_url}/api/projects/{{id}} | Get project details")
    lines.append(f"- PATCH {base_url}/api/projects/{{id}} | Update project")
    lines.append(f"- GET {base_url}/api/artifacts | List artifacts")
    lines.append(f"- GET {base_url}/api/endpoints | List all generated endpoints")
    lines.append(f"- GET {base_url}/api/endpoints/by-project/{{id}} | Endpoints per project")
    lines.append(f"- GET {base_url}/api/status | Server status")
    lines.append("")
    lines.append("### Teams")
    lines.append(f"- GET {base_url}/api/teams | List user's teams")
    lines.append(f"- POST {base_url}/api/teams | Create team")
    lines.append(f"- GET {base_url}/api/teams/{{id}} | Team details")
    lines.append(f"- POST {base_url}/api/teams/{{id}}/members | Add member")
    lines.append(f"- DELETE {base_url}/api/teams/{{id}}/members/{{mid}} | Remove member")
    lines.append(f"- DELETE {base_url}/api/teams/{{id}} | Delete team")
    lines.append("")
    lines.append("### Usage & Analytics")
    lines.append(f"- GET {base_url}/api/usage | Usage history (7d default)")
    lines.append(f"- GET {base_url}/api/usage/count | Current month count vs tier limit")
    lines.append(f"- POST {base_url}/api/usage/record | Record tool usage event")
    lines.append("")

    # ── MCP Protocol ──
    lines.append("## MCP Protocol")
    lines.append("AgentBridge exposes MCP-compatible tools and prompts for each project.")
    lines.append("Connect any MCP client to the endpoint above.")
    lines.append("")
    lines.append("### Supported Artifact Types (8)")
    lines.append("- OpenAPI (.yaml, .json) → REST tools")
    lines.append("- Spring MVC (.java) → Controller endpoints")
    lines.append("- gRPC (.proto) → RPC tools")
    lines.append("- WSDL (.wsdl) → SOAP operations")
    lines.append("- GraphQL (.graphql) → Query/mutation tools")
    lines.append("- Postman (.json) → Collection tools")
    lines.append("- DB Schema (.sql, .prisma) → Table query tools")
    lines.append("- Docs (.md) → Endpoint extraction")
    lines.append("")

    # ── Pricing Tiers ──
    lines.append("## Pricing")
    lines.append("| Tier | Endpoints | Teams | Private MCP | Custom Branding | SSO | Price |")
    lines.append("| Free | 3 | 1 | - | - | - | $0/mo |")
    lines.append("| Pro | 50 | 5 | Yes | Yes | - | $29/mo |")
    lines.append("| Enterprise | Unlimited | Unlimited | Yes | Yes | Yes | $99/mo |")
    lines.append("")

    # ── Live projects ──
    lines.append("## Live Projects")
    projects = store.list_projects()
    if projects:
        for proj in projects[:20]:
            endpoints = store.get_endpoints_by_project(proj.id)
            lines.append(f"- **{proj.name}** ({len(endpoints)} endpoints) | MCP: {base_url}/mcp/")
            for ep in endpoints[:5]:
                lines.append(f"  - `{ep.method} {ep.path}` — {ep.description or 'no description'}")
            if len(endpoints) > 5:
                lines.append(f"  - ... and {len(endpoints) - 5} more")
        lines.append("")
    else:
        lines.append("No projects yet. Create one at https://agentbridge-one.vercel.app")
        lines.append("")

    # ── For AI Agents ──
    lines.append("## For AI Agents")
    lines.append("This file follows the llms.txt standard (https://llmstxt.org).")
    lines.append("Connect to the MCP endpoint to get live tool definitions:")
    lines.append("```json")
    lines.append('{"mcpServers": {"agentbridge": {"url": "' + base_url + '/mcp/"}}}')
    lines.append("```")

    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("\n".join(lines), media_type="text/plain; charset=utf-8")


@app.get("/projects/{project_id}/llms.txt", include_in_schema=False)
async def project_llms_txt(project_id: str):
    """Generate llms.txt from ingested specs for a specific project."""
    from agentbridge.generators.llms_txt import generate_llms_txt

    proj = store.get_project_by_id(project_id)
    if not proj:
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse("# Project not found\n", media_type="text/plain; charset=utf-8", status_code=404)

    endpoints = store.get_endpoints_by_project(project_id)
    mcp_url = settings.host if hasattr(settings, 'host') else "https://agentbridge-demo.onrender.com"
    text = generate_llms_txt(proj, endpoints, base_url=mcp_url)

    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(text, media_type="text/plain; charset=utf-8")
