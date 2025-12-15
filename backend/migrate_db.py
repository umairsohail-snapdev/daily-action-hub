from sqlalchemy import create_engine, text
from app.config import settings

# Setup DB connection
engine = create_engine(settings.DATABASE_URL)

def migrate():
    print("Migrating database...")
    with engine.connect() as connection:
        # 1. Add password_hash column
        try:
            connection.execute(text("ALTER TABLE user ADD COLUMN password_hash VARCHAR"))
            print("✅ Added 'password_hash' column to 'user' table.")
        except Exception as e:
            print(f"⚠️ Could not add 'password_hash' column (it might already exist): {e}")

        # 2. Add integrations_config column
        try:
            connection.execute(text("ALTER TABLE user ADD COLUMN integrations_config VARCHAR"))
            print("✅ Added 'integrations_config' column to 'user' table.")
        except Exception as e:
            print(f"⚠️ Could not add 'integrations_config' column (it might already exist): {e}")

        # 3. Add notification_preferences column
        try:
            connection.execute(text("ALTER TABLE user ADD COLUMN notification_preferences VARCHAR"))
            print("✅ Added 'notification_preferences' column to 'user' table.")
        except Exception as e:
            print(f"⚠️ Could not add 'notification_preferences' column (it might already exist): {e}")
            
        # 4. Add notion_access_token column
        try:
            connection.execute(text("ALTER TABLE user ADD COLUMN notion_access_token VARCHAR"))
            print("✅ Added 'notion_access_token' column to 'user' table.")
        except Exception as e:
            print(f"⚠️ Could not add 'notion_access_token' column (it might already exist): {e}")

        # 5. Add notion_bot_id column
        try:
            connection.execute(text("ALTER TABLE user ADD COLUMN notion_bot_id VARCHAR"))
            print("✅ Added 'notion_bot_id' column to 'user' table.")
        except Exception as e:
            print(f"⚠️ Could not add 'notion_bot_id' column (it might already exist): {e}")

    print("Migration attempt finished.")

if __name__ == "__main__":
    migrate()