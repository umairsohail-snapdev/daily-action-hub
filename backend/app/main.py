from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .config import settings
from .routers import dashboard, meetings, actions, auth, notifications
from .services.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database
    print(f"--- CONFIG: FRONTEND_URL is set to: {settings.FRONTEND_URL} ---")
    init_db()
    # Startup: Initialize the scheduler
    start_scheduler()
    yield
    # Shutdown logic
    stop_scheduler()

app = FastAPI(title="Daily Action Hub API", lifespan=lifespan)

# Configure CORS to allow requests from the frontend
origins = [
    "http://localhost:5137",
    "http://localhost:3000",
    "https://daily-action-frontend.onrender.com",
    settings.FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(meetings.router)
app.include_router(actions.router)
app.include_router(auth.router)
app.include_router(notifications.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Daily Action Hub API"}