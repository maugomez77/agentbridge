from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from agentbridge.config import settings
from agentbridge.models.artifact import Artifact, ArtifactStatus, ArtifactType
from agentbridge.models.endpoint import Endpoint, HttpMethod, Parameter
from agentbridge.models.project import Project
from agentbridge.models.user import SubscriptionTier, Team, UsageRecord, User, Subscription


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    api_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tier: Mapped[str] = mapped_column(String(32), default="free")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def to_model(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            display_name=self.display_name,
            api_key=self.api_key,
            tier=SubscriptionTier(self.tier),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class TeamRow(Base):
    __tablename__ = "teams"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), nullable=False)
    member_ids: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def to_model(self) -> Team:
        return Team(
            id=self.id,
            name=self.name,
            owner_id=self.owner_id,
            member_ids=json.loads(self.member_ids or "[]"),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class SubscriptionRow(Base):
    __tablename__ = "subscriptions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), nullable=False)
    tier: Mapped[str] = mapped_column(String(32), default="free")
    stripe_customer_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def to_model(self) -> Subscription:
        return Subscription(
            id=self.id,
            user_id=self.user_id,
            tier=SubscriptionTier(self.tier),
            stripe_customer_id=self.stripe_customer_id,
            stripe_subscription_id=self.stripe_subscription_id,
            current_period_start=self.current_period_start,
            current_period_end=self.current_period_end,
            cancel_at_period_end=self.cancel_at_period_end,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class UsageRow(Base):
    __tablename__ = "usage"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), nullable=False)
    project_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    endpoint_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tool_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def to_model(self) -> UsageRecord:
        return UsageRecord(
            id=self.id,
            user_id=self.user_id,
            project_id=self.project_id,
            endpoint_id=self.endpoint_id,
            tool_name=self.tool_name,
            timestamp=self.timestamp,
        )


TIER_LIMITS = {
    SubscriptionTier.free: {"endpoints": 3, "teams": 1, "private_mcp": False, "branding": False, "sso": False, "audit": False, "priority": False},
    SubscriptionTier.pro: {"endpoints": 50, "teams": 5, "private_mcp": True, "branding": True, "sso": False, "audit": False, "priority": False},
    SubscriptionTier.enterprise: {"endpoints": 999_999, "teams": 999_999, "private_mcp": True, "branding": True, "sso": True, "audit": True, "priority": True},
}


