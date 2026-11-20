from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, StudyPlan, StudyTask, Topic
from app.schemas.schemas import (
    StudyPlanResponse, StudyTaskResponse, StudyPlanGenerateRequest
)
from app.services.intelligence_engine import intelligence_engine

router = APIRouter(prefix="/study-planner", tags=["AI Study Planner"])

@router.post("/generate", response_model=StudyPlanResponse)
async def generate_study_plan(
    req: StudyPlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    plan = await intelligence_engine.generate_adaptive_study_plan(
        session=session,
        user_id=current_user.id,
        title=req.title or "Personalized Adaptive Study Plan",
        daily_hours=req.daily_hours_target,
        days_duration=req.days_duration
    )
    
    # Reload with tasks and topic names
    stmt = select(StudyPlan).options(
        selectinload(StudyPlan.tasks).selectinload(StudyTask.topic)
    ).where(StudyPlan.id == plan.id)
    res = await session.execute(stmt)
    loaded_plan = res.scalar_one()

    tasks_out = []
    for t in loaded_plan.tasks:
        tasks_out.append(
            StudyTaskResponse(
                id=t.id,
                study_plan_id=t.study_plan_id,
                topic_id=t.topic_id,
                topic_name=t.topic.name if t.topic else "General Study",
                title=t.title,
                description=t.description,
                scheduled_date=t.scheduled_date,
                duration_minutes=t.duration_minutes,
                priority=t.priority,
                is_completed=t.is_completed,
                completed_at=t.completed_at
            )
        )

    return StudyPlanResponse(
        id=loaded_plan.id,
        title=loaded_plan.title,
        start_date=loaded_plan.start_date,
        end_date=loaded_plan.end_date,
        daily_hours_target=loaded_plan.daily_hours_target,
        status=loaded_plan.status,
        tasks=tasks_out,
        created_at=loaded_plan.created_at
    )

@router.get("/active", response_model=Optional[StudyPlanResponse])
async def get_active_study_plan(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(StudyPlan).options(
        selectinload(StudyPlan.tasks).selectinload(StudyTask.topic)
    ).where(
        StudyPlan.user_id == current_user.id,
        StudyPlan.status == "active"
    ).order_by(StudyPlan.created_at.desc()).limit(1)

    res = await session.execute(stmt)
    plan = res.scalar_one_or_none()

    if not plan:
        # Generate an initial adaptive plan automatically if none exists
        plan = await intelligence_engine.generate_adaptive_study_plan(
            session=session,
            user_id=current_user.id
        )
        stmt = select(StudyPlan).options(
            selectinload(StudyPlan.tasks).selectinload(StudyTask.topic)
        ).where(StudyPlan.id == plan.id)
        res = await session.execute(stmt)
        plan = res.scalar_one()

    tasks_out = [
        StudyTaskResponse(
            id=t.id,
            study_plan_id=t.study_plan_id,
            topic_id=t.topic_id,
            topic_name=t.topic.name if t.topic else "General Study",
            title=t.title,
            description=t.description,
            scheduled_date=t.scheduled_date,
            duration_minutes=t.duration_minutes,
            priority=t.priority,
            is_completed=t.is_completed,
            completed_at=t.completed_at
        )
        for t in plan.tasks
    ]

    return StudyPlanResponse(
        id=plan.id,
        title=plan.title,
        start_date=plan.start_date,
        end_date=plan.end_date,
        daily_hours_target=plan.daily_hours_target,
        status=plan.status,
        tasks=tasks_out,
        created_at=plan.created_at
    )

@router.post("/tasks/{task_id}/toggle")
async def toggle_task_completion(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(StudyTask, StudyPlan).join(
        StudyPlan, StudyTask.study_plan_id == StudyPlan.id
    ).where(
        StudyTask.id == task_id,
        StudyPlan.user_id == current_user.id
    )
    res = await session.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Study task not found.")

    task, plan = row
    task.is_completed = not task.is_completed
    task.completed_at = datetime.now(timezone.utc) if task.is_completed else None

    await session.commit()
    return {
        "task_id": task.id,
        "is_completed": task.is_completed,
        "completed_at": task.completed_at
    }

@router.post("/tasks/{task_id}/reschedule")
async def reschedule_task(
    task_id: str,
    new_date: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(StudyTask, StudyPlan).join(
        StudyPlan, StudyTask.study_plan_id == StudyPlan.id
    ).where(
        StudyTask.id == task_id,
        StudyPlan.user_id == current_user.id
    )
    res = await session.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Study task not found.")

    task, plan = row
    task.scheduled_date = new_date.strip()
    await session.commit()
    return {"task_id": task.id, "new_date": task.scheduled_date}
