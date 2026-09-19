from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Replace with your actual local PostgreSQL credentials
# Format: postgresql://username:password@localhost:5432/database_name
DATABASE_URL = "sqlite:///piano.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Creates all tables in the database if they don't already exist."""
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")