import os
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from agentbridge.db import db
from agentbridge.models.user import User, SubscriptionTier, Subscription

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = os.getenv("AGENTBRIDGE_SECRET_KEY", "dev-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class ApiKeyResponse(BaseModel):
    api_key: str


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str | None
    tier: str
    api_key: str | None
    created_at: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, tier: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "tier": tier, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def generate_api_key() -> str:
    return f"ab_{secrets.token_hex(24)}"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_api_key: str | None = Header(None),
) -> User:
    user_id: str | None = None

    if credentials:
        try:
            payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
        except JWTError:
            raise HTTPException(401, "Invalid token")

    if x_api_key and not user_id:
        user = await db.get_user_by_api_key(x_api_key)
        if not user:
            raise HTTPException(401, "Invalid API key")
        return user

    if not user_id:
        raise HTTPException(401, "Not authenticated")

    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_api_key: str | None = Header(None),
) -> User | None:
    try:
        return await get_current_user(credentials, x_api_key)
    except HTTPException:
        return None


def check_tier_limit(user: User, feature: str) -> int:
    from agentbridge.db import TIER_LIMITS
    limits = TIER_LIMITS.get(user.tier, TIER_LIMITS[SubscriptionTier.free])
    return limits.get(feature, 0)


def check_tier_bool(user: User, feature: str) -> bool:
    from agentbridge.db import TIER_LIMITS
    limits = TIER_LIMITS.get(user.tier, TIER_LIMITS[SubscriptionTier.free])
    return limits.get(feature, False)


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    existing = await db.get_user_by_email(req.email)
    if existing:
        raise HTTPException(400, "Email already registered")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        display_name=req.display_name,
        tier=SubscriptionTier.free,
    )
    user = await db.create_user(user)

    sub = Subscription(
        user_id=user.id,
        tier=SubscriptionTier.free,
    )
    await db.create_subscription(sub)

    token = create_access_token(user.id, user.tier.value)
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id, "email": user.email,
            "display_name": user.display_name, "tier": user.tier.value,
            "api_key": user.api_key, "created_at": user.created_at.isoformat(),
        },
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    user = await db.get_user_by_email(req.email)
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")

    token = create_access_token(user.id, user.tier.value)
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id, "email": user.email,
            "display_name": user.display_name, "tier": user.tier.value,
            "api_key": user.api_key, "created_at": user.created_at.isoformat(),
        },
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id, email=user.email, display_name=user.display_name,
        tier=user.tier.value, api_key=user.api_key,
        created_at=user.created_at.isoformat(),
    )


@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(user: User = Depends(get_current_user)):
    user.api_key = generate_api_key()
    await db.update_user(user)
    return ApiKeyResponse(api_key=user.api_key)


@router.delete("/api-keys")
async def revoke_api_key(user: User = Depends(get_current_user)):
    user.api_key = None
    await db.update_user(user)
    return {"message": "API key revoked"}


@router.post("/api-keys/regenerate", response_model=ApiKeyResponse)
async def regenerate_api_key(user: User = Depends(get_current_user)):
    user.api_key = generate_api_key()
    await db.update_user(user)
    return ApiKeyResponse(api_key=user.api_key)
