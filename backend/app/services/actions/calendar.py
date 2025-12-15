from typing import Any, Dict, Optional
from .base import ActionExecutor

class CalendarExecutor(ActionExecutor):
    def execute(self, action_data: Dict[str, Any], user_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates a Google Calendar render URL for scheduling.
        Returns the calendarUrl.
        """
        import urllib.parse

        # Map action item description to event title
        title = action_data.get("description", "New Meeting")
        
        # We don't have exact time, so we just provide a template link
        # Base URL for creating an event
        base_url = "https://calendar.google.com/calendar/render"
        
        # Get meeting context
        meeting_context = ""
        if "meeting_start_time" in action_data:
             meeting_context = f"Context from meeting on {action_data['meeting_start_time']}\n\n"
        
        details = f"{meeting_context}Task: {action_data.get('description', '')}"

        params = {
            "action": "TEMPLATE",
            "text": title,
            "details": details,
            # "dates": "..." # Optional: If we extracted dates, we could put them here in YYYYMMDDTHHMMSSZ/YYYYMMDDTHHMMSSZ format
        }
        
        calendar_url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        print(f"--- CALENDAR EXECUTOR ---")
        print(f"Generated URL: {calendar_url}")
        print("-------------------------")
        
        return {
            "success": True,
            "calendarUrl": calendar_url,
            "link": calendar_url # Standardize on 'link' for frontend handling
        }