import sys
import os
from dotenv import load_dotenv

# Load .env file explicitly
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai import AIService

def test_ai_service():
    print("Testing AIService with Groq...")
    
    service = AIService()
    
    title = "Weekly Team Sync"
    participants = ["alice@example.com", "bob@example.com"]
    content = """
    Alice: Hi everyone, let's start. Bob, did you finish the report?
    Bob: Yes, I sent it yesterday.
    Alice: Great. I need you to also update the slide deck for Friday.
    Bob: Sure, I'll do that by tomorrow.
    Alice: Also, we need to schedule a meeting with the marketing team.
    Bob: I'll send an invite for that.
    """
    
    print("\n--- Sending request to Groq ---")
    try:
        result = service.process_meeting(title, content, participants)
        print("\n--- Result received ---")
        print("Summary:", result.get("summary"))
        print("Action Items:")
        for item in result.get("action_items", []):
            print(f"- [{item.get('suggested_action')}] {item.get('description')}")
            
        print("\n✅ AIService Test Passed!")
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")

if __name__ == "__main__":
    test_ai_service()