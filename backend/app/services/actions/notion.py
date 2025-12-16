from typing import Any, Dict, Optional
from .base import ActionExecutor
from notion_client import Client
from app.config import settings

class NotionExecutor(ActionExecutor):
    def execute(self, action_data: Dict[str, Any], user_token: Optional[str] = None) -> Any:
        """
        Creates a task page in a Notion database.
        """
        notion_api_key = settings.NOTION_API_KEY
        database_id = settings.NOTION_DATABASE_ID
        
        if not notion_api_key or not database_id:
            return {
                "status": "error",
                "message": "Notion not configured. Please set API Key and Database ID in environment settings."
            }

        client = Client(auth=notion_api_key)
        
        description = action_data.get("description", "No description")
        meeting_title = action_data.get("meeting_title", "Unknown Meeting")
        
        try:
            print(f"Creating Notion page in DB: {database_id}...")
            
            new_page = client.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Task Name": {
                        "title": [
                            {
                                "text": {
                                    "content": description
                                }
                            }
                        ]
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Context from meeting: {meeting_title}"
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
            
            print(f"Notion page created: {new_page.get('url')}")
            return {
                "status": "success",
                "notionUrl": new_page.get("url")
            }
            
        except Exception as e:
            print(f"Notion API Error: {str(e)}")
            raise e