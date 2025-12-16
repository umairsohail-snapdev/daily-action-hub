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
    user_token: Optional[str] = None # For actions needing Google API, this is the Google Access Token
    params: Dict[str, Any] = {}

@router.post("/{action_id}/execute")
def execute_action(
    action_id: int,
    request: ExecuteActionRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify ownership
    statement = select(ActionItem).join(Meeting).where(
        ActionItem.id == action_id,
        Meeting.user_id == current_user.id
    )
    action_item = session.exec(statement).first()

    if not action_item:
        raise HTTPException(status_code=404, detail="Action item not found")

    # Prepare data for the executor
    action_data = {
        "description": action_item.description,
        "meeting_title": action_item.meeting.title,
        "participants": action_item.meeting.participants,
        "params": request.params
    }
    
    google_token = request.user_token

    try:
        executor = ActionExecutorFactory.get_executor(action_item.suggested_action)
        # Pass action_data and user_token as expected by the ActionExecutor interface
        result = executor.execute(action_data, google_token)
    except Exception as e:
        print(f"Executor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # Mark as completed
    action_item.is_completed = True
    session.add(action_item)
    session.commit()

    return result