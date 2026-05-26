import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from agentbridge.db import db, TIER_LIMITS
from agentbridge.models.user import SubscriptionTier, Subscription, User
from agentbridge.api.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/api/billing", tags=["billing"])

STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID", "price_pro_monthly")
STRIPE_ENT_PRICE_ID = os.getenv("STRIPE_ENT_PRICE_ID", "price_ent_monthly")


class SubscriptionResponse(BaseModel):
    id: str
    tier: str
    current_period_start: str | None = None
    current_period_end: str | None = None
    cancel_at_period_end: bool = False


class UpgradeRequest(BaseModel):
    tier: str


class TierInfo(BaseModel):
    tier: str
    price_monthly: int
    price_yearly: int
    endpoints: int
    teams: int
    features: list[str]
    highlighted: bool = False


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(user: User = Depends(get_current_user)):
    sub = await db.get_subscription(user.id)
    if not sub:
        sub = Subscription(user_id=user.id, tier=SubscriptionTier.free)
        sub = await db.create_subscription(sub)
    return SubscriptionResponse(
        id=sub.id,
        tier=sub.tier.value,
        current_period_start=sub.current_period_start.isoformat() if sub.current_period_start else None,
        current_period_end=sub.current_period_end.isoformat() if sub.current_period_end else None,
        cancel_at_period_end=sub.cancel_at_period_end,
    )


@router.get("/tiers", response_model=list[TierInfo])
async def list_tiers():
    return [
        TierInfo(
            tier="free",
            price_monthly=0,
            price_yearly=0,
            endpoints=TIER_LIMITS[SubscriptionTier.free]["endpoints"],
            teams=TIER_LIMITS[SubscriptionTier.free]["teams"],
            features=["Public MCP endpoints", "3 API endpoints", "1 team", "Community support"],
        ),
        TierInfo(
            tier="pro",
            price_monthly=29,
            price_yearly=290,
            endpoints=TIER_LIMITS[SubscriptionTier.pro]["endpoints"],
            teams=TIER_LIMITS[SubscriptionTier.pro]["teams"],
            features=["Everything in Free", "50 API endpoints", "5 teams", "Private MCP endpoints", "Custom branding", "Email support"],
            highlighted=True,
        ),
        TierInfo(
            tier="enterprise",
            price_monthly=99,
            price_yearly=990,
            endpoints=999_999,
            teams=999_999,
            features=["Everything in Pro", "Unlimited endpoints", "Unlimited teams", "SSO / SAML", "Audit logs", "Priority support", "Custom SLA"],
        ),
    ]


@router.post("/upgrade")
async def upgrade_tier(req: UpgradeRequest, user: User = Depends(get_current_user)):
    try:
        new_tier = SubscriptionTier(req.tier)
    except ValueError:
        raise HTTPException(400, f"Invalid tier: {req.tier}")

    sub = await db.get_subscription(user.id)
    now = datetime.utcnow()

    if not sub:
        sub = Subscription(
            user_id=user.id, tier=new_tier,
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
        )
        sub = await db.create_subscription(sub)
    else:
        sub.tier = new_tier
        sub.current_period_start = now
        sub.current_period_end = now + timedelta(days=30)
        await db.update_subscription(sub)

    user.tier = new_tier
    await db.update_user(user)

    return {
        "message": f"Upgraded to {new_tier.value}",
        "tier": new_tier.value,
        "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
    }


@router.post("/cancel")
async def cancel_subscription(user: User = Depends(get_current_user)):
    sub = await db.get_subscription(user.id)
    if not sub or sub.tier == SubscriptionTier.free:
        raise HTTPException(400, "No active paid subscription")

    sub.cancel_at_period_end = True
    await db.update_subscription(sub)

    return {"message": "Subscription will cancel at the end of the billing period"}


@router.post("/reactivate")
async def reactivate_subscription(user: User = Depends(get_current_user)):
    sub = await db.get_subscription(user.id)
    if not sub:
        raise HTTPException(400, "No subscription found")

    sub.cancel_at_period_end = False
    await db.update_subscription(sub)

    return {"message": "Subscription reactivated"}


@router.post("/downgrade")
async def downgrade_tier(user: User = Depends(get_current_user)):
    sub = await db.get_subscription(user.id)
    if not sub:
        raise HTTPException(400, "No subscription found")

    sub.tier = SubscriptionTier.free
    user.tier = SubscriptionTier.free
    sub.cancel_at_period_end = False
    await db.update_subscription(sub)
    await db.update_user(user)

    return {"message": "Downgraded to free tier", "tier": "free"}


@router.post("/checkout")
async def create_checkout_session(user: User = Depends(get_current_user), tier: str = "pro"):
    if not STRIPE_SECRET or STRIPE_SECRET.startswith("sk_live_"):
        return {
            "url": f"https://agentbridge-one.vercel.app/billing/success?tier={tier}",
            "message": "Stripe not configured. Using test checkout.",
            "session_id": "test_session",
        }
    import stripe
    stripe.api_key = STRIPE_SECRET
    try:
        sub = await db.get_subscription(user.id)
        customer_id = sub.stripe_customer_id if sub else None
        if not customer_id:
            customer = stripe.Customer.create(email=user.email, metadata={"user_id": user.id})
            customer_id = customer.id
            if sub:
                sub.stripe_customer_id = customer_id
                await db.update_subscription(sub)

        price_id = STRIPE_PRO_PRICE_ID if tier == "pro" else STRIPE_ENT_PRICE_ID
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"https://agentbridge-one.vercel.app/billing/success?tier={tier}",
            cancel_url=f"https://agentbridge-one.vercel.app/billing",
        )
        return {"url": session.url, "session_id": session.id}
    except Exception as e:
        raise HTTPException(500, f"Stripe error: {e}")
