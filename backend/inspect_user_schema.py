from sqlalchemy import create_engine, text, inspect
from app.config import settings
import os

# Ensure we use the exact same path logic
db_url = settings.DATABASE_URL
print(f"Connecting to: {db_url}")
print(f"Current working directory: {os.getcwd()}")

engine = create_engine(db_url)

def inspect_schema():
    inspector = inspect(engine)
    columns = inspector.get_columns('user')
    print("\nColumns in 'user' table:")
    found_notion = False
    for column in columns:
        print(f"- {column['name']} ({column['type']})")
        if column['name'] == 'notion_access_token':
            found_notion = True
            
    if found_notion:
        print("\n✅ 'notion_access_token' FOUND.")
    else:
        print("\n❌ 'notion_access_token' NOT FOUND.")

if __name__ == "__main__":
    inspect_schema()