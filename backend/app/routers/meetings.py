from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session, select
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import selectinload
import requests

from ..database import get_session
from ..models import User, Meeting, ActionItem, ActionType, MeetingRead
from ..auth import get_current_user
from ..services.ai import AIService
from ..services.content_providers.factory import ContentProviderFactory
from notion_client import Client
from ..config import settings

from ..services.calendar import CalendarService

router = APIRouter(prefix="/meetings", tags=["meetings"])

class ProcessMeetingRequest(BaseModel):
    content: Optional[str] = None # Optional now, as we try to fetch if not provided

class AnalyzeMeetingRequest(BaseModel):
    notes_text: str

class SyncMeetingsRequest(BaseModel):
    pass # No body needed for now, token is in header or from session if we use that flow later

@router.post("/sync")
def sync_calendar_meetings(
    x_google_access_token: Optional[str] = Header(None, alias="X-Google-Access-Token"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Syncs today's meetings from Google Calendar.
    Accepts X-Google-Access-Token header OR falls back to stored token (if we had it).
    For now, frontend sends the token.
    """
    if not x_google_access_token:
        # In a real app with offline access, we might refresh the token here.
        raise HTTPException(status_code=400, detail="Google Access Token required for sync")

    calendar_service = CalendarService(token=x_google_access_token)
    try:
        google_meetings = calendar_service.fetch_todays_meetings()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch from Google Calendar: {str(e)}")

    # Track IDs found in Google Calendar to identify deletions
    fetched_google_ids = set()
    synced_meetings = []

    for g_meeting in google_meetings:
        fetched_google_ids.add(g_meeting.google_event_id)

        # Check if meeting already exists
        statement = select(Meeting).where(
            Meeting.google_event_id == g_meeting.google_event_id,
            Meeting.user_id == current_user.id
        )
        existing_meeting = session.exec(statement).first()

        if existing_meeting:
            # Update existing meeting details
            existing_meeting.title = g_meeting.title
            existing_meeting.start_time = g_meeting.start_time
            existing_meeting.end_time = g_meeting.end_time
            existing_meeting.participants = g_meeting.participants
            # Only update type if it wasn't manually overridden? For now, source of truth is calendar.
            existing_meeting.type = g_meeting.type
            existing_meeting.summary = g_meeting.summary or existing_meeting.summary
            session.add(existing_meeting)
            synced_meetings.append(existing_meeting)
        else:
            # Create new meeting
            g_meeting.user_id = current_user.id
            session.add(g_meeting)
            synced_meetings.append(g_meeting)
    
    # Handle Deletions: Remove local meetings for today that are no longer in Google Calendar
    # Define "Today" window matching CalendarService (UTC)
    now = datetime.utcnow()
    time_min = now.replace(hour=0, minute=0, second=0, microsecond=0)
    time_max = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    statement = select(Meeting).where(
        Meeting.user_id == current_user.id,
        Meeting.start_time >= time_min,
        Meeting.start_time <= time_max,
        Meeting.google_event_id != None # Only consider synced meetings
    )
    local_meetings = session.exec(statement).all()

    for meeting in local_meetings:
        if meeting.google_event_id not in fetched_google_ids:
            # Delete associated action items first to avoid integrity errors
            # Or rely on cascade delete if configured (it seems it's not)
            # We must manually delete the meeting, which should cascade if SQLModel relationship is set up right
            # but the error suggests action items are being updated to NULL meeting_id or similar?
            # Actually, `session.delete(meeting)` should work if cascade is set in DB.
            # If not, we need to delete children first.
            
            # Deleting action items for this meeting
            # Note: In a real app we might want to keep orphan action items or move them to 'Inbox'
            # But here we delete them with the meeting as per sync logic
            for item in meeting.action_items:
                session.delete(item)
            
            session.delete(meeting)

    session.commit()
    return {"message": "Sync successful", "count": len(synced_meetings), "meetings": synced_meetings}

@router.post("/{meeting_id}/process", response_model=MeetingRead)
def process_meeting(
    meeting_id: int,
    request: ProcessMeetingRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Process a meeting's content using AI to generate a summary and extract action items.
    If content is not provided, it attempts to fetch from configured providers.
    """
    # Fetch meeting and verify ownership
    statement = select(Meeting).where(Meeting.id == meeting_id, Meeting.user_id == current_user.id)
    meeting = session.exec(statement).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting_content = request.content

    # If content not provided by frontend, try content providers
    if not meeting_content:
        providers = ContentProviderFactory.get_providers()
        meeting_date = meeting.start_time.date().isoformat()
        
        for provider in providers:
            fetched_content = provider.fetch_content(meeting.title, meeting_date)
            if fetched_content:
                meeting_content = fetched_content
                break
    
    if not meeting_content:
        # Fallback if nothing found
        meeting_content = "No content found for this meeting."

    ai_service = AIService()
    result = ai_service.process_meeting(
        meeting_title=meeting.title,
        meeting_content=meeting_content,
        participants=meeting.participants
    )
    
    # Update meeting summary
    meeting.summary = result.get("summary", "")
    session.add(meeting)
    
    # Create action items
    extracted_actions = result.get("action_items", [])
    for item in extracted_actions:
        action_item = ActionItem(
            meeting_id=meeting.id,
            description=item.get("description"),
            suggested_action=item.get("suggested_action"),
            is_completed=False
        )
        session.add(action_item)
        
    session.commit()
    # Re-fetch meeting with fresh action items
    statement = select(Meeting).options(selectinload(Meeting.action_items)).where(Meeting.id == meeting.id)
    meeting = session.exec(statement).first()
    
    return meeting

@router.get("/{meeting_id}/fetch-notes")
def fetch_meeting_notes(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # 1. Get Meeting
    statement = select(Meeting).where(Meeting.id == meeting_id, Meeting.user_id == current_user.id)
    meeting = session.exec(statement).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # 2. Setup Credentials
    notion_api_key = settings.NOTION_API_KEY.strip() if settings.NOTION_API_KEY else None
    database_id = settings.NOTION_DATABASE_ID.strip() if settings.NOTION_DATABASE_ID else None

    if not notion_api_key or not database_id:
        return {"notes": "", "error": "Notion API Key or DB ID missing."}

    # 3. Prepare Direct Request
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # 4. Query Database (Find the page)
    search_title = meeting.title.strip()
    print(f"DEBUG: Searching Notion DB {database_id} for: '{search_title}'")
    
    query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {
        "filter": {
            "property": "Task Name", # Verified verified property name
            "title": { "contains": search_title }
        }
    }
    
    try:
        response = requests.post(query_url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"ERROR: Notion Query Failed {response.status_code}: {response.text}")
            return {"notes": "", "error": f"Notion Error: {response.text}"}
            
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            print("DEBUG: No matching page found.")
            return {"notes": ""}

        # 5. Fetch Content (Get blocks from the page)
        page_id = results[0]["id"]
        print(f"DEBUG: Found page {page_id}. Fetching blocks...")
        
        blocks_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        blocks_response = requests.get(blocks_url, headers=headers)
        
        if blocks_response.status_code != 200:
             return {"notes": "", "error": "Failed to fetch page blocks"}
             
        blocks_data = blocks_response.json()
        
        text_content = []
        for block in blocks_data.get("results", []):
            b_type = block.get("type")
            if b_type in block:
                rich_text = block[b_type].get("rich_text", [])
                plain_text = "".join([t.get("plain_text", "") for t in rich_text])
                
                if plain_text:
                    if "heading" in b_type:
                        text_content.append(f"\n## {plain_text}")
                    elif "bullet" in b_type:
                        text_content.append(f"* {plain_text}")
                    else:
                        text_content.append(plain_text)

        final_notes = "\n".join(text_content)
        return {"notes": final_notes}

    except Exception as e:
        print(f"ERROR: Notion Fetch Exception: {e}")
        return {"notes": "", "error": str(e)}

@router.post("/{meeting_id}/analyze", response_model=MeetingRead)
def analyze_meeting(
    meeting_id: int,
    request: AnalyzeMeetingRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Analyze meeting notes to extract next steps using Groq AI.
    Saves the extracted action items to the database.
    """
    # Fetch meeting and verify ownership
    statement = select(Meeting).where(Meeting.id == meeting_id, Meeting.user_id == current_user.id)
    meeting = session.exec(statement).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    ai_service = AIService()
    result = ai_service.process_meeting(
        meeting_title=meeting.title,
        meeting_content=request.notes_text,
        participants=meeting.participants
    )
    
    # Update meeting summary
    meeting.summary = result.get("summary", "")
    session.add(meeting)
    
    # Create action items
    extracted_actions = result.get("action_items", [])
    
    # Optional: Clear existing action items?
    # For now, we append. In a real app, maybe we'd diff or replace.
    # To replace: session.exec(delete(ActionItem).where(ActionItem.meeting_id == meeting.id))
    
    for item in extracted_actions:
        # Map string to ActionType enum safely
        action_type_str = item.get("action_type")
        suggested_action = ActionType.CREATE_TASK # Default
        
        try:
            suggested_action = ActionType(action_type_str)
        except ValueError:
            # Fallback mapping if AI gets creative
            if "email" in action_type_str.lower():
                suggested_action = ActionType.SEND_EMAIL
            elif "calendar" in action_type_str.lower() or "schedule" in action_type_str.lower():
                suggested_action = ActionType.CREATE_CALENDAR_INVITE
            elif "note" in action_type_str.lower() or "obsidian" in action_type_str.lower():
                suggested_action = ActionType.ADD_TO_OBSIDIAN
        
        description = item.get("description")
        assignee = item.get("assignee")
        if assignee and assignee.lower() != "me":
            description = f"[{assignee}] {description}"

        action_item = ActionItem(
            meeting_id=meeting.id,
            description=description,
            suggested_action=suggested_action,
            is_completed=False
        )
        session.add(action_item)
        
    session.commit()
    # Re-fetch meeting with fresh action items
    statement = select(Meeting).options(selectinload(Meeting.action_items)).where(Meeting.id == meeting.id)
    meeting = session.exec(statement).first()
    
    return meeting