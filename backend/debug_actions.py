import os
import sys
from app.models import ActionType
from app.services.actions.factory import ActionExecutorFactory
from app.services.actions.calendar import CalendarExecutor
from app.services.actions.notion import NotionExecutor
from app.services.actions.gmail import GmailExecutor

# Mock data
mock_action_data = {
    "description": "Test action item",
    "meeting_title": "Test Meeting",
    "meeting_start_time": "2024-01-01T10:00:00Z"
}

def test_action_types():
    print("\n--- Testing Action Types ---")
    types = [
        "Send Email",
        "Create Calendar Invite",
        "Create Task",
        "Add to Obsidian"
    ]
    for t in types:
        try:
            at = ActionType(t)
            print(f"'{t}' -> {at}")
        except ValueError as e:
            print(f"ERROR: '{t}' failed to map: {e}")

def test_executors():
    print("\n--- Testing Executors ---")
    
    # 1. Calendar
    print("\n[Calendar]")
    try:
        executor = ActionExecutorFactory.get_executor(ActionType.CREATE_CALENDAR_INVITE)
        result = executor.execute(mock_action_data)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Calendar Failed: {e}")

    # 2. Notion
    print("\n[Notion]")
    try:
        # Check env vars first
        print(f"NOTION_API_KEY set: {'Yes' if os.getenv('NOTION_API_KEY') else 'No'}")
        print(f"NOTION_DATABASE_ID set: {'Yes' if os.getenv('NOTION_DATABASE_ID') else 'No'}")
        
        executor = ActionExecutorFactory.get_executor(ActionType.CREATE_TASK)
        # We expect this might fail if no real keys, but we want to see HOW it fails
        result = executor.execute(mock_action_data)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Notion Failed: {e}")

    # 3. Gmail
    print("\n[Gmail]")
    try:
        executor = ActionExecutorFactory.get_executor(ActionType.SEND_EMAIL)
        # Pass a dummy token
        result = executor.execute(mock_action_data, user_token="dummy_token")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Gmail Failed: {e}")

if __name__ == "__main__":
    # Load env vars manually for script since uvicorn isn't loading them here
    from dotenv import load_dotenv
    load_dotenv()
    
    test_action_types()
    test_executors()