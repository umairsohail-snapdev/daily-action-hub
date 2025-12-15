from groq import Groq
from ..config import settings
from ..models import ActionType
import json
from typing import List, Dict, Any

class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def process_meeting(self, meeting_title: str, meeting_content: str, participants: List[str]) -> Dict[str, Any]:
        """
        Analyzes meeting content to generate a summary and extract action items.
        Returns a dictionary with 'summary' and 'action_items'.
        """
        if not meeting_content:
            return {
                "summary": "No content available to analyze.",
                "action_items": []
            }

        prompt = f"""
        Analyze the following meeting transcript/notes:
        Title: {meeting_title}
        Participants: {", ".join(participants)}
        Content: {meeting_content}

        1. Provide a concise summary of the meeting.
        2. Extract explicit Next Steps. Return a JSON object with a key "action_items" containing a list. Each item must have:
           - "action_type": (One of: "Send Email", "Create Calendar Invite", "Create Task", "Add to Obsidian")
           - "description": (Clear summary of what to do)
           - "assignee": (Name of the person responsible, or "Me" if unclear)
        
        Return the result in JSON format:
        {{
            "summary": "string",
            "action_items": [
                {{
                    "action_type": "string (one of the options above)",
                    "description": "string",
                    "assignee": "string"
                }}
            ]
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes meetings and extracts actionable tasks. You must respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            if content:
                return json.loads(content)
            else:
                 return {"summary": "Error: Empty response from AI", "action_items": []}
                 
        except Exception as e:
            print(f"Error calling Groq: {e}")
            return {
                "summary": "Error processing meeting with AI.",
                "action_items": []
            }