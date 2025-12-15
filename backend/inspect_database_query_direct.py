import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID").strip()

print(f"API Key: {NOTION_API_KEY[:4]}...")
print(f"Database ID: {DATABASE_ID}")

url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}
# Empty payload to fetch any pages
payload = {
    "page_size": 1
}

print(f"Querying URL: {url}")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if not results:
            print("No pages found in this database.")
        else:
            page = results[0]
            print("\n--- Page Properties ---")
            props = page.get("properties", {})
            found_title = False
            for name, prop in props.items():
                print(f"Property: '{name}', Type: '{prop['type']}'")
                if prop['type'] == 'title':
                    print(f"  >>> FOUND TITLE PROPERTY: '{name}' <<<")
                    found_title = True
            
            if not found_title:
                print("No title property found on the page object!")
    else:
        print("Error Response:")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")