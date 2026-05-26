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
