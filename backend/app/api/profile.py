from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, LearningProfile, CareerRole
from app.services.intelligence_engine import intelligence_engine

router = APIRouter(prefix="/profile", tags=["Student Learning Profile"])

class LearningProfileUpdateRequest(BaseModel):
    preferred_language: Optional[str] = None
    explanation_style: Optional[str] = None
    daily_goal_minutes: Optional[int] = Field(None, ge=10, le=480)
    target_career_id: Optional[str] = None
    learning_preferences: Optional[Dict[str, Any]] = None

@router.get("/learning")
async def get_learning_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Retrieves the authenticated student's persistent learning profile,
    including preferred language (14 languages), explanation depth mode,
    daily study goal, and targeted career role.
    """
    profile = await intelligence_engine.get_or_create_learning_profile(session, current_user.id)

    target_role_title = None
    if profile.target_career_id:
        role_stmt = select(CareerRole.title).where(CareerRole.id == profile.target_career_id)
        role_res = await session.execute(role_stmt)
        target_role_title = role_res.scalar_one_or_none()

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "preferred_language": profile.preferred_language,
        "explanation_style": profile.explanation_style,
        "daily_goal_minutes": profile.daily_goal_minutes,
        "target_career_id": profile.target_career_id,
        "target_career_title": target_role_title,
        "learning_preferences": profile.preferences,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at
    }

@router.put("/learning")
async def update_learning_profile(
    req: LearningProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Updates the student's persistent learning profile and triggers
    career alignment and notification workflows if target career changes.
    """
    updates = req.dict(exclude_unset=True)
    updated_profile = await intelligence_engine.update_learning_profile(session, current_user.id, updates)

    target_role_title = None
    if updated_profile.target_career_id:
        role_stmt = select(CareerRole.title).where(CareerRole.id == updated_profile.target_career_id)
        role_res = await session.execute(role_stmt)
        target_role_title = role_res.scalar_one_or_none()

    return {
        "id": updated_profile.id,
        "user_id": updated_profile.user_id,
        "preferred_language": updated_profile.preferred_language,
        "explanation_style": updated_profile.explanation_style,
        "daily_goal_minutes": updated_profile.daily_goal_minutes,
        "target_career_id": updated_profile.target_career_id,
        "target_career_title": target_role_title,
        "learning_preferences": updated_profile.preferences,
        "updated_at": updated_profile.updated_at
    }
