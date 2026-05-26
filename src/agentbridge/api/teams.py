from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from agentbridge.db import db, TIER_LIMITS
from agentbridge.models.user import Team, User, SubscriptionTier
from agentbridge.api.auth import get_current_user, check_tier_limit, check_tier_bool

router = APIRouter(prefix="/api/teams", tags=["teams"])


class CreateTeamRequest(BaseModel):
    name: str


class AddMemberRequest(BaseModel):
    email: str


@router.get("")
async def list_teams(user: User = Depends(get_current_user)):
    teams = await db.list_user_teams(user.id)
    return [t.model_dump(mode="json") for t in teams]


@router.post("")
async def create_team(req: CreateTeamRequest, user: User = Depends(get_current_user)):
    teams = await db.list_user_teams(user.id)
    limit = check_tier_limit(user, "teams")
    if len(teams) >= limit:
        raise HTTPException(400, f"Team limit reached ({limit}) on {user.tier.value} tier")

    team = Team(name=req.name, owner_id=user.id, member_ids=[])
    team = await db.create_team(team)
    return team.model_dump(mode="json")


@router.get("/{team_id}")
async def get_team(team_id: str, user: User = Depends(get_current_user)):
    team = await db.get_team(team_id)
    if not team:
        raise HTTPException(404, "Team not found")
    if team.owner_id != user.id and user.id not in team.member_ids:
        raise HTTPException(403, "Not a member")
    return team.model_dump(mode="json")


@router.post("/{team_id}/members")
async def add_member(team_id: str, req: AddMemberRequest, user: User = Depends(get_current_user)):
    team = await db.get_team(team_id)
    if not team:
        raise HTTPException(404, "Team not found")
    if team.owner_id != user.id:
        raise HTTPException(403, "Only the owner can add members")

    member = await db.get_user_by_email(req.email)
    if not member:
        raise HTTPException(404, f"User not found: {req.email}")

    if member.id not in team.member_ids:
        team.member_ids = team.member_ids + [member.id]
        await db.update_team(team)

    return {"message": "Member added"}


@router.delete("/{team_id}/members/{member_id}")
async def remove_member(team_id: str, member_id: str, user: User = Depends(get_current_user)):
    team = await db.get_team(team_id)
    if not team:
        raise HTTPException(404, "Team not found")
    if team.owner_id != user.id and user.id != member_id:
        raise HTTPException(403, "Not authorized")

    team.member_ids = [m for m in team.member_ids if m != member_id]
    await db.update_team(team)
    return {"message": "Member removed"}


@router.delete("/{team_id}")
async def delete_team(team_id: str, user: User = Depends(get_current_user)):
    team = await db.get_team(team_id)
    if not team:
        raise HTTPException(404, "Team not found")
    if team.owner_id != user.id:
        raise HTTPException(403, "Only the owner can delete the team")

    await db.delete_team(team_id)
    return {"message": "Team deleted"}
