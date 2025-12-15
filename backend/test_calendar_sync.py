import sys
import os
from dotenv import load_dotenv

# Load .env file explicitly
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.calendar import CalendarService
from app.config import settings

def test_calendar_sync():
    print("Testing CalendarService...")
    
    # NOTE: This test requires a valid Google Access Token to be passed.
    # Since we can't easily get a fresh user token here without the OAuth flow,
    # we'll mock the service or check if a token exists in env (unlikely for user token).
    
    # However, to check if the logic *inside* fetch_todays_meetings is correct regarding
    # date ranges and parsing, we can mock the google service.
    
    # For now, let's just instantiate it to see if imports and init work.
    try:
        # We pass a dummy token just to initialize the credentials object
        service = CalendarService(token="dummy_token")
        print("✅ CalendarService initialized successfully.")
        
        print("\n⚠️ Note: To fully test syncing, we need a valid user access token.")
        print("The real sync happens via the /dashboard/sync endpoint where the frontend sends the token.")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")

if __name__ == "__main__":
    test_calendar_sync()