from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.services.intelligence_engine import intelligence_engine
from app.services.personalized_learning_service import personalized_learning_service

router = APIRouter(prefix="/workspace", tags=["Interactive Learning Workspace"])

class ExplainConceptRequest(BaseModel):
    topic_name: str
    concept_name: Optional[str] = None
    mode: str = "step_by_step"  # beginner, intermediate, advanced, step_by_step, real_world, exam_oriented
    subject_name: Optional[str] = None
    context_notes: Optional[str] = None

@router.get("/topic/{topic_id}")
async def get_topic_workspace_data(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns unified workspace view aggregating subject, topic, notes, documents,
    quiz history, accuracy stats, and due revision tasks in one screen (Upgrade 7).
    """
    try:
        return await intelligence_engine.get_topic_workspace(session, current_user.id, topic_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/explain")
async def explain_concept(
    req: ExplainConceptRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates tailored pedagogical explanation across 6 depth modes:
    - beginner: Everyday analogies, simple conceptual intuition
    - intermediate: Standard academic formal rigor and component interactions
    - advanced: Systems engineering, invariant proofs, lock contention, tradeoffs
    - step_by_step: Granular numbered execution trace
    - real_world: Production enterprise case study and tooling
    - exam_oriented: High-yield marks breakdown and common student pitfalls
    """
    return await personalized_learning_service.generate_explanation(
        topic_name=req.topic_name,
        concept_name=req.concept_name,
        mode=req.mode,
        subject_name=req.subject_name,
        context_notes=req.context_notes
    )

@router.get("/ecosystem-summary")
async def get_ecosystem_summary(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns unified ecosystem summary aggregating documents, notes, quizzes,
    analytics, active study plan, career readiness, and actionable recommendations.
    """
    return await intelligence_engine.get_ecosystem_summary(session, current_user.id)

