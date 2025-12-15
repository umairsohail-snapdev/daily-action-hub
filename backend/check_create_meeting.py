from sqlmodel import Session, select
from app.database import engine
from app.models import Meeting, User
from datetime import datetime, timedelta

def check_create_meeting():
    with Session(engine) as session:
        # Get the test user (assuming ID 2 based on previous logs)
        user = session.get(User, 2)
        if not user:
            print("User ID 2 not found. Please check existing users.")
            return

        # Check for "Architecture Review" meeting
        statement = select(Meeting).where(Meeting.user_id == user.id, Meeting.title == "Architecture Review")
        meeting = session.exec(statement).first()

        if meeting:
            print(f"Meeting found! ID: {meeting.id}")
            print(f"Title: {meeting.title}")
        else:
            print("Meeting not found. Creating it...")
            now = datetime.utcnow()
            meeting = Meeting(
                user_id=user.id,
                title="Architecture Review",
                start_time=now,
                end_time=now + timedelta(hours=1),
                participants=[],
                type="OFFLINE",
                summary=""
            )
            session.add(meeting)
            session.commit()
            session.refresh(meeting)
            print(f"Meeting created! ID: {meeting.id}")

if __name__ == "__main__":
    check_create_meeting()