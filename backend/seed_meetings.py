import sys
import os

# Add the current directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select, create_engine, SQLModel
from app.models import User, Meeting, MeetingType, ActionItem, ActionType
from app.config import settings
from datetime import datetime, timedelta

# Setup DB connection
engine = create_engine(settings.DATABASE_URL)

def seed_meetings():
    with Session(engine) as session:
        # Get ALL users
        statement = select(User)
        users = session.exec(statement).all()
        
        if not users:
            print("No users found in the database. Please log in via the frontend first.")
            return

        print(f"Found {len(users)} users. Seeding meetings for all of them...")

        today = datetime.now()

        for user in users:
            print(f"Seeding for user: {user.email}")
            
            # 1. Project Sync Meeting
            start_time = today.replace(hour=10, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)
            
            meeting = Meeting(
                user_id=user.id,
                google_event_id=f"test_event_1_{user.id}",
                title="Project Sync",
                start_time=start_time,
                end_time=end_time,
                participants=["test@example.com", "colleague@example.com"],
                type=MeetingType.ONLINE,
                summary=""
            )
            session.add(meeting)
            session.commit()
            session.refresh(meeting)
            
            # Add an action item
            action_item = ActionItem(
                meeting_id=meeting.id,
                description="Send meeting minutes",
                is_completed=False,
                suggested_action=ActionType.SEND_EMAIL
            )
            session.add(action_item)
            
            # 2. Sales Call (Good for testing AI summary)
            meeting_sales = Meeting(
                user_id=user.id,
                google_event_id=f"test_event_2_{user.id}",
                title="Sales Call with Client X",
                start_time=today.replace(hour=14, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=15, minute=0, second=0, microsecond=0),
                participants=["test@example.com", "client@example.com"],
                type=MeetingType.ONLINE,
                summary=""
            )
            session.add(meeting_sales)
            session.commit()

            # 3. Offline Coffee Chat (for testing offline prompt)
            meeting_offline = Meeting(
                user_id=user.id,
                google_event_id=f"test_event_3_{user.id}",
                title="Coffee with Mentor",
                start_time=today.replace(hour=16, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=17, minute=0, second=0, microsecond=0),
                participants=["test@example.com", "mentor@example.com"],
                type=MeetingType.OFFLINE,
                summary="Met at Starbucks."
            )
            session.add(meeting_offline)
            session.commit()

        print("Meetings seeded successfully for all users!")

if __name__ == "__main__":
    seed_meetings()