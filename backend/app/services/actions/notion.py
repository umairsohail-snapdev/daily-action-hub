from typing import Any, Dict, Optional
from .base import ActionExecutor
from notion_client import Client
import os

class NotionExecutor(ActionExecutor):
    def execute(self, action_data: Dict[str, Any], user_token: Optional[str] = None) -> Any:
        """
        Creates a task page in a Notion database.
        """
        notion_api_key = os.getenv("NOTION_API_KEY")
        database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not notion_api_key or not database_id:
            from ...config import settings
            notion_api_key = notion_api_key or settings.NOTION_API_KEY
            database_id = database_id or settings.NOTION_DATABASE_ID
            
            if not notion_api_key or not database_id:
                 print("Notion keys missing in both env and settings.")
                 return {
                    "status": "error", 
                    "message": "Notion configuration missing"
                }

        # Check if we have a user token via context or params
        # In the future, this should be passed explicitly.
        # For now, we rely on the env vars as per MVP, but we can check if 'user_token' param is passed
        # (though typically that's the Google token in this architecture).
        
        # NOTE: To fully support OAuth, we'd need to fetch the User object using the 'user_token' (which is the app JWT in some contexts,
        # or the Google token in others).
        # Since 'execute_action' receives 'user_token' which is currently the Google Access Token, we can't look up the user easily
        # unless we have a mapping or pass the User ID.
        #
        # Ideally, `execute` would receive the `User` object directly.
        #
        # For this refactor, we will stick to ENV variables for stability, but this is where we'd inject:
        # notion_token = user.notion_access_token or notion_api_key
        
        # For now, default to the env var key as the fallback or primary
        # In a real user context, we would pull `user.notion_access_token` if available
        # But this Executor class doesn't currently receive the `user` object, only `user_token` (which is Google)
        # We will fix this in a future refactor by passing the full User context.
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