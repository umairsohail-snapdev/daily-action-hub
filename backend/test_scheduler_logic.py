import asyncio
import os
from app.services.scheduler import send_daily_briefs
from app.database import init_db

# Ensure DB is initialized (useful if running against a fresh temp DB)
init_db()

async def main():
    print("Testing Daily Brief Job logic...")
    await send_daily_briefs()
    print("Job execution logic finished.")

if __name__ == "__main__":
    asyncio.run(main())