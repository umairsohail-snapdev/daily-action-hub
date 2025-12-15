import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion_api_key = os.getenv("NOTION_API_KEY", "").strip()
database_id = os.getenv("NOTION_DATABASE_ID", "").strip()

print(f"API Key: {notion_api_key[:4]}...")
print(f"Database ID: {database_id}")

client = Client(auth=notion_api_key)

try:
    print("Testing client.databases.retrieve...")
    db_info = client.databases.retrieve(database_id=database_id)
    print("Retrieve success!")
    title_prop_name = "Name"
    
    print("Testing client.request with /query...")
    response = client.request(
        path=f"databases/{database_id}/query",
        method="POST",
        body={
            "filter": {
                "property": title_prop_name,
                "title": {
                    "contains": "Architecture"
                }
            }
        }
    )
    print("Request success!")
    print(response)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()