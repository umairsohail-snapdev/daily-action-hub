from sqlmodel import Session, select, create_engine, SQLModel
from app.models import User
from app.auth_utils import create_access_token
from app.config import settings
from datetime import datetime, timedelta

# Setup DB connection
engine = create_engine(settings.DATABASE_URL)
SQLModel.metadata.create_all(engine)

def create_test_user():
    with Session(engine) as session:
        # Check if test user exists
        statement = select(User).where(User.email == "test@example.com")
        user = session.exec(statement).first()
        
        if not user:
            print("Creating test user...")
            user = User(
                email="test@example.com",
                google_sub="test_sub_12345",
                name="Test User",
                picture="https://via.placeholder.com/150",
                created_at=datetime.utcnow()
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        else:
            print(f"Test user found: {user.email}")
            
        # Generate Token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        print(f"\nLOGIN_URL=http://localhost:5173/login?token={access_token}")

if __name__ == "__main__":
    create_test_user()