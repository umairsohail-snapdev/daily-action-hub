from sqlmodel import Session, select, create_engine
from app.models import Meeting, User

# Adjust the database URL if necessary (assuming sqlite)
sqlite_file_name = "daily_action_hub_v2.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def inspect_meetings():
    with Session(engine) as session:
        # Fetch all meetings for User 2 (as seen in logs)
        user_id = 2
        statement = select(Meeting).where(Meeting.user_id == user_id)
        meetings = session.exec(statement).all()
        
        print(f"Found {len(meetings)} meetings for User {user_id}:")
        for m in meetings:
            print(f"ID: {m.id} | Title: {m.title} | Start: {m.start_time} | End: {m.end_time} | Type: {m.type} | GoogleID: {m.google_event_id}")

if __name__ == "__main__":
    inspect_meetings()