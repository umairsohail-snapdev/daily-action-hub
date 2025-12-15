import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

notion_api_key = os.getenv("NOTION_API_KEY")
client = Client(auth=notion_api_key)

print(f"Client type: {type(client)}")
print(f"Databases type: {type(client.databases)}")
print("Databases attributes:")
print(dir(client.databases))

try:
    print("Has query method:", hasattr(client.databases, 'query'))
except Exception as e:
    print(f"Error checking attribute: {e}")