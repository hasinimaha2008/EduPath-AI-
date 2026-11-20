from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, CareerRole, CareerRecommendation, CareerSkillRequirement, UserSkill, Skill
from app.schemas.schemas import CareerRoleResponse, CareerRecommendationResponse
from app.services.intelligence_engine import intelligence_engine

router = APIRouter(prefix="/careers", tags=["Career Intelligence"])

@router.get("/roles", response_model=List[CareerRoleResponse])
async def list_career_roles(
    session: AsyncSession = Depends(get_db)
):
    stmt = select(CareerRole).order_by(CareerRole.title)
    res = await session.execute(stmt)
    roles = res.scalars().all()
    return [CareerRoleResponse.model_validate(r) for r in roles]

@router.get("/recommendations", response_model=List[CareerRecommendationResponse])
async def get_career_recommendations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns personalized career role recommendations computed by the EduPath Intelligence Engine.
    Explains the objective rationale behind each score without promising employment.
    """
    # Ensure intelligence engine recalculates fresh recommendations
    await intelligence_engine.recalculate_career_intelligence(session, current_user.id)
    await session.commit()

    stmt = select(CareerRecommendation, CareerRole).join(
        CareerRole, CareerRecommendation.career_role_id == CareerRole.id
    ).where(
        CareerRecommendation.user_id == current_user.id
    ).order_by(CareerRecommendation.match_score.desc())

    res = await session.execute(stmt)
    records = res.all()

    # Fetch user skills
    us_stmt = select(UserSkill, Skill).join(Skill, UserSkill.skill_id == Skill.id).where(UserSkill.user_id == current_user.id)
    us_res = await session.execute(us_stmt)
    user_skill_map = {us.skill_id: (us, s.name) for us, s in us_res.all()}

    output = []
    for rec, role in records:
        # Check requirements for matching vs missing
        req_stmt = select(CareerSkillRequirement, Skill).join(
            Skill, CareerSkillRequirement.skill_id == Skill.id
        ).where(CareerSkillRequirement.career_role_id == role.id)
        req_res = await session.execute(req_stmt)
        reqs = req_res.all()

        matching = []
        missing = []
        for req, sk in reqs:
            if req.skill_id in user_skill_map:
                u_sk, _ = user_skill_map[req.skill_id]
                if u_sk.proficiency_level >= req.min_proficiency:
                    matching.append(sk.name)
                else:
                    missing.append(f"{sk.name} (Proficiency: {u_sk.proficiency_level}%)")
            else:
                missing.append(sk.name)

        output.append(
            CareerRecommendationResponse(
                id=rec.id,
                career_role=CareerRoleResponse.model_validate(role),
                match_score=rec.match_score,
                rationale=rec.rationale,
                missing_skills_count=len(missing),
                matching_skills=matching,
                missing_skills=missing,
                recommended_at=rec.recommended_at
            )
        )

    return output
