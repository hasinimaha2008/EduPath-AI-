from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, CareerRole, CareerSkillRequirement, UserSkill, Skill, SkillGap
from app.schemas.schemas import SkillGapResponse, SkillGapItem, CareerRoleResponse

router = APIRouter(prefix="/skills", tags=["Skill Gap Analysis"])

@router.get("/gaps/{career_role_id}", response_model=SkillGapResponse)
async def get_skill_gaps_for_career(
    career_role_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Analyzes skill gaps against target career role, clearly distinguishing
    demonstrated (quiz-verified) skills from self-reported skills and missing skills.
    """
    role_stmt = select(CareerRole).where(CareerRole.id == career_role_id)
    role_res = await session.execute(role_stmt)
    role = role_res.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Career role not found.")

    # Fetch role requirements
    req_stmt = select(CareerSkillRequirement, Skill).join(
        Skill, CareerSkillRequirement.skill_id == Skill.id
    ).where(
        CareerSkillRequirement.career_role_id == role.id
    )
    req_res = await session.execute(req_stmt)
    requirements = req_res.all()

    # Fetch user skills
    us_stmt = select(UserSkill).where(UserSkill.user_id == current_user.id)
    us_res = await session.execute(us_stmt)
    user_skills = {us.skill_id: us for us in us_res.scalars().all()}

    gap_items = []
    total_prof = 0.0

    for req, skill in requirements:
        user_skill = user_skills.get(skill.id)
        
        if user_skill:
            prof = user_skill.proficiency_level
            total_prof += min(prof, 100.0)
            status_val = "existing" if prof >= req.min_proficiency else "needs_improvement"
            evidence_source = user_skill.source  # "demonstrated" or "self_reported"
            priority = "High" if (req.importance_level == "Core" and status_val != "existing") else "Medium"
            rec_text = (
                f"Current verified score: {prof}%. Target threshold is {req.min_proficiency}%. "
                f"Complete advanced topic quizzes in {skill.name} to reinforce demonstrated mastery."
            )
        else:
            prof = 0.0
            status_val = "missing"
            evidence_source = "missing"
            priority = "High" if req.importance_level == "Core" else "Low"
            rec_text = f"Begin with fundamental study notes and beginner quizzes covering {skill.name} concepts."

        gap_items.append(
            SkillGapItem(
                skill_name=skill.name,
                category=skill.category,
                status=status_val,
                priority=priority,
                proficiency=prof,
                evidence_source=evidence_source,
                learning_recommendation=rec_text
            )
        )

    readiness = round(total_prof / (len(requirements) * 100.0) * 100.0, 1) if requirements else 0.0

    return SkillGapResponse(
        career_role=CareerRoleResponse.model_validate(role),
        overall_readiness=readiness,
        gaps=gap_items
    )
