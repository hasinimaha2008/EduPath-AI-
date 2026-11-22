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


# --- Phase 6: Student Career Profile Management ---
from app.models.models import UserSkill, Skill, QuizAttempt, TopicPerformance
from app.schemas.schemas import StudentCareerProfileResponse, StudentProfileUpdateRequest

@router.get("/student", response_model=StudentCareerProfileResponse)
async def get_student_career_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns complete student-provided information (interests, skills, preferred domains,
    career goals, projects) alongside verified academic learning progress.
    Never invents student qualifications.
    """
    profile = await intelligence_engine.get_or_create_learning_profile(session, current_user.id)
    prefs = profile.preferences

    target_role_title = None
    if profile.target_career_id:
        role_stmt = select(CareerRole.title).where(CareerRole.id == profile.target_career_id)
        role_res = await session.execute(role_stmt)
        target_role_title = role_res.scalar_one_or_none()

    # Fetch demonstrated skills
    us_stmt = select(UserSkill, Skill.name).join(Skill, UserSkill.skill_id == Skill.id).where(
        UserSkill.user_id == current_user.id,
        UserSkill.source == "demonstrated"
    )
    us_res = await session.execute(us_stmt)
    demonstrated_skills = [
        {
            "skill_name": s_name,
            "proficiency": us.proficiency_level,
            "evidence_notes": us.evidence_notes
        }
        for us, s_name in us_res.all()
    ]

    # Fetch actual academic progress
    attempts_stmt = select(QuizAttempt).where(QuizAttempt.user_id == current_user.id)
    attempts_res = await session.execute(attempts_stmt)
    attempts = attempts_res.scalars().all()

    total_quizzes = len(attempts)
    avg_score = round(sum(a.percentage for a in attempts) / total_quizzes, 1) if total_quizzes > 0 else 0.0
    study_hours = round(sum(a.time_taken_seconds for a in attempts) / 3600.0, 1)

    tp_stmt = select(TopicPerformance).where(
        TopicPerformance.user_id == current_user.id,
        TopicPerformance.mastery_status == "mastered"
    )
    tp_res = await session.execute(tp_stmt)
    mastered_count = len(tp_res.scalars().all())

    return StudentCareerProfileResponse(
        user_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        interests=prefs.get("interests", []),
        preferred_domains=prefs.get("preferred_domains", []),
        career_goals=prefs.get("career_goals"),
        self_reported_skills=prefs.get("self_reported_skills", []),
        demonstrated_skills=demonstrated_skills,
        projects_and_experience=prefs.get("projects_and_experience", []),
        learning_progress={
            "total_quizzes_attempted": total_quizzes,
            "average_quiz_score": avg_score,
            "study_hours": study_hours,
            "mastered_topics_count": mastered_count
        },
        target_career_id=profile.target_career_id,
        target_career_title=target_role_title,
        preferred_language=profile.preferred_language,
        explanation_style=profile.explanation_style,
        daily_goal_minutes=profile.daily_goal_minutes
    )

@router.put("/student", response_model=StudentCareerProfileResponse)
async def update_student_career_profile(
    req: StudentProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Updates student-provided career information: interests, preferred domains,
    career goals, self-reported skills, and projects/experience.
    Triggers re-evaluation of career recommendations and skill gaps.
    """
    updates = req.dict(exclude_unset=True)
    if "projects_and_experience" in updates and updates["projects_and_experience"] is not None:
        updates["projects_and_experience"] = [
            p.dict() if hasattr(p, "dict") else p for p in updates["projects_and_experience"]
        ]

    await intelligence_engine.update_learning_profile(session, current_user.id, updates)
    return await get_student_career_profile(current_user, session)
