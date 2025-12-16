from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum
from sqlalchemy import Column, String, JSON

class MeetingType(str, Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"
    UNRECORDED = "Unrecorded"

class ActionType(str, Enum):
    SEND_EMAIL = "Send Email"
    CREATE_CALENDAR_INVITE = "Create Calendar Invite"
    CREATE_TASK = "Create Task"
    ADD_TO_OBSIDIAN = "Add to Obsidian"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: Optional[str] = None
    google_sub: Optional[str] = Field(default=None, index=True)
    name: Optional[str] = None
    picture: Optional[str] = None
    google_refresh_token: Optional[str] = None
    google_token_expiry: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Settings
    integrations_config: Optional[str] = Field(default="{}") # JSON string for enabled integrations
    notification_preferences: Optional[str] = Field(default='{"dailyBrief": true, "unresolvedReminders": false}') # JSON string
    
    # OAuth Tokens
    
    meetings: List["Meeting"] = Relationship(back_populates="user")

class Meeting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    google_event_id: str = Field(index=True)
    title: str
    start_time: datetime
    end_time: datetime
    # Storing participants as a list of strings using JSON (compatible with SQLite)
    participants: List[str] = Field(default=[], sa_column=Column(JSON))
    type: MeetingType
    summary: Optional[str] = None
    
    user: User = Relationship(back_populates="meetings")
    action_items: List["ActionItem"] = Relationship(back_populates="meeting")

class ActionItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    meeting_id: int = Field(foreign_key="meeting.id")
    description: str
    is_completed: bool = False
    suggested_action: ActionType
    
    meeting: Meeting = Relationship(back_populates="action_items")

class ActionItemRead(SQLModel):
    id: int
    meeting_id: int
    description: str
    is_completed: bool
    suggested_action: ActionType

class MeetingRead(SQLModel):
    id: int
    user_id: int
    google_event_id: str
    title: str
    start_time: datetime
    end_time: datetime
    participants: List[str]
    type: MeetingType
    summary: Optional[str] = None
    action_items: List[ActionItemRead] = []