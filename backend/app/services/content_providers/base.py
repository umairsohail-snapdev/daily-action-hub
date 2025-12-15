from abc import ABC, abstractmethod
from typing import Optional

class ContentProvider(ABC):
    @abstractmethod
    def fetch_content(self, title: str, date: str) -> Optional[str]:
        """
        Fetches the content (transcript/notes) for a meeting.
        
        Args:
            title: The title of the meeting from Google Calendar
            date: The date of the meeting (ISO format YYYY-MM-DD)
            
        Returns:
            String content of the notes/transcript if found, None otherwise.
        """
        pass