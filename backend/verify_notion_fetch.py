import os
import requests
import json
from dotenv import load_dotenv

# Load your keys
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "").strip()

print(f"Testing Fetch with:")
print(f"API Key: {NOTION_API_KEY[:4]}...")
print(f"Database ID: '{DATABASE_ID}'")

# Simulate Meeting
meeting_title = "Architecture Review"
print(f"\nSearching for notes with title: '{meeting_title}'")

url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}
payload = {
    "filter": {
        "property": "Task Name", # We confirmed this property name
        "title": {
            "contains": meeting_title
        }
    }
}

try:
    # 1. Query Database
    print(f"Querying: {url}")
    r = requests.post(url, json=payload, headers=headers)
    print(f"Status: {r.status_code}")
    
    if r.status_code != 200:
        print(f"Error: {r.text}")
        exit(1)
        
    data = r.json()
    results = data.get("results", [])
    print(f"Found {len(results)} pages.")
    
    if not results:
        print("No matching notes found.")
        exit(0)
        
    page_id = results[0]["id"]
    print(f"Fetching content for Page ID: {page_id}")
    
    # 2. Fetch Blocks
    blocks_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    r_blocks = requests.get(blocks_url, headers=headers)
    
    if r_blocks.status_code != 200:
        print(f"Error fetching blocks: {r_blocks.text}")
        exit(1)
        
    blocks_data = r_blocks.json()
    
    # 3. Extract Text
    print("\n--- Extracted Notes ---")
    text_content = []
    for block in blocks_data.get("results", []):
        type_ = block.get("type")
        text_parts = []
        
        if type_ in block:
            rich_text = block[type_].get("rich_text", [])
            for t in rich_text:
                text_parts.append(t.get("plain_text", ""))
        
        if text_parts:
            line = "".join(text_parts)
            if type_ in ["heading_1", "heading_2", "heading_3"]:
                print(f"\n# {line}")
            elif type_ == "bulleted_list_item":
                print(f"- {line}")
            elif type_ == "numbered_list_item":
                print(f"1. {line}")
            else:
                print(line)
            
            text_content.append(line)

except Exception as e:
    print(f"Exception: {e}")