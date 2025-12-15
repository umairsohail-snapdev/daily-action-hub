from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
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
from ..auth_utils import get_password_hash, verify_password, create_access_token
from ..auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Schemas ---
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class GoogleAuthRequest(BaseModel):
    token: str # Google Access Token

class Token(BaseModel):
    access_token: str
    token_type: str

class SettingsUpdateRequest(BaseModel):
    integrations: dict
    notifications: dict

# --- Endpoints ---

@router.post("/signup", response_model=Token)
def signup(user_data: UserSignup, session: Session = Depends(get_session)):
    # Check if user exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    # OAuth2PasswordRequestForm expects 'username' and 'password'
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()
    
    if not user or not user.password_hash or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

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

# --- Notion OAuth Endpoints ---

@router.get("/notion")
def login_with_notion():
    """
    Redirects the user to Notion's OAuth2 consent page.
    """
    base_url = "https://api.notion.com/v1/oauth/authorize"
    # Note: owner=user means the token is scoped to the user (Bot integration)
    params = {
        "client_id": settings.NOTION_CLIENT_ID,
        "redirect_uri": f"{settings.FRONTEND_URL}/settings", # Redirect back to settings
        "response_type": "code",
        "owner": "user"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

class NotionCallbackRequest(BaseModel):
    code: str

@router.post("/notion/callback")
def notion_callback(
    request: NotionCallbackRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Exchanges Notion code for access token.
    """
    code = request.code
    
    # Exchange code for token
    auth_string = f"{settings.NOTION_CLIENT_ID}:{settings.NOTION_CLIENT_SECRET}"
    import base64
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{settings.FRONTEND_URL}/settings"
    }
    
    try:
        response = requests.post("https://api.notion.com/v1/oauth/token", headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"Notion OAuth Error: {response.text}")
            raise HTTPException(status_code=400, detail="Failed to authenticate with Notion")
            
        data = response.json()
        access_token = data.get("access_token")
        bot_id = data.get("bot_id")
        
        # Save to user
        current_user.notion_access_token = access_token
        current_user.notion_bot_id = bot_id
        
        # Update integrations config to show Notion as connected
        integrations = json.loads(current_user.integrations_config or "{}")
        integrations["Notion / Granola"] = True
        current_user.integrations_config = json.dumps(integrations)
        
        session.add(current_user)
        session.commit()
        
        return {"message": "Notion connected successfully"}
        
    except Exception as e:
        print(f"Notion Callback Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))