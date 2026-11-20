from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import AnalyticsDashboardResponse
from app.services.intelligence_engine import intelligence_engine

router = APIRouter(prefix="/analytics", tags=["Learning Analytics"])

@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns actual user learning metrics: quizzes attempted, avg score,
    learning activity timeline, verified strong and weak topics, and revision recommendations.
    Never returns fabricated dummy numbers.
    """
    analytics = await intelligence_engine.get_user_analytics(session, current_user.id)
    return AnalyticsDashboardResponse(**analytics)
