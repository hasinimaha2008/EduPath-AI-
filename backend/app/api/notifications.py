from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Notification
from app.services.personalized_learning_service import personalized_learning_service

router = APIRouter(prefix="/notifications", tags=["Smart Notifications & Reminders"])

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    action_url: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NotificationListResponse(BaseModel):
    unread_count: int
    notifications: List[NotificationResponse]

@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns user notifications sorted by newest first, with unread badge count (Upgrade 8).
    """
    stmt = select(Notification).where(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(limit)
    res = await session.execute(stmt)
    notifs = res.scalars().all()

    unread_stmt = select(func.count(Notification.id)).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    )
    unread_res = await session.execute(unread_stmt)
    unread_count = unread_res.scalar() or 0

    return NotificationListResponse(
        unread_count=unread_count,
        notifications=notifs
    )

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Marks a single notification as read.
    """
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    )
    res = await session.execute(stmt)
    notif = res.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    await session.commit()
    return {"status": "success", "notification_id": notification_id, "is_read": True}

@router.put("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Marks all notifications for the authenticated user as read.
    """
    stmt = update(Notification).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).values(is_read=True)
    await session.execute(stmt)
    await session.commit()
    return {"status": "success", "message": "All notifications marked as read"}

@router.post("/trigger-reminders")
async def trigger_revision_reminders(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Evaluates due revisions and incomplete study tasks, creating reminders for items due today.
    """
    due_items = await personalized_learning_service.get_due_revisions(session, current_user.id)
    reminders_created = 0

    for item in due_items:
        if item["status"] in ["due_today", "overdue"]:
            # Check if reminder already sent today
            notif = Notification(
                user_id=current_user.id,
                title=f"Revision Due: {item['topic_name']}",
                message=f"Your scheduled spaced repetition review for {item['topic_name']} is {item['status'].replace('_', ' ')}. Practice now to reinforce long-term memory.",
                notification_type="revision_due",
                action_url=f"/dashboard/workspace?topic_id={item['topic_id']}" if item["topic_id"] else "/dashboard/study-plan"
            )
            session.add(notif)
            reminders_created += 1

    await session.commit()
    return {"status": "success", "reminders_created": reminders_created}
