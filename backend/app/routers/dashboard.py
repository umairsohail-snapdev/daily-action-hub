from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, date, timedelta

from ..database import get_session
from ..models import User, Meeting, ActionItem, MeetingType, MeetingRead
from ..auth import get_current_user
from ..services.calendar import CalendarService
from ..services.ai import AIService
from pydantic import BaseModel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

class DashboardResponse(BaseModel):
    date: str
    is_resolved: bool
    meetings: List[MeetingRead]

@router.post("/sync", status_code=status.HTTP_200_OK)
def sync_meetings(
    x_google_access_token: str = Header(..., alias="X-Google-Access-Token"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Syncs today's meetings from Google Calendar.
    Requires a valid Google Access Token passed in the X-Google-Access-Token header.
    """
    calendar_service = CalendarService(token=x_google_access_token)
    try:
        google_meetings = calendar_service.fetch_todays_meetings()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch from Google Calendar: {str(e)}")

    # 1. Fetch existing local meetings for today to detect deletions
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Simple check: sync covers "today", so we check meetings starting today
    # Note: CalendarService.fetch_todays_meetings also fetches based on 'today'
    
    statement = select(Meeting).where(
        Meeting.user_id == current_user.id,
        Meeting.start_time >= today_start,
        Meeting.start_time <= today_end
    )
    existing_local_meetings = session.exec(statement).all()
    existing_google_ids = {m.google_event_id for m in existing_local_meetings}

    # 2. Process Google Meetings
    synced_meetings = []
    fetched_google_ids = set()

    for g_meeting in google_meetings:
        fetched_google_ids.add(g_meeting.google_event_id)
        
        # Check if meeting already exists
        statement = select(Meeting).where(
            Meeting.google_event_id == g_meeting.google_event_id,
            Meeting.user_id == current_user.id
        )
        existing_meeting = session.exec(statement).first()

        if existing_meeting:
            # Update existing meeting details if needed
            existing_meeting.title = g_meeting.title
            existing_meeting.start_time = g_meeting.start_time
            existing_meeting.end_time = g_meeting.end_time
            existing_meeting.participants = g_meeting.participants
            existing_meeting.type = g_meeting.type
            existing_meeting.summary = g_meeting.summary or existing_meeting.summary
            session.add(existing_meeting)
            synced_meetings.append(existing_meeting)
        else:
            # Create new meeting
            g_meeting.user_id = current_user.id
            session.add(g_meeting)
            synced_meetings.append(g_meeting)
    
    # 3. Delete orphans (Local meetings not present in Google fetch)
    # Re-fetch local meetings to ensure we are operating on current session objects or use the IDs
    orphaned_ids = existing_google_ids - fetched_google_ids
    if orphaned_ids:
        # We need to query again or filter the 'existing_local_meetings' list
        # It's safer to query by ID to ensure we delete the correct rows associated with this user
        
        # Note: 'orphan_id' is the google_event_id string
        for orphan_id in orphaned_ids:
            statement = select(Meeting).where(
                Meeting.google_event_id == orphan_id,
                Meeting.user_id == current_user.id
            )
            orphan_meeting = session.exec(statement).first()
            if orphan_meeting:
                session.delete(orphan_meeting)
    
    session.commit()
    return {"message": "Sync successful", "count": len(synced_meetings), "deleted": len(orphaned_ids)}

@router.get("/today", response_model=DashboardResponse)
def get_todays_dashboard(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the dashboard data for today.
    """
    # Broaden the window to handle timezones (yesterday + today + tomorrow UTC)
    now_utc = datetime.utcnow()
    window_start = (now_utc - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    window_end = (now_utc + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)

    statement = select(Meeting).options(selectinload(Meeting.action_items)).where(
        Meeting.user_id == current_user.id,
        Meeting.start_time >= window_start,
        Meeting.start_time <= window_end
    ).order_by(Meeting.start_time)
    
    meetings = session.exec(statement).all()
    
    # Calculate if resolved (all action items completed)
    # This logic assumes a dashboard is resolved if all meetings have their action items completed
    # For MVP, let's keep it simple.
    
    is_resolved = True
    meetings_data = []
    
    for meeting in meetings:
        # Load action items
        # Since we used SQLModel with Relationship, they should be lazy loaded or we can eager load
        # But here accessing meeting.action_items should trigger a fetch if attached to session
        # However, async session handling might need explicit loading. 
        # With sync engine/session in database.py, lazy loading works within the session context.
        
        # Check for unresolved items
        for item in meeting.action_items:
            if not item.is_completed:
                is_resolved = False
        
        meetings_data.append(meeting)

    return {
        "date": date.today().isoformat(),
        "is_resolved": is_resolved,
        "meetings": meetings_data
    }

@router.get("/history", response_model=List[DashboardResponse])
def get_past_dashboards(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get past dashboards (last 7 days).
    """
    # Simplified history logic: Group meetings by date
    # For MVP, fetching last 7 days of meetings and grouping them in python
    
    end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=7)
    
    statement = select(Meeting).options(selectinload(Meeting.action_items)).where(
        Meeting.user_id == current_user.id,
        Meeting.start_time >= start_date,
        Meeting.start_time < end_date
    ).order_by(Meeting.start_time.desc())
    
    meetings = session.exec(statement).all()
    
    # Group by date
    history = {}
    for meeting in meetings:
        m_date = meeting.start_time.date().isoformat()
        if m_date not in history:
            history[m_date] = {"date": m_date, "meetings": [], "is_resolved": True}
        
        history[m_date]["meetings"].append(meeting)
        
        for item in meeting.action_items:
            if not item.is_completed:
                history[m_date]["is_resolved"] = False
                
    return list(history.values())