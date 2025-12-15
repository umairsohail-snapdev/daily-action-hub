from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from pydantic import BaseModel
from ..models import ActionType

from ..database import get_session
from ..models import User, Meeting, ActionItem
from ..auth import get_current_user
from ..services.actions.factory import ActionExecutorFactory
from typing import Dict, Any

router = APIRouter(prefix="/actions", tags=["actions"])

class UpdateActionItemRequest(BaseModel):
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    suggested_action: Optional[ActionType] = None

class CreateActionItemRequest(BaseModel):
    meeting_id: int
    description: str
    suggested_action: ActionType = ActionType.CREATE_TASK

@router.post("/", status_code=201)
def create_action_item(
    request: CreateActionItemRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new manual action item for a meeting.
    """
    # Verify meeting ownership
    meeting = session.get(Meeting, request.meeting_id)
    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Meeting not found")

    action_item = ActionItem(
        meeting_id=request.meeting_id,
        description=request.description,
        suggested_action=request.suggested_action,
        is_completed=False
    )
    session.add(action_item)
    session.commit()
    session.refresh(action_item)
    return action_item

@router.patch("/{action_id}")
def update_action_item(
    action_id: int,
    request: UpdateActionItemRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update an action item's status or details.
    """
    # Join with Meeting to verify user ownership
    statement = select(ActionItem, Meeting).join(Meeting).where(
        ActionItem.id == action_id,
        Meeting.user_id == current_user.id
    )
    result = session.exec(statement).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Action item not found")
        
    action_item, _ = result
    
    if request.description is not None:
        action_item.description = request.description
    if request.is_completed is not None:
        action_item.is_completed = request.is_completed
    if request.suggested_action is not None:
        action_item.suggested_action = request.suggested_action
        
    session.add(action_item)
    session.commit()
    session.refresh(action_item)
    
    return action_item

class ExecuteActionRequest(BaseModel):
    user_token: Optional[str] = None
    params: Dict[str, Any] = {}

@router.post("/{action_id}/execute")
def execute_action(
    action_id: int,
    request: ExecuteActionRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Execute an action item using the appropriate service.
    """
    # Verify action ownership via Meeting
    statement = select(ActionItem, Meeting).join(Meeting).where(
        ActionItem.id == action_id,
        Meeting.user_id == current_user.id
    )
    result = session.exec(statement).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Action item not found")
        
    action_item, meeting = result
    
    # Determine the action type to execute: prefer the one passed in params (user selection), fallback to stored
    action_type_str = request.params.get("action_type")
    action_to_execute = action_item.suggested_action
    
    if action_type_str:
        try:
            # Try to match the string to an ActionType enum
            # The frontend sends "Send Email", "Create Task", etc.
            action_to_execute = ActionType(action_type_str)
        except ValueError:
            print(f"Invalid action type passed: {action_type_str}, falling back to stored {action_item.suggested_action}")

    print(f"Executing Action Type: {action_to_execute} (Stored: {action_item.suggested_action})")

    def parse_meeting_time(text: str) -> Optional[str]:
        """
        Simple helper to parse dates.
        Returns Google Calendar format dates=YYYYMMDDTHHMMSSZ/YYYYMMDDTHHMMSSZ
        """
        from datetime import datetime, timedelta
        import re

        text = text.lower()
        now = datetime.utcnow()
        start_dt = None

        if 'tomorrow' in text:
            start_dt = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        elif 'next week' in text:
            start_dt = (now + timedelta(days=7)).replace(hour=10, minute=0, second=0, microsecond=0)
        elif 'next friday' in text:
             # Find next friday
             days_ahead = 4 - now.weekday()
             if days_ahead <= 0: # Target day already happened this week
                 days_ahead += 7
             start_dt = (now + timedelta(days=days_ahead)).replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Add basic time parsing like "at 2pm"
        time_match = re.search(r'at (\d+)(?::(\d+))?\s*(am|pm)?', text)
        if time_match:
             hour = int(time_match.group(1))
             minute = int(time_match.group(2) or 0)
             meridiem = time_match.group(3)
             
             if meridiem == 'pm' and hour < 12:
                 hour += 12
             elif meridiem == 'am' and hour == 12:
                 hour = 0
             
             if not start_dt:
                 start_dt = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
             else:
                 start_dt = start_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if not start_dt:
             # Default to tomorrow 10am if no date keyword found
             start_dt = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        
        end_dt = start_dt + timedelta(hours=1)
        
        fmt = "%Y%m%dT%H%M%SZ"
        return f"{start_dt.strftime(fmt)}/{end_dt.strftime(fmt)}"

    try:
        executor = ActionExecutorFactory.get_executor(action_to_execute)
        
        # Prepare action data
        # We merge the description/action item details with any params sent from frontend
        action_data = {
            "description": action_item.description,
            "meeting_title": meeting.title,
            "meeting_participants": meeting.participants,
            "meeting_start_time": meeting.start_time,
            **request.params
        }
        
        # Basic mapping logic if specific fields are needed by executors that aren't in params
        if action_to_execute == ActionType.SEND_EMAIL:
            if "body" not in action_data:
                action_data["body"] = action_item.description
            if "subject" not in action_data:
                action_data["subject"] = f"Follow up: {meeting.title}"
        elif action_to_execute == ActionType.CREATE_CALENDAR_INVITE:
             if "summary" not in action_data:
                 action_data["summary"] = action_item.description
             
             # Calculate dates
             dates = parse_meeting_time(action_item.description)
             if dates:
                 action_data["dates"] = dates
            
        try:
            # Determine appropriate token based on action type
            execution_token = request.user_token
            if action_to_execute in [ActionType.CREATE_TASK, ActionType.ADD_TO_OBSIDIAN]:
                 # Use stored Notion token if available
                 if current_user.notion_access_token:
                     execution_token = current_user.notion_access_token

            result = executor.execute(action_data, user_token=execution_token)
        except Exception as e:
            print(f"Executor failed: {e}")
            if "AuthError" in str(e):
                raise HTTPException(status_code=401, detail="Google authentication failed. Please re-login.")
            raise HTTPException(status_code=500, detail=f"Executor failed: {str(e)}")
        
        if result:
            # If result is a dict (like from Gmail), it might contain a link
            response_data = {"message": "Action executed successfully", "status": "success"}
            if isinstance(result, dict):
                response_data.update(result)

            action_item.is_completed = True
            session.add(action_item)
            session.commit()
            return response_data
        else:
            print("Executor returned False/None indicating failure")
            raise HTTPException(status_code=500, detail="Action execution failed (Executor returned False)")
            
    except ValueError as e:
        print(f"ValueError in execute_action: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error executing action: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")