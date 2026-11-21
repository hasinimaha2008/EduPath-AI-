from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.models import Subject, Topic
from app.schemas.schemas import SubjectResponse, TopicResponse

router = APIRouter(prefix="/subjects", tags=["Curriculum & Multi-Subject Topics"])

@router.get("", response_model=List[SubjectResponse])
async def list_all_subjects(
    category: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    """
    Returns all 16 canonical subjects with their module topics and subtopics.
    """
    stmt = select(Subject).options(selectinload(Subject.topics)).order_by(Subject.name)
    if category:
        stmt = stmt.where(Subject.category == category)
    res = await session.execute(stmt)
    subjects = res.scalars().all()
    return [SubjectResponse.model_validate(s) for s in subjects]

@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject_detail(
    subject_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Returns a single subject with full module-wise topics.
    """
    stmt = select(Subject).options(selectinload(Subject.topics)).where(Subject.id == subject_id)
    res = await session.execute(stmt)
    subj = res.scalar_one_or_none()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found.")
    return SubjectResponse.model_validate(subj)

@router.get("/{subject_id}/topics", response_model=List[TopicResponse])
async def list_subject_topics(
    subject_id: str,
    module_name: Optional[str] = None,
    only_emerging: Optional[bool] = None,
    session: AsyncSession = Depends(get_db)
):
    """
    Returns topics belonging strictly to the selected subject.
    Prevents cross-subject content leakage.
    """
    stmt = select(Topic).where(Topic.subject_id == subject_id)
    if module_name:
        stmt = stmt.where(Topic.module_name == module_name)
    if only_emerging is not None:
        stmt = stmt.where(Topic.is_emerging == only_emerging)
    stmt = stmt.order_by(Topic.order_index)
    res = await session.execute(stmt)
    topics = res.scalars().all()
    return [TopicResponse.model_validate(t) for t in topics]

@router.get("/topic/{topic_id}", response_model=TopicResponse)
async def get_topic_detail(
    topic_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Returns detailed topic metadata, subtopics, and verified educational source references.
    """
    stmt = select(Topic).where(Topic.id == topic_id)
    res = await session.execute(stmt)
    topic = res.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found.")
    return TopicResponse.model_validate(topic)
