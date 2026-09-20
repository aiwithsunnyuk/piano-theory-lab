import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# 1. Dynamically get the absolute path to the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "piano.db")

# 2. Use the absolute path for the SQLite connection
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Creates all tables in the database if they don't already exist."""
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")