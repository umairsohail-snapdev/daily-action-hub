from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional
from pydantic import BaseModel, EmailStr
import requests
import json
import urllib.parse

from fastapi.responses import RedirectResponse
from ..database import get_session
from ..models import User
from ..config import settings
from ..auth_utils import create_access_token
from ..auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Schemas ---
class GoogleAuthRequest(BaseModel):
    token: str # Google Access Token

class Token(BaseModel):
    access_token: str
    token_type: str

class SettingsUpdateRequest(BaseModel):
    integrations: dict
    notifications: dict

class NotionSettingsRequest(BaseModel):
    api_key: str
    database_id: str
 
# --- Endpoints ---

@router.post("/google", response_model=Token)
def google_auth(request: GoogleAuthRequest, session: Session = Depends(get_session)):
    """
    Verifies Google Access Token and creates/updates user.
    Returns app's JWT token.
    """
    token = request.token
    try:
        # Verify access token by fetching user info from Google
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Google token")
            
        user_info = response.json()
        email = user_info.get('email')
        google_sub = user_info.get('sub')
        name = user_info.get('name')
        picture = user_info.get('picture')
        
        if not email:
             raise HTTPException(status_code=400, detail="Google token does not contain email")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error validating Google token: {str(e)}")

    # Check if user exists by email
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        # Create new user
        user = User(
            email=email,
            google_sub=google_sub,
            name=name,
            picture=picture
        )
        session.add(user)
    else:
        # Update existing user with Google info if missing or changed
        user.google_sub = google_sub
        user.name = name or user.name
        user.picture = picture or user.picture
        session.add(user)
        
    session.commit()
    session.refresh(user)
    
    # Create app access token
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/login")
def login_with_google():
    """
    Redirects the user to Google's OAuth2 consent page.
    Using implicit flow for MVP simplicity (getting access token directly in URL fragment).
    """
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": f"{settings.FRONTEND_URL}/login", # Frontend handles the token extraction
        "response_type": "token", # Implicit flow: returns access_token in hash
        "scope": "openid email profile https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/gmail.compose",
        "state": "random_state_string",
        "prompt": "consent"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

@router.get("/settings")
def get_user_settings(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user settings.
    """
    return {
        "integrations": json.loads(current_user.integrations_config) if current_user.integrations_config else {},
        "notifications": json.loads(current_user.notification_preferences) if current_user.notification_preferences else {}
    }

@router.post("/settings")
def update_user_settings(
    request: SettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update user settings.
    """
    current_user.integrations_config = json.dumps(request.integrations)
    current_user.notification_preferences = json.dumps(request.notifications)
    
    session.add(current_user)
    session.commit()
    
    return {"message": "Settings updated successfully"}

# --- Notion Developer API Endpoints ---

@router.post("/notion/save_credentials")
def save_notion_credentials(
    request: NotionSettingsRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Saves Notion developer API key and database ID for a user.
    """
    print(f"Saving Notion credentials for user {current_user.id}: API Key: {request.api_key}, DB ID: {request.database_id}")
    current_user.notion_api_key = request.api_key
    current_user.notion_database_id = request.database_id
    
    # Update integrations config to show Notion as connected
    integrations = json.loads(current_user.integrations_config or "{}")
    integrations["Notion"] = True # Changed from "Notion / Granola"
    current_user.integrations_config = json.dumps(integrations)
    
    session.add(current_user)
    session.commit()
    
    return {"message": "Notion credentials saved successfully"}