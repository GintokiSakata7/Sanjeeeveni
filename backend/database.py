"""
AERO SQLModel Database Engine Configuration
Connects natively to PostgreSQL / Supabase using pure Python SQLModel.
"""

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

# Get PostgreSQL Connection String from .env
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Fix postgresql:// prefix if using older driver scheme
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create SQLModel Engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

def create_db_and_tables():
    """Initializes all SQLModel database tables in PostgreSQL / Supabase"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """FastAPI Dependency for database sessions"""
    with Session(engine) as session:
        yield session
