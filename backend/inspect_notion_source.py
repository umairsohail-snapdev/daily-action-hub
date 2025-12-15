import notion_client
import inspect
from notion_client import Client

client = Client(auth="test")
print(f"Package file: {notion_client.__file__}")
print(f"DatabasesEndpoint file: {inspect.getfile(client.databases.__class__)}")

# Read the file content of DatabasesEndpoint definition
file_path = inspect.getfile(client.databases.__class__)
with open(file_path, 'r') as f:
    content = f.read()
    print(f"--- Content of {file_path} ---")
    # Print the class definition part
    start = content.find("class DatabasesEndpoint")
    print(content[start:start+1000]) 