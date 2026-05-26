from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class SubscriptionTier(str, Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    email: str
    hashed_password: str
    display_name: str | None = None
    api_key: str | None = None
    tier: SubscriptionTier = SubscriptionTier.free
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Team(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    owner_id: str
    member_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str
    tier: SubscriptionTier
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    cancel_at_period_end: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UsageRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str
    project_id: str | None = None
    endpoint_id: str | None = None
    tool_name: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
