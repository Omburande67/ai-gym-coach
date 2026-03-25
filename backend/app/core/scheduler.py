import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.user import User, NotificationPreferences, WorkoutStreak

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def check_missed_workouts():
    """Check for users who missed workouts and send reminders."""
    logger.info("Checking for missed workouts...")
    async with AsyncSessionLocal() as db:
        try:
            # Logic: Find users who haven't worked out in > 2 days
            # and have missed workout reminders enabled
            # Note: This is a simplified check.
            pass  
            # In real implementation:
            # result = await db.execute(select(User).join(NotificationPreferences).where(...))
            # for user in result.scalars():
            #    send_email(user.email, "We miss you! Come back and workout!")
        except Exception as e:
            logger.error(f"Error checking missed workouts: {e}")

async def send_scheduled_reminders():
    """Send daily workout reminders based on user preferences."""
    logger.info("Sending scheduled reminders...")
    async with AsyncSessionLocal() as db:
        try:
            # Logic: Find users whose daily_reminder_time is close to now
            now = datetime.now()
            current_time_str = now.strftime("%H:%M")
            # Query users with matching reminder time
            pass
        except Exception as e:
            logger.error(f"Error sending scheduled reminders: {e}")

def start_scheduler():
    """Start the scheduler."""
    # Add jobs
    scheduler.add_job(
        check_missed_workouts,
        IntervalTrigger(hours=4),  # Check every 4 hours
        id="missed_workouts",
        replace_existing=True,
    )
    scheduler.add_job(
        send_scheduled_reminders,
        IntervalTrigger(minutes=15), # Check every 15 mins
        id="scheduled_reminders",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info("Scheduler started.")

def shutdown_scheduler():
    """Shutdown the scheduler."""
    scheduler.shutdown()
    logger.info("Scheduler shutdown.")
