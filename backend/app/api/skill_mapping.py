from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.models import Subject, Topic, Skill, CareerRole, SubjectSkillMapping
from app.schemas.schemas import SubjectResponse, SkillResponse, SubjectSkillMappingResponse

router = APIRouter(prefix="/skills", tags=["Academic-to-Industry Skill Mapping"])

@router.get("/subjects", response_model=List[SubjectResponse])
async def list_subjects(session: AsyncSession = Depends(get_db)):
    stmt = select(Subject).options(selectinload(Subject.topics)).order_by(Subject.name)
    res = await session.execute(stmt)
    subjects = res.scalars().all()
    return [SubjectResponse.model_validate(s) for s in subjects]

@router.get("/catalog", response_model=List[SkillResponse])
async def list_skills(session: AsyncSession = Depends(get_db)):
    stmt = select(Skill).order_by(Skill.category, Skill.name)
    res = await session.execute(stmt)
    skills = res.scalars().all()
    return [SkillResponse.model_validate(s) for s in skills]

@router.get("/mappings", response_model=List[SubjectSkillMappingResponse])
async def list_subject_skill_mappings(session: AsyncSession = Depends(get_db)):
    """
    Returns the complete Academic Subject -> Topic -> Industry Competency -> Skill -> Career Role graph.
    """
    stmt = select(
        SubjectSkillMapping.id,
        Subject.name.label("subject_name"),
        Topic.name.label("topic_name"),
        SubjectSkillMapping.competency_name,
        Skill.name.label("skill_name"),
        CareerRole.title.label("career_role_title")
    ).join(
        Subject, SubjectSkillMapping.subject_id == Subject.id
    ).join(
        Topic, SubjectSkillMapping.topic_id == Topic.id
    ).join(
        Skill, SubjectSkillMapping.skill_id == Skill.id
    ).join(
        CareerRole, SubjectSkillMapping.career_role_id == CareerRole.id
    ).order_by(Subject.name, Topic.name)

    res = await session.execute(stmt)
    rows = res.all()

    return [
        SubjectSkillMappingResponse(
            id=r.id,
            subject_name=r.subject_name,
            topic_name=r.topic_name,
            competency_name=r.competency_name,
            skill_name=r.skill_name,
            career_role_title=r.career_role_title
        )
        for r in rows
    ]
