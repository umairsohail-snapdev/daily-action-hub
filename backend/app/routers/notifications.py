from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import User, Meeting, ActionItem
from ..auth import get_current_user
from ..services.notification import NotificationService
from ..services.calendar import CalendarService
from datetime import datetime, timedelta

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/trigger-daily-brief")
def trigger_daily_brief(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Manually trigger the Daily Brief email for the current user.
    In production, this would be called by a scheduler.
    """
    # Fetch today's meetings (reusing logic from dashboard or calendar service)
    # For simplicity, let's fetch from DB if synced, or we could sync live.
    # Let's assume DB is source of truth for the brief.
    
    now = datetime.utcnow()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    statement = select(Meeting).where(
        Meeting.user_id == current_user.id,
        Meeting.start_time >= start_of_day,
        Meeting.start_time <= end_of_day
    )
    meetings = session.exec(statement).all()
    
    service = NotificationService()
    service.send_daily_brief(current_user, meetings)
    
    return {"message": "Daily brief triggered successfully"}

@router.post("/trigger-reminders")
def trigger_reminders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Manually trigger reminders for unresolved action items.
    """
    # Fetch all incomplete action items for this user
    statement = select(ActionItem).join(Meeting).where(
        Meeting.user_id == current_user.id,
        ActionItem.is_completed == False
    )
    pending_items = session.exec(statement).all()
    
    service = NotificationService()
    if pending_items:
        service.send_unresolved_reminders(current_user, pending_items)
        return {"message": f"Reminders sent for {len(pending_items)} items"}
    else:
        return {"message": "No pending items found"}