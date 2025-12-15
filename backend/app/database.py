from sqlmodel import SQLModel, create_engine, Session
from .config import settings

# Handle SQLite specific configuration
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

# Create the database engine
engine = create_engine(settings.DATABASE_URL, echo=True, connect_args=connect_args)

def init_db():
    """
    Create the database tables based on the SQLModel metadata.
    This should be called on application startup.
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency to provide a database session to API endpoints.
    Yields a session and closes it after the request is finished.
    """
    with Session(engine) as session:
        yield session