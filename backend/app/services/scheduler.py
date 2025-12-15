from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select
from datetime import datetime, timedelta
import json

from ..database import engine
from ..models import User, Meeting, ActionItem
from .notification import NotificationService

scheduler = AsyncIOScheduler()

async def send_daily_briefs():
    """
    Job to send daily brief emails to users who have opted in.
    """
    print("--- [SCHEDULER] Running Daily Brief Job ---")
    
    with Session(engine) as session:
        # Fetch all users
        users = session.exec(select(User)).all()
        
        notification_service = NotificationService()
        
        for user in users:
            # Check preferences
            prefs = json.loads(user.notification_preferences or "{}")
            if not prefs.get("dailyBrief", True):
                continue
                
            # Get today's meetings (UTC window, but ideally user timezone aware)
            # For MVP, we use UTC "today"
            now = datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            meetings = session.exec(
                select(Meeting).where(
                    Meeting.user_id == user.id,
                    Meeting.start_time >= start_of_day,
                    Meeting.start_time <= end_of_day
                )
            ).all()
            
            if meetings:
                notification_service.send_daily_brief(user, meetings)
                
            # Also send reminders for unresolved items if enabled
            if prefs.get("unresolvedReminders", False):
                pending_items = session.exec(
                    select(ActionItem)
                    .join(Meeting)
                    .where(
                        Meeting.user_id == user.id,
                        ActionItem.is_completed == False
                    )
                ).all()
                
                if pending_items:
                    notification_service.send_unresolved_reminders(user, pending_items)

def start_scheduler():
    """
    Starts the scheduler with defined jobs.
    """
    # Schedule Daily Brief at 9:00 AM UTC (adjust as needed for timezone)
    scheduler.add_job(
        send_daily_briefs, 
        CronTrigger(hour=9, minute=0), 
        id="daily_brief",
        replace_existing=True
    )
    
    scheduler.start()
    print("--- [SCHEDULER] Started ---")

def stop_scheduler():
    scheduler.shutdown()
    print("--- [SCHEDULER] Stopped ---")