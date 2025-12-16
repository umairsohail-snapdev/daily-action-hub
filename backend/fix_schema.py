import sqlite3
import json

# Configuration
DB_PATH = 'daily_action_hub_v2.db'
TABLE_NAME = 'user'
BACKUP_TABLE_NAME = 'user_backup'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def backup_data(conn):
    """Backs up existing data and returns it."""
    print(f"Backing up data from '{TABLE_NAME}'...")
    cursor = conn.cursor()
    
    # Check if the backup table exists and drop it
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {BACKUP_TABLE_NAME}")
        print(f"Dropped existing backup table '{BACKUP_TABLE_NAME}'.")
    except Exception as e:
        print(f"Could not drop backup table (this is likely fine): {e}")

    # Rename the current table to the backup name
    try:
        cursor.execute(f"ALTER TABLE {TABLE_NAME} RENAME TO {BACKUP_TABLE_NAME}")
        conn.commit()
        print(f"Renamed '{TABLE_NAME}' to '{BACKUP_TABLE_NAME}'.")
    except sqlite3.OperationalError:
        print(f"'{TABLE_NAME}' does not exist, skipping backup.")
        return None, None

    # Fetch all data from the backup
    cursor.execute(f"SELECT * FROM {BACKUP_TABLE_NAME}")
    data = cursor.fetchall()
    columns = [description for description in cursor.description]
    
    print(f"Backed up {len(data)} rows.")
    return columns, data

def create_new_table_from_model(conn):
    """
    Creates the new table structure using SQLModel's metadata.
    This function relies on the main application's models being importable.
    """
    print("Creating new table structure from SQLModel definitions...")
    # Import necessary components
    from app.database import engine
    from sqlmodel import SQLModel
    # Import all models to ensure they are registered with SQLModel's metadata
    import app.models

    try:
        # This will create tables if they don't exist, based on the current models.
        SQLModel.metadata.create_all(engine)
        print("Successfully created tables based on current models.")
    except Exception as e:
        print(f"Error creating tables with SQLModel: {e}")
        raise

def restore_data(conn, old_columns, data):
    """Restores data from the backup into the new table structure."""
    if not data:
        print("No data to restore.")
        return

    print("Restoring data...")
    cursor = conn.cursor()

    # Get new columns to map data correctly
    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    new_columns_info = cursor.fetchall()
    new_columns_names = [col for col in new_columns_info]
    
    print(f"Old columns: {[col for col in old_columns]}")
    print(f"New columns: {new_columns_names}")

    # Create a mapping from old column names to their index
    old_col_map = {name: i for i, (name, *_) in enumerate(old_columns)}

    for row in data:
        # Build the new row based on the new schema
        new_row_dict = {}
        for col_name in new_columns_names:
            if col_name in old_col_map:
                new_row_dict[col_name] = row[old_col_map[col_name]]
            else:
                # For new columns not in the old data, use a default value (NULL)
                new_row_dict[col_name] = None
        
        # Ensure the order of values matches the new column order
        ordered_values = [new_row_dict[col_name] for col_name in new_columns_names]
        
        placeholders = ', '.join(['?'] * len(new_columns_names))
        sql = f"INSERT INTO {TABLE_NAME} ({', '.join(new_columns_names)}) VALUES ({placeholders})"
        
        try:
            cursor.execute(sql, ordered_values)
        except Exception as e:
            print(f"Error inserting row: {ordered_values}")
            print(f"Exception: {e}")

    conn.commit()
    print(f"Successfully restored {len(data)} rows.")

def main():
    """Main migration function."""
    conn = get_db_connection()
    try:
        # Step 1: Backup existing data
        old_columns, data = backup_data(conn)
        
        # Step 2: Create the new table structure from the models
        # This needs to be done with the app's context
        create_new_table_from_model(conn)
        
        # Step 3: Restore the data if there was any
        if old_columns and data:
            restore_data(conn, [col for col in old_columns], data)
            
        # Step 4: Clean up the backup table
        print("Cleaning up backup table...")
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE {BACKUP_TABLE_NAME}")
        conn.commit()
        print("Migration complete!")

    except Exception as e:
        print(f"An error occurred during migration: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # A bit of a hack to ensure the app's models are importable
    import sys
    import os
    # Add the parent directory to the path to allow `from app.database import ...`
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    main()