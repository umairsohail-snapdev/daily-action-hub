import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion_api_key = os.getenv("NOTION_API_KEY", "").strip()
database_id = os.getenv("NOTION_DATABASE_ID", "").strip()

print(f"API Key: {notion_api_key[:4]}...")
print(f"Database ID: '{database_id}'")

client = Client(auth=notion_api_key)

try:
    print("Fetching database info...")
    db_info = client.databases.retrieve(database_id=database_id)
    
    print("\n--- Database Info ---")
    print(json.dumps(db_info, indent=2))
    
    properties = db_info.get("properties", {})
    print("\n--- Properties ---")
    found_title = False
    for name, prop in properties.items():
        print(f"Name: '{name}', Type: {prop['type']}")
        if prop['type'] == 'title':
            print(f"  -> FOUND TITLE PROPERTY: '{name}'")
            found_title = True
            
    if not found_title:
        print("  -> NO TITLE PROPERTY FOUND!")

except Exception as e:
    print(f"Error: {e}")