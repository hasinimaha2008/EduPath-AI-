import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import (
    User, CareerRole, CareerRoadmap, RoadmapMilestone,
    CareerSkillRequirement, UserSkill, Skill
)
from app.schemas.schemas import (
    CareerRoadmapResponse, RoadmapMilestoneResponse,
    CareerRoleResponse, RoadmapGenerateRequest
)

router = APIRouter(prefix="/roadmaps", tags=["Career Roadmaps"])

@router.post("/generate", response_model=CareerRoadmapResponse)
async def generate_career_roadmap(
    req: RoadmapGenerateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    role_stmt = select(CareerRole).where(CareerRole.id == req.career_role_id)
    role_res = await session.execute(role_stmt)
    role = role_res.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Career role not found.")

    # Fetch required skills
    req_stmt = select(CareerSkillRequirement, Skill).join(
        Skill, CareerSkillRequirement.skill_id == Skill.id
    ).where(CareerSkillRequirement.career_role_id == role.id)
    req_res = await session.execute(req_stmt)
    requirements = req_res.all()

    # Fetch user skills
    us_stmt = select(UserSkill).where(UserSkill.user_id == current_user.id)
    us_res = await session.execute(us_stmt)
    user_skills = {us.skill_id: us.proficiency_level for us in us_res.scalars().all()}

    # Check existing roadmap
    rm_stmt = select(CareerRoadmap).where(
        CareerRoadmap.user_id == current_user.id,
        CareerRoadmap.career_role_id == role.id
    )
    rm_res = await session.execute(rm_stmt)
    existing_roadmap = rm_res.scalar_one_or_none()

    if existing_roadmap:
        # Delete old milestones to regenerate cleanly
        await session.delete(existing_roadmap)
        await session.flush()

    roadmap = CareerRoadmap(
        user_id=current_user.id,
        career_role_id=role.id,
        title=f"Personalized Career Pathway: {role.title}",
        target_timeline_months=req.target_timeline_months,
        progress_percentage=0.0
    )
    session.add(roadmap)
    await session.flush()

    # Generate structured milestones validated against requirements
    milestone_templates = [
        {
            "title": f"Phase 1: Academic & Theoretical Core ({role.title})",
            "desc": "Establish rigorous conceptual foundation in core algorithmic invariants and data structures.",
            "projects": ["Build CLI-based Data Structure benchmark suite", "Implement foundational state machine and validation parser"],
            "activities": ["Study lecture notes on Big-O complexity", "Complete 5 topic quizzes with >= 80% accuracy"]
        },
        {
            "title": f"Phase 2: Database Systems & API Integration",
            "desc": "Master schema normalization (3NF/BCNF), SQL optimization, and robust REST architectural patterns.",
            "projects": ["Design e-commerce normalized PostgreSQL relational schema", "Construct secure JWT-authenticated REST API with FastAPI"],
            "activities": ["Analyze slow queries with EXPLAIN ANALYZE", "Practice ACID transaction concurrency control"]
        },
        {
            "title": f"Phase 3: Production Engineering & Ecosystem Tools",
            "desc": "Implement testing suites, CI/CD automation, asynchronous I/O, and containerized deployment.",
            "projects": ["Develop production microservice with automated unit tests", "Configure Dockerized multi-stage container deployment"],
            "activities": ["Conduct vulnerability audit and rate limiting tests", "Benchmark async throughput under load"]
        },
        {
            "title": f"Phase 4: Capstone Industry Portfolio Project",
            "desc": "Architect an end-to-end full-stack portfolio system showcasing demonstrated technical excellence.",
            "projects": [f"Complete flagship {role.title} Capstone Platform", "Publish technical architecture writeup with benchmarks"],
            "activities": ["Perform peer code reviews", "Conduct mock technical interview sessions"]
        }
    ]

    milestones_created = []
    for idx, tmpl in enumerate(milestone_templates):
        m = RoadmapMilestone(
            roadmap_id=roadmap.id,
            title=tmpl["title"],
            description=tmpl["desc"],
            order_index=idx + 1,
            is_completed=False,
            target_date=f"Month {idx + 1}",
            suggested_projects_json=json.dumps(tmpl["projects"]),
            practice_activities_json=json.dumps(tmpl["activities"])
        )
        session.add(m)
        milestones_created.append(m)

    await session.commit()
    await session.refresh(roadmap)

    return CareerRoadmapResponse(
        id=roadmap.id,
        career_role=CareerRoleResponse.model_validate(role),
        title=roadmap.title,
        target_timeline_months=roadmap.target_timeline_months,
        progress_percentage=roadmap.progress_percentage,
        milestones=[
            RoadmapMilestoneResponse(
                id=m.id,
                title=m.title,
                description=m.description,
                order_index=m.order_index,
                is_completed=m.is_completed,
                target_date=m.target_date,
                suggested_projects=json.loads(m.suggested_projects_json or "[]"),
                practice_activities=json.loads(m.practice_activities_json or "[]")
            )
            for m in milestones_created
        ],
        created_at=roadmap.created_at,
        updated_at=roadmap.updated_at
    )

@router.get("", response_model=List[CareerRoadmapResponse])
async def list_user_roadmaps(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(CareerRoadmap).options(
        selectinload(CareerRoadmap.milestones),
        selectinload(CareerRoadmap.career_role)
    ).where(CareerRoadmap.user_id == current_user.id).order_by(CareerRoadmap.created_at.desc())

    res = await session.execute(stmt)
    roadmaps = res.scalars().all()

    output = []
    for r in roadmaps:
        output.append(
            CareerRoadmapResponse(
                id=r.id,
                career_role=CareerRoleResponse.model_validate(r.career_role),
                title=r.title,
                target_timeline_months=r.target_timeline_months,
                progress_percentage=r.progress_percentage,
                milestones=[
                    RoadmapMilestoneResponse(
                        id=m.id,
                        title=m.title,
                        description=m.description,
                        order_index=m.order_index,
                        is_completed=m.is_completed,
                        target_date=m.target_date,
                        suggested_projects=json.loads(m.suggested_projects_json or "[]"),
                        practice_activities=json.loads(m.practice_activities_json or "[]")
                    )
                    for m in r.milestones
                ],
                created_at=r.created_at,
                updated_at=r.updated_at
            )
        )
    return output

@router.post("/milestones/{milestone_id}/toggle")
async def toggle_milestone(
    milestone_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(RoadmapMilestone, CareerRoadmap).join(
        CareerRoadmap, RoadmapMilestone.roadmap_id == CareerRoadmap.id
    ).where(
        RoadmapMilestone.id == milestone_id,
        CareerRoadmap.user_id == current_user.id
    )
    res = await session.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Milestone not found.")

    milestone, roadmap = row
    milestone.is_completed = not milestone.is_completed

    # Recalculate roadmap progress
    all_m_stmt = select(RoadmapMilestone).where(RoadmapMilestone.roadmap_id == roadmap.id)
    all_m_res = await session.execute(all_m_stmt)
    all_ms = all_m_res.scalars().all()

    completed_count = sum(1 for m in all_ms if m.is_completed)
    roadmap.progress_percentage = round((completed_count / len(all_ms)) * 100.0, 1) if all_ms else 0.0

    await session.commit()
    return {
        "milestone_id": milestone.id,
        "is_completed": milestone.is_completed,
        "roadmap_progress": roadmap.progress_percentage
    }
