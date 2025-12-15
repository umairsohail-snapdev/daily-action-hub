import os
from notion_client import Client
from dotenv import load_dotenv

# Load your keys
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID").strip()

# Initialize
notion = Client(auth=NOTION_API_KEY)

print(f"Inspecting Database: {NOTION_DATABASE_ID}...\n")

try:
    response = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)
    
    print("--- YOUR COLUMN NAMES ---")
    found_title = False
    
    if "properties" in response:
        for prop_name, prop_data in response["properties"].items():
            prop_type = prop_data['type']
            print(f"• Name: '{prop_name}'  (Type: {prop_type})")
            
            if prop_type == 'title':
                print(f"  ✅ YES! This is your Title column.")
                print(f"  👉 USE THIS IN YOUR CODE: '{prop_name}'")
                found_title = True
    else:
        print("No properties found in response.")

    if not found_title:
        print("\n❌ Error: No 'Title' column found. This is very strange for a database.")

except Exception as e:
    print(f"❌ Error: {e}")