class DBPool:
    def __init__(self):
        database_url = os.getenv("DATABASE_URL", "").strip()
        self._async_engine = None
        self._async_sessionmaker = None
        self._sync_engine = None
        self._sync_sessionmaker = None
        self._file_store: FileStore | None = None

        if database_url and database_url.startswith("postgres"):
            async_url = database_url
            if async_url.startswith("postgresql://"):
                async_url = async_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif async_url.startswith("postgres://"):
                async_url = async_url.replace("postgres://", "postgresql+asyncpg://", 1)
            self._async_engine = create_async_engine(async_url, echo=False)
            self._async_sessionmaker = async_sessionmaker(self._async_engine, class_=AsyncSession, expire_on_commit=False)

            sync_url = database_url
            if sync_url.startswith("postgresql+asyncpg://"):
                sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
            self._sync_engine = create_engine(sync_url, echo=False)
            self._sync_sessionmaker = sessionmaker(self._sync_engine, class_=Session, expire_on_commit=False)
        else:
            self._file_store = FileStore()

    async def init_db(self):
        if self._async_engine:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        else:
            self._file_store._load()

    def _use_db(self) -> bool:
        return self._async_engine is not None

    async def create_user(self, user: User) -> User:
        if self._use_db():
            row = UserRow(
                id=user.id,
                email=user.email,
                hashed_password=user.hashed_password,
                display_name=user.display_name,
                api_key=user.api_key,
                tier=user.tier.value,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            async with self._async_sessionmaker() as sess:
                sess.add(row)
                await sess.commit()
            return user
        return self._file_store.create_user(user)

    async def get_user_by_email(self, email: str) -> User | None:
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                result = await sess.execute(select(UserRow).where(UserRow.email == email))
                row = result.scalar_one_or_none()
                return row.to_model() if row else None
        return self._file_store.get_user_by_email(email)

    async def get_user_by_id(self, user_id: str) -> User | None:
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                result = await sess.execute(select(UserRow).where(UserRow.id == user_id))
                row = result.scalar_one_or_none()
                return row.to_model() if row else None
        return self._file_store.get_user_by_id(user_id)

    async def get_user_by_api_key(self, api_key: str) -> User | None:
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                result = await sess.execute(select(UserRow).where(UserRow.api_key == api_key))
                row = result.scalar_one_or_none()
                return row.to_model() if row else None
        return self._file_store.get_user_by_api_key(api_key)

    async def update_user(self, user: User):
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                result = await sess.execute(select(UserRow).where(UserRow.id == user.id))
                row = result.scalar_one_or_none()
                if row:
                    row.email = user.email
                    row.hashed_password = user.hashed_password
                    row.display_name = user.display_name
                    row.api_key = user.api_key
                    row.tier = user.tier.value
                    row.updated_at = datetime.now()
                    await sess.commit()
            return
        self._file_store.update_user(user)

    async def create_team(self, team: Team) -> Team:
        if self._use_db():
            row = TeamRow(
                id=team.id, name=team.name, owner_id=team.owner_id,
                member_ids=json.dumps(team.member_ids),
                created_at=team.created_at, updated_at=team.updated_at,
            )
            async with self._async_sessionmaker() as sess:
                sess.add(row)
                await sess.commit()
            return team
        return self._file_store.create_team(team)

    async def get_team(self, team_id: str) -> Team | None:
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                result = await sess.execute(select(TeamRow).where(TeamRow.id == team_id))
                row = result.scalar_one_or_none()
                return row.to_model() if row else None
        return self._file_store.get_team(team_id)

    async def list_user_teams(self, user_id: str) -> list[Team]:
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                result = await sess.execute(
                    select(TeamRow).where(
                        (TeamRow.owner_id == user_id) | (TeamRow.member_ids.contains(user_id))
                    )
                )
                return [r.to_model() for r in result.scalars().all()]
        return self._file_store.list_user_teams(user_id)

    async def update_team(self, team: Team):
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                result = await sess.execute(select(TeamRow).where(TeamRow.id == team.id))
                row = result.scalar_one_or_none()
                if row:
                    row.name = team.name
                    row.member_ids = json.dumps(team.member_ids)
                    row.updated_at = datetime.now()
                    await sess.commit()
            return
        self._file_store.update_team(team)

    async def delete_team(self, team_id: str):
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                result = await sess.execute(select(TeamRow).where(TeamRow.id == team_id))
                row = result.scalar_one_or_none()
                if row:
                    await sess.delete(row)
                    await sess.commit()
            return
        self._file_store.delete_team(team_id)

    async def create_subscription(self, sub: Subscription) -> Subscription:
        if self._use_db():
            row = SubscriptionRow(
                id=sub.id, user_id=sub.user_id, tier=sub.tier.value,
                stripe_customer_id=sub.stripe_customer_id,
                stripe_subscription_id=sub.stripe_subscription_id,
                current_period_start=sub.current_period_start,
                current_period_end=sub.current_period_end,
                cancel_at_period_end=sub.cancel_at_period_end,
                created_at=sub.created_at, updated_at=sub.updated_at,
            )
            async with self._async_sessionmaker() as sess:
                sess.add(row)
                await sess.commit()
            return sub
        return self._file_store.create_subscription(sub)

    async def get_subscription(self, user_id: str) -> Subscription | None:
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                result = await sess.execute(
                    select(SubscriptionRow).where(SubscriptionRow.user_id == user_id)
                )
                row = result.scalar_one_or_none()
                return row.to_model() if row else None
        return self._file_store.get_subscription(user_id)

    async def update_subscription(self, sub: Subscription):
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                result = await sess.execute(select(SubscriptionRow).where(SubscriptionRow.id == sub.id))
                row = result.scalar_one_or_none()
                if row:
                    row.tier = sub.tier.value
                    row.stripe_customer_id = sub.stripe_customer_id
                    row.stripe_subscription_id = sub.stripe_subscription_id
                    row.current_period_start = sub.current_period_start
                    row.current_period_end = sub.current_period_end
                    row.cancel_at_period_end = sub.cancel_at_period_end
                    row.updated_at = datetime.now()
                    await sess.commit()
            return
        self._file_store.update_subscription(sub)

    async def record_usage(self, record: UsageRecord):
        if self._use_db():
            row = UsageRow(
                id=record.id, user_id=record.user_id,
                project_id=record.project_id, endpoint_id=record.endpoint_id,
                tool_name=record.tool_name, timestamp=record.timestamp,
            )
            async with self._async_sessionmaker() as sess:
                sess.add(row)
                await sess.commit()
            return
        self._file_store.record_usage(record)

    async def get_usage_count(
        self, user_id: str, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> int:
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                stmt = select(UsageRow).where(UsageRow.user_id == user_id)
                if start_date:
                    stmt = stmt.where(UsageRow.timestamp >= start_date)
                if end_date:
                    stmt = stmt.where(UsageRow.timestamp <= end_date)
                result = await sess.execute(stmt)
                rows = result.scalars().all()
                return len(rows)
        return self._file_store.get_usage_count(user_id, start_date, end_date)

    async def get_usage_by_day(self, user_id: str, days: int = 30) -> list[dict]:
        if self._use_db():
            async with self._async_sessionmaker() as sess:
                result = await sess.execute(
                    select(UsageRow).where(UsageRow.user_id == user_id)
                )
                rows = result.scalars().all()
                daily: dict[str, int] = {}
                for r in rows:
                    day = r.timestamp.strftime("%Y-%m-%d")
                    daily[day] = daily.get(day, 0) + 1
                return [{"date": k, "count": v} for k, v in sorted(daily.items())[-days:]]
        return self._file_store.get_usage_by_day(user_id, days)


class FileStore:
    def __init__(self):
        self._projects_file = settings.data_dir / "projects.json"
        self._artifacts_file = settings.data_dir / "artifacts.json"
        self._endpoints_file = settings.data_dir / "endpoints.json"
        self._users_file = settings.data_dir / "users.json"
        self._teams_file = settings.data_dir / "teams.json"
        self._subscriptions_file = settings.data_dir / "subscriptions.json"
        self._usage_file = settings.data_dir / "usage.json"
        self._projects: list[Project] = []
        self._artifacts: list[Artifact] = []
        self._endpoints: list[Endpoint] = []
        self._users: list[User] = []
        self._teams: list[Team] = []
        self._subscriptions: list[Subscription] = []
        self._usage: list[UsageRecord] = []

    def _load(self):
        if self._projects_file.exists():
            self._projects = [Project(**p) for p in json.loads(self._projects_file.read_text())]
        if self._artifacts_file.exists():
            self._artifacts = [Artifact(**a) for a in json.loads(self._artifacts_file.read_text())]
        if self._endpoints_file.exists():
            self._endpoints = [Endpoint(**e) for e in json.loads(self._endpoints_file.read_text())]
        if self._users_file.exists():
            self._users = [User(**u) for u in json.loads(self._users_file.read_text())]
        if self._teams_file.exists():
            self._teams = [Team(**t) for t in json.loads(self._teams_file.read_text())]
        if self._subscriptions_file.exists():
            self._subscriptions = [Subscription(**s) for s in json.loads(self._subscriptions_file.read_text())]
        if self._usage_file.exists():
            self._usage = [UsageRecord(**r) for r in json.loads(self._usage_file.read_text())]

    def _save(self, items: list, filepath: Path):
        filepath.write_text(json.dumps([i.model_dump(mode="json") for i in items], indent=2, default=str))

    def create_user(self, user: User) -> User:
        self._users.append(user)
        self._save(self._users, self._users_file)
        return user

    def get_user_by_email(self, email: str) -> User | None:
        return next((u for u in self._users if u.email == email), None)

    def get_user_by_id(self, user_id: str) -> User | None:
        return next((u for u in self._users if u.id == user_id), None)

    def get_user_by_api_key(self, api_key: str) -> User | None:
        return next((u for u in self._users if u.api_key == api_key), None)

    def update_user(self, user: User):
        for i, u in enumerate(self._users):
            if u.id == user.id:
                user.updated_at = datetime.now()
                self._users[i] = user
                self._save(self._users, self._users_file)
                return

    def create_team(self, team: Team) -> Team:
        self._teams.append(team)
        self._save(self._teams, self._teams_file)
        return team

    def get_team(self, team_id: str) -> Team | None:
        return next((t for t in self._teams if t.id == team_id), None)

    def list_user_teams(self, user_id: str) -> list[Team]:
        return [t for t in self._teams if t.owner_id == user_id or user_id in t.member_ids]

    def update_team(self, team: Team):
        for i, t in enumerate(self._teams):
            if t.id == team.id:
                team.updated_at = datetime.now()
                self._teams[i] = team
                self._save(self._teams, self._teams_file)
                return

    def delete_team(self, team_id: str):
        self._teams = [t for t in self._teams if t.id != team_id]
        self._save(self._teams, self._teams_file)

    def create_subscription(self, sub: Subscription) -> Subscription:
        self._subscriptions.append(sub)
        self._save(self._subscriptions, self._subscriptions_file)
        return sub

    def get_subscription(self, user_id: str) -> Subscription | None:
        return next((s for s in self._subscriptions if s.user_id == user_id), None)

    def update_subscription(self, sub: Subscription):
        for i, s in enumerate(self._subscriptions):
            if s.id == sub.id:
                sub.updated_at = datetime.now()
                self._subscriptions[i] = sub
                self._save(self._subscriptions, self._subscriptions_file)
                return

    def record_usage(self, record: UsageRecord):
        self._usage.append(record)
        if len(self._usage) % 10 == 0:
            self._save(self._usage, self._usage_file)

    def get_usage_count(self, user_id: str, start_date: datetime | None = None, end_date: datetime | None = None) -> int:
        count = 0
        for r in self._usage:
            if r.user_id != user_id:
                continue
            if start_date and r.timestamp < start_date:
                continue
            if end_date and r.timestamp > end_date:
                continue
            count += 1
        return count

    def get_usage_by_day(self, user_id: str, days: int = 30) -> list[dict]:
        daily: dict[str, int] = {}
        for r in self._usage:
            if r.user_id != user_id:
                continue
            day = r.timestamp.strftime("%Y-%m-%d")
            daily[day] = daily.get(day, 0) + 1
        return [{"date": k, "count": v} for k, v in sorted(daily.items())[-days:]]

    def create_project(self, name: str, base_url: str | None = None) -> Project:
        project = Project(name=name, base_url=base_url)
        self._projects.append(project)
        self._save(self._projects, self._projects_file)
        return project

    def get_project(self, name: str) -> Project | None:
        return next((p for p in self._projects if p.name == name), None)

    def get_project_by_id(self, project_id: str) -> Project | None:
        return next((p for p in self._projects if p.id == project_id), None)

    def list_projects(self) -> list[Project]:
        return list(self._projects)

    def update_project(self, project: Project):
        for i, p in enumerate(self._projects):
            if p.id == project.id:
                project.updated_at = datetime.now()
                self._projects[i] = project
                self._save(self._projects, self._projects_file)
                return

    def create_artifact(self, artifact: Artifact) -> Artifact:
        self._artifacts.append(artifact)
        self._save(self._artifacts, self._artifacts_file)
        return artifact

    def get_artifact(self, artifact_id: str) -> Artifact | None:
        return next((a for a in self._artifacts if a.id == artifact_id), None)

    def list_artifacts(self, project_id: str | None = None) -> list[Artifact]:
        if project_id:
            return [a for a in self._artifacts if a.project_id == project_id]
        return list(self._artifacts)

    def update_artifact(self, artifact: Artifact):
        for i, a in enumerate(self._artifacts):
            if a.id == artifact.id:
                artifact.updated_at = datetime.now()
                self._artifacts[i] = artifact
                self._save(self._artifacts, self._artifacts_file)
                return

    def save_endpoints(self, endpoints: list[Endpoint]):
        for ep in endpoints:
            if not any(e.id == ep.id for e in self._endpoints):
                self._endpoints.append(ep)
        self._save(self._endpoints, self._endpoints_file)

    def get_endpoints(self, artifact_id: str | None = None) -> list[Endpoint]:
        if artifact_id:
            return [e for e in self._endpoints if e.artifact_id == artifact_id]
        return list(self._endpoints)

    def get_endpoints_by_project(self, project_id: str) -> list[Endpoint]:
        artifact_ids = {a.id for a in self._artifacts if a.project_id == project_id}
        return [e for e in self._endpoints if e.artifact_id in artifact_ids]


db = DBPool()


class StoreAdapter:
    def __init__(self, pool: DBPool):
        self.pool = pool
        self.fs = pool._file_store

    @property
    def _store(self):
        if self.pool._file_store:
            return self.pool._file_store
        return self

    def create_project(self, name: str, base_url: str | None = None) -> Project:
        return self.fs.create_project(name, base_url) if self.fs else None

    def get_project(self, name: str) -> Project | None:
        return self.fs.get_project(name) if self.fs else None

    def get_project_by_id(self, project_id: str) -> Project | None:
        return self.fs.get_project_by_id(project_id) if self.fs else None

    def list_projects(self) -> list[Project]:
        return self.fs.list_projects() if self.fs else []

    def update_project(self, project: Project):
        if self.fs:
            self.fs.update_project(project)

    def create_artifact(self, artifact: Artifact) -> Artifact:
        return self.fs.create_artifact(artifact) if self.fs else artifact

    def get_artifact(self, artifact_id: str) -> Artifact | None:
        return self.fs.get_artifact(artifact_id) if self.fs else None

    def list_artifacts(self, project_id: str | None = None) -> list[Artifact]:
        return self.fs.list_artifacts(project_id) if self.fs else []

    def update_artifact(self, artifact: Artifact):
        if self.fs:
            self.fs.update_artifact(artifact)

    def save_endpoints(self, endpoints: list[Endpoint]):
        if self.fs:
            self.fs.save_endpoints(endpoints)

    def get_endpoints(self, artifact_id: str | None = None) -> list[Endpoint]:
        return self.fs.get_endpoints(artifact_id) if self.fs else []

    def get_endpoints_by_project(self, project_id: str) -> list[Endpoint]:
        return self.fs.get_endpoints_by_project(project_id) if self.fs else []


store = StoreAdapter(db)
