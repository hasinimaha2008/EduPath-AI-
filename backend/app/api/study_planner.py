from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, StudyPlan, StudyTask, Topic
from app.schemas.schemas import (
    StudyPlanResponse, StudyTaskResponse, StudyPlanGenerateRequest,
    StudyTaskCreateRequest, StudyTaskUpdateRequest, RescheduleMissedRequest,
    AdaptiveRecommendationItem, PlannerProgressResponse
)
from app.services.intelligence_engine import intelligence_engine

router = APIRouter(prefix="/study-planner", tags=["AI Study Planner"])

def _serialize_task(t: StudyTask, today_str: str) -> StudyTaskResponse:
    is_overdue = (not t.is_completed) and (t.scheduled_date < today_str)
    return StudyTaskResponse(
        id=t.id,
        study_plan_id=t.study_plan_id,
        topic_id=t.topic_id,
        topic_name=t.topic.name if t.topic else "Curriculum Study",
        title=t.title,
        description=t.description,
        scheduled_date=t.scheduled_date,
        duration_minutes=t.duration_minutes,
        priority=t.priority,
        task_type=getattr(t, "task_type", "study") or "study",
        difficulty_level=getattr(t, "difficulty_level", "medium") or "medium",
        action_url=getattr(t, "action_url", None),
        notes=getattr(t, "notes", None),
        is_completed=t.is_completed,
        completed_at=t.completed_at,
        is_overdue=is_overdue
    )

def _serialize_plan(plan: StudyPlan, today_str: str) -> StudyPlanResponse:
    tasks_out = [_serialize_task(t, today_str) for t in plan.tasks]
    total = len(tasks_out)
    completed = sum(1 for t in tasks_out if t.is_completed)
    overdue = sum(1 for t in tasks_out if t.is_overdue)
    adherence = round((completed / total) * 100.0, 1) if total > 0 else 0.0

    return StudyPlanResponse(
        id=plan.id,
        title=plan.title,
        start_date=plan.start_date,
        end_date=plan.end_date,
        daily_hours_target=plan.daily_hours_target,
        status=plan.status,
        exam_date=getattr(plan, "exam_date", None),
        learning_priority=getattr(plan, "learning_priority", "balanced") or "balanced",
        total_tasks=total,
        completed_tasks=completed,
        overdue_tasks=overdue,
        adherence_rate=adherence,
        tasks=tasks_out,
        created_at=plan.created_at
    )

