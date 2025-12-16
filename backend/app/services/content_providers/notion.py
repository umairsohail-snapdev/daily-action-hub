import requests
from typing import Optional
from .base import ContentProvider
from datetime import datetime
from app.config import settings

class NotionProvider(ContentProvider):
    def fetch_content(self, user: 'User', meeting_title: str, meeting_date: str) -> Optional[str]:
        """
        Fetches content from a specific Notion database using a developer API key from environment settings.
        """
        if not settings.NOTION_API_KEY or not settings.NOTION_DATABASE_ID:
            print("Notion API key or Database ID not configured in environment settings.")
            return None

        api_key = settings.NOTION_API_KEY
        database_id = settings.NOTION_DATABASE_ID
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

        # Parse the meeting date to filter by day
        try:
            search_date = datetime.fromisoformat(meeting_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
        except ValueError:
            print(f"Invalid date format for Notion search: {meeting_date}")
            return None

        # Query the database
        query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
        
        # Filter: find pages created on the same day as the meeting AND matching the title
        payload = {
            "filter": {
                "and": [
                    {
                        "property": "Created time",
                        "date": {
                            "on_or_after": search_date,
                            "on_or_before": search_date
                        }
                    },
                    {
                        "property": "Task Name",
                        "title": {
                            "contains": meeting_title
                        }
                    }
                ]
            }
        }

        try:
            response = requests.post(query_url, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"Error querying Notion database: {response.text}")
                return None
            
            data = response.json()
            if not data.get("results"):
                print(f"No Notion page found for date: {search_date}")
                return None

            # For simplicity, we'll take the first result and fetch its content
            page_id = data["results"][0]["id"]
            return self._get_page_content(page_id, headers)

        except Exception as e:
            print(f"An exception occurred while fetching from Notion: {e}")
            return None

    def _get_page_content(self, page_id: str, headers: dict) -> Optional[str]:
        """Retrieves and concatenates all text blocks from a given page."""
        block_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        
        try:
            response = requests.get(block_url, headers=headers)
            if response.status_code != 200:
                print(f"Error fetching page content from Notion: {response.text}")
                return None
            
            blocks = response.json().get("results", [])
            
            full_text = ""
            for block in blocks:
                if "type" in block and block["type"] in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"]:
                    text_content = block[block["type"]]["rich_text"]
                    for text_part in text_content:
                        if text_part["type"] == "text":
                            full_text += text_part["text"]["content"] + "\n"
            
            return full_text if full_text else None

        except Exception as e:
            print(f"An exception occurred while getting page content: {e}")
            return None