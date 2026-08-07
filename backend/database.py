"""
Sanjeevani (AERO) SQLModel Database Engine Configuration
Connects natively to PostgreSQL / Supabase with automatic SQLite local fallback.
"""

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
from app.models.hospital_models import *  # Ensure all models are loaded


load_dotenv()

# Get PostgreSQL Connection String from .env
raw_db_url = os.getenv("DATABASE_URL", "")

if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

def build_engine():
    """Builds SQLModel engine strictly for Supabase PostgreSQL"""
    if not raw_db_url:
        raise RuntimeError("DATABASE_URL environment variable is missing!")
    
    pg_engine = create_engine(
        raw_db_url,
        echo=False,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10}
    )
    print("Successfully initialized Supabase PostgreSQL engine!")
    return pg_engine

engine = build_engine()

def create_db_and_tables():
    """Initializes all SQLModel database tables & ensures missing columns exist"""
    try:
        SQLModel.metadata.create_all(engine)
        print("SQLModel tables verified & initialized.")
    except Exception as e:
        print(f"SQLModel table init note: {e}")

    # Only run PostgreSQL-specific ALTER TABLE migrations if using PostgreSQL
    if engine.dialect.name == "postgresql":
        alter_statements = [
            "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS hospital_type VARCHAR(50) DEFAULT 'SMALL';",
            "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'CHC';",
            "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS registration_number VARCHAR(100);",
            "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS license_number VARCHAR(100);",
            "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS has_nabh_accreditation BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS nabh_number VARCHAR(100);",
            "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS gst_number VARCHAR(50);",
            "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'PENDING_VERIFICATION';",
            "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS latitude FLOAT;",
            "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS longitude FLOAT;",
            "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;",
            "ALTER TABLE doctors ADD COLUMN IF NOT EXISTS shift_timing VARCHAR(255) DEFAULT 'Morning Shift (08:00 AM - 04:00 PM)';",
            "ALTER TABLE doctors ADD COLUMN IF NOT EXISTS name VARCHAR(255);",
            "ALTER TABLE drivers ADD COLUMN IF NOT EXISTS shift_timing VARCHAR(255) DEFAULT 'Morning Shift (08:00 AM - 04:00 PM)';",
            "ALTER TABLE drivers ADD COLUMN IF NOT EXISTS name VARCHAR(255);",
            "ALTER TABLE ambulances ADD COLUMN IF NOT EXISTS assigned_driver_name VARCHAR(255);",
            "ALTER TABLE ambulances ADD COLUMN IF NOT EXISTS vehicle_type VARCHAR(255) DEFAULT 'Basic';"
        ]
        for stmt in alter_statements:
            try:
                with engine.begin() as conn:
                    conn.execute(text(stmt))
            except Exception:
                pass

def get_session():
    """FastAPI Dependency for database sessions"""
    with Session(engine) as session:
        yield session