@router.post("/generate", response_model=StudyPlanResponse)
async def generate_study_plan(
    req: StudyPlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Phase 7: Generates an intelligent, adaptive study plan based on student-selected
    subjects, topics, exam targets, available daily hours, and verified weak topic performance.
    """
    plan = await intelligence_engine.generate_adaptive_study_plan(
        session=session,
        user_id=current_user.id,
        title=req.title or "Personalized Adaptive Study Plan",
        daily_hours=req.daily_hours_target,
        days_duration=req.days_duration,
        focus_weak_topics=req.focus_weak_topics,
        subject_ids=req.subject_ids,
        topic_ids=req.topic_ids,
        exam_date=req.exam_date,
        learning_priority=req.learning_priority or "balanced",
        include_revision=req.include_revision,
        include_quizzes=req.include_quizzes
    )
    
    # Reload with tasks and topic relationships
    stmt = select(StudyPlan).options(
        selectinload(StudyPlan.tasks).selectinload(StudyTask.topic)
    ).where(StudyPlan.id == plan.id)
    res = await session.execute(stmt)
    loaded_plan = res.scalar_one()

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return _serialize_plan(loaded_plan, today_str)

@router.get("/active", response_model=Optional[StudyPlanResponse])
async def get_active_study_plan(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns the student's current active adaptive study plan, or automatically
    synthesizes a baseline plan if none exists.
    """
    stmt = select(StudyPlan).options(
        selectinload(StudyPlan.tasks).selectinload(StudyTask.topic)
    ).where(
        StudyPlan.user_id == current_user.id,
        StudyPlan.status == "active"
    ).order_by(StudyPlan.created_at.desc()).limit(1)

    res = await session.execute(stmt)
    plan = res.scalar_one_or_none()

    if not plan:
        plan = await intelligence_engine.generate_adaptive_study_plan(
            session=session,
            user_id=current_user.id
        )
        stmt = select(StudyPlan).options(
            selectinload(StudyPlan.tasks).selectinload(StudyTask.topic)
        ).where(StudyPlan.id == plan.id)
        res = await session.execute(stmt)
        plan = res.scalar_one()

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return _serialize_plan(plan, today_str)

@router.post("/tasks/{task_id}/toggle")
async def toggle_task_completion(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Toggles completion state of a scheduled task and tracks completed_at timestamp.
    """
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
    """
    Manually reschedules an individual study task to a new target date.
    """
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

@router.put("/tasks/{task_id}", response_model=StudyTaskResponse)
async def update_task(
    task_id: str,
    req: StudyTaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Allows students to edit scheduled study task attributes (title, notes, duration, priority).
    """
    stmt = select(StudyTask, StudyPlan).join(
        StudyPlan, StudyTask.study_plan_id == StudyPlan.id
    ).options(selectinload(StudyTask.topic)).where(
        StudyTask.id == task_id,
        StudyPlan.user_id == current_user.id
    )
    res = await session.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Study task not found.")

    task, plan = row
    if req.title is not None:
        task.title = req.title.strip()
    if req.description is not None:
        task.description = req.description.strip()
    if req.scheduled_date is not None:
        task.scheduled_date = req.scheduled_date.strip()
    if req.duration_minutes is not None:
        task.duration_minutes = req.duration_minutes
    if req.priority is not None:
        task.priority = req.priority
    if req.task_type is not None:
        task.task_type = req.task_type
    if req.difficulty_level is not None:
        task.difficulty_level = req.difficulty_level
    if req.notes is not None:
        task.notes = req.notes

    await session.commit()
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return _serialize_task(task, today_str)

@router.post("/tasks", response_model=StudyTaskResponse)
async def create_custom_task(
    req: StudyTaskCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Allows students to add custom or manual revision / study tasks to their active planner.
    """
    if req.study_plan_id:
        plan_stmt = select(StudyPlan).where(StudyPlan.id == req.study_plan_id, StudyPlan.user_id == current_user.id)
    else:
        plan_stmt = select(StudyPlan).where(
            StudyPlan.user_id == current_user.id,
            StudyPlan.status == "active"
        ).order_by(StudyPlan.created_at.desc()).limit(1)

    plan_res = await session.execute(plan_stmt)
    plan = plan_res.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="No active study plan found to add task to.")

    action_url = None
    if req.task_type == "quiz" and req.topic_id:
        action_url = f"/dashboard/quiz?topic_id={req.topic_id}"
    elif req.task_type in ["study", "revision"]:
        action_url = "/dashboard/notes"

    new_task = StudyTask(
        study_plan_id=plan.id,
        topic_id=req.topic_id,
        title=req.title.strip(),
        description=req.description,
        scheduled_date=req.scheduled_date.strip(),
        duration_minutes=req.duration_minutes,
        priority=req.priority,
        task_type=req.task_type,
        difficulty_level=req.difficulty_level,
        action_url=action_url,
        notes=req.notes,
        is_completed=False
    )
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    stmt = select(StudyTask).options(selectinload(StudyTask.topic)).where(StudyTask.id == new_task.id)
    reloaded = (await session.execute(stmt)).scalar_one()

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return _serialize_task(reloaded, today_str)

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Removes a study task from the student's schedule.
    """
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
    await session.delete(task)
    await session.commit()
    return {"message": "Study task removed successfully.", "task_id": task_id}

@router.post("/reschedule-missed")
async def reschedule_missed_tasks(
    req: Optional[RescheduleMissedRequest] = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Phase 7 Adaptive Rescheduling: Automatically detects overdue/missed tasks and
    redistributes them into upcoming available schedule slots without overloading any single day.
    """
    plan_id = req.study_plan_id if req else None
    start_date = req.start_from_date if req else None
    result = await intelligence_engine.reschedule_missed_tasks(
        session=session,
        user_id=current_user.id,
        plan_id=plan_id,
        start_from_date=start_date
    )
    return result

@router.get("/adaptive-recommendations", response_model=List[AdaptiveRecommendationItem])
async def get_adaptive_recommendations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Analyzes student quiz scores, weak topics, and overdue tasks to suggest proactive
    schedule additions and revision sessions.
    """
    recs = await intelligence_engine.get_adaptive_planner_recommendations(
        session=session,
        user_id=current_user.id
    )
    return recs

@router.get("/progress", response_model=PlannerProgressResponse)
async def get_planner_progress(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns daily and weekly progress, schedule adherence percentage,
    upcoming exam countdown, and study streaks.
    """
    progress = await intelligence_engine.get_planner_progress(
        session=session,
        user_id=current_user.id
    )
    return progress
