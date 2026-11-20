from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, TopicPerformance, Topic, Subject
from app.schemas.schemas import TopicPerformanceResponse

router = APIRouter(prefix="/topics", tags=["Topic Performance"])

@router.get("/performance", response_model=List[TopicPerformanceResponse])
async def get_topic_performance(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns actual tracked topic performance for current user across all subjects.
    Mastery requires repeated evidence across assessments.
    """
    stmt = select(TopicPerformance, Topic.name, Subject.name).join(
        Topic, TopicPerformance.topic_id == Topic.id
    ).join(
        Subject, TopicPerformance.subject_id == Subject.id, isouter=True
    ).where(
        TopicPerformance.user_id == current_user.id
    ).order_by(TopicPerformance.accuracy_percentage.asc())

    res = await session.execute(stmt)
    records = res.all()

    items = []
    for tp, topic_name, subject_name in records:
        items.append(
            TopicPerformanceResponse(
                id=tp.id,
                subject_name=subject_name or "General",
                topic_name=topic_name,
                topic_id=tp.topic_id,
                total_attempts=tp.total_attempts,
                correct_answers=tp.correct_answers,
                incorrect_answers=tp.incorrect_answers,
                accuracy_percentage=tp.accuracy_percentage,
                mastery_status=tp.mastery_status,
                last_practiced_at=tp.last_practiced_at
            )
        )
    return items
