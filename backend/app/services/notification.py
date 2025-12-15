from typing import List
from ..models import User, Meeting, ActionItem
from datetime import datetime

class NotificationService:
    def send_daily_brief(self, user: User, meetings: List[Meeting]):
        """
        Simulates sending a morning Daily Brief email.
        """
        print(f"--- [EMAIL] Sending Daily Brief to {user.email} ---")
        print(f"Subject: Your Daily Brief for {datetime.now().strftime('%Y-%m-%d')}")
        print("Body:")
        print(f"Good morning {user.name or 'there'}!")
        print(f"You have {len(meetings)} meetings today:")
        for meeting in meetings:
            print(f" - {meeting.time_str if hasattr(meeting, 'time_str') else meeting.start_time}: {meeting.title}")
        print("---------------------------------------------------")
        return True

    def send_unresolved_reminders(self, user: User, pending_items: List[ActionItem]):
        """
        Simulates sending reminders for unresolved items.
        """
        if not pending_items:
            return False
            
        print(f"--- [EMAIL] Sending Reminder to {user.email} ---")
        print("Subject: You have pending action items")
        print("Body:")
        print("Don't forget to complete these tasks:")
        for item in pending_items:
            print(f" - {item.description} (from meeting ID {item.meeting_id})")
        print("------------------------------------------------")
        return True