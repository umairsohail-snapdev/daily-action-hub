import sys
import os
from dotenv import load_dotenv

# Load .env file explicitly
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.calendar import CalendarService

def test_calendar_sync():
    print("\n--- Google Calendar Real Test ---")
    print("This script connects to your actual Google Calendar.")
    print("You need a valid OAuth Access Token.")
    print("If you have the frontend running, log in, open the Network tab, sync, and copy the token from the request header (X-Google-Access-Token).")
    print("Or obtain one from the Google OAuth Playground.")
    
    token = input("\nPaste your Google Access Token here: ").strip()
    
    if not token:
        print("❌ No token provided. Exiting.")
        return

    print("\nConnecting to Google Calendar...")
    try:
        service = CalendarService(token=token)
        meetings = service.fetch_todays_meetings()
        
        print(f"\n✅ Successfully fetched {len(meetings)} meetings for TODAY (UTC based):")
        
        if not meetings:
            print("No meetings found for today.")
            
        for m in meetings:
            print(f"\n📅 {m.title}")
            print(f"   Time: {m.start_time} - {m.end_time} (UTC)")
            print(f"   Type: {m.type}")
            print(f"   Participants: {', '.join(m.participants)}")
            print(f"   ID: {m.google_event_id}")

    except Exception as e:
        print(f"\n❌ Error fetching meetings: {e}")
        print("Please check if the token is valid and has the correct scopes (calendar.readonly).")

if __name__ == "__main__":
    test_calendar_sync()