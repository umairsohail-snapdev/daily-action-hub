import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

print(f"API Key: {NOTION_API_KEY[:4]}...{NOTION_API_KEY[-4:]}")
print(f"Database ID: {DATABASE_ID}")

url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}
payload = {
    "filter": {
        "property": "Name",
        "title": {
            "contains": "Architecture Review"
        }
    }
}

print(f"Testing URL: {url}")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")