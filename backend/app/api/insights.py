from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.services.intelligence_engine import intelligence_engine

router = APIRouter(prefix="/insights", tags=["AI Learning Insights & Mistake Analysis"])

@router.get("/mistakes")
async def get_mistakes(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns student mistake analytics (Upgrade 5):
    - Categorized error breakdown (conceptual misunderstanding, incorrect application, calculation error, etc.)
    - Repeated mistakes list with frequency counts
    - Recent mistakes history with explanations and suggested fixes
    - Actionable pedagogical remediation advice
    """
    return await intelligence_engine.get_mistake_insights(session, current_user.id)

@router.get("/summary")
async def get_insights_summary(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns learning trend metrics, improvement rate, and high-priority revision focus.
    """
    analytics = await intelligence_engine.get_user_analytics(session, current_user.id)
    mistakes = await intelligence_engine.get_mistake_insights(session, current_user.id)
    return {
        "analytics": analytics,
        "mistakes": mistakes
    }
