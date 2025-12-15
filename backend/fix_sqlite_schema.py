from sqlalchemy import create_engine, text
from app.config import settings

# Setup DB connection
engine = create_engine(settings.DATABASE_URL)

def fix_schema():
    print("Attempting to fix SQLite schema (making google_sub nullable)...")
    
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            # 1. Disable foreign keys
            connection.execute(text("PRAGMA foreign_keys=OFF"))
            
            # 2. Create new table with desired schema (google_sub nullable)
            # We explicitly define the schema here to ensure it matches what we want
            connection.execute(text("""
                CREATE TABLE user_new (
                    id INTEGER NOT NULL, 
                    email VARCHAR NOT NULL, 
                    google_sub VARCHAR, 
                    name VARCHAR, 
                    picture VARCHAR, 
                    google_refresh_token VARCHAR, 
                    google_token_expiry DATETIME, 
                    created_at DATETIME NOT NULL, 
                    password_hash VARCHAR, 
                    integrations_config VARCHAR, 
                    notification_preferences VARCHAR, 
                    PRIMARY KEY (id)
                )
            """))
            
            # 3. Copy data from old table to new table
            # We select columns explicitly to avoid mismatch if columns order changed
            connection.execute(text("""
                INSERT INTO user_new (id, email, google_sub, name, picture, google_refresh_token, google_token_expiry, created_at, password_hash, integrations_config, notification_preferences)
                SELECT id, email, google_sub, name, picture, google_refresh_token, google_token_expiry, created_at, password_hash, integrations_config, notification_preferences
                FROM user
            """))
            
            # 4. Drop old table
            connection.execute(text("DROP TABLE user"))
            
            # 5. Rename new table to old table name
            connection.execute(text("ALTER TABLE user_new RENAME TO user"))
            
            # 6. Re-enable foreign keys
            connection.execute(text("PRAGMA foreign_keys=ON"))
            
            # 7. Re-create indices (optional but good practice)
            try:
                connection.execute(text("CREATE UNIQUE INDEX ix_user_email ON user (email)"))
                connection.execute(text("CREATE INDEX ix_user_google_sub ON user (google_sub)"))
            except Exception as index_error:
                print(f"Warning creating indices: {index_error}")
            
            trans.commit()
            print("✅ Schema fixed: 'google_sub' is now nullable.")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error fixing schema: {e}")
            raise e

if __name__ == "__main__":
    fix_schema()