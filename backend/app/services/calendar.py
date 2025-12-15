from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Optional
from ..models import Meeting, MeetingType
import re

class CalendarService:
    def __init__(self, token: str):
        # We assume the token passed is a valid access token
        # For offline access, we would need to construct Credentials with refresh_token, etc.
        self.creds = Credentials(token=token)
        self.service = build('calendar', 'v3', credentials=self.creds)

    def fetch_todays_meetings(self) -> List[Meeting]:
        """
        Fetches meetings for the current day from the primary calendar.
        """
        now = datetime.utcnow()
        # Start of day (00:00:00)
        time_min = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
        # End of day (23:59:59)
        time_max = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'

        events_result = self.service.events().list(
            calendarId='primary', 
            timeMin=time_min, 
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        meetings = []

        for event in events:
            # Skip cancelled events
            if event.get('status') == 'cancelled':
                continue
            
            # Additional check: sometimes 'cancelled' events don't have 'start'
            if 'start' not in event:
                continue
                
            # Parse start and end times
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Simple logic to determine if it's an online meeting
            # Check for hangoutLink or conferenceData or common video conference patterns in location/description
            is_online = False
            if 'hangoutLink' in event or 'conferenceData' in event:
                is_online = True
            elif event.get('location') and re.search(r'(zoom|teams|meet|webex)', event['location'], re.IGNORECASE):
                is_online = True
            elif event.get('description') and re.search(r'(zoom|teams|meet|webex)', event['description'], re.IGNORECASE):
                is_online = True
            
            # Determine Meeting Type
            # For now, if it's online, we assume it might be recorded or not. 
            # The PRD says:
            # - Online: Link detected
            # - Offline: Physical location or no link
            
            meeting_type = MeetingType.ONLINE if is_online else MeetingType.OFFLINE
            
            # Participants
            attendees = event.get('attendees', [])
            participants = [a.get('email') for a in attendees if a.get('email')]

            meeting = Meeting(
                google_event_id=event['id'],
                title=event.get('summary', 'No Title'),
                start_time=datetime.fromisoformat(start.replace('Z', '+00:00')),
                end_time=datetime.fromisoformat(end.replace('Z', '+00:00')),
                participants=participants,
                type=meeting_type,
                summary=event.get('description', ''), # Initial summary is the description
                user_id=0 # Placeholder, needs to be set by the caller
            )
            meetings.append(meeting)

        return meetings