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
    """Builds SQLModel engine with automatic local SQLite fallback on database error"""
    if raw_db_url:
        try:
            pg_engine = create_engine(
                raw_db_url,
                echo=False,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 5}
            )
            # Test live connection
            with pg_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Successfully connected to Supabase PostgreSQL Database!")
            return pg_engine
        except Exception as e:
            print(f"Supabase PostgreSQL Connection Warning: {e}")
            print("Falling back to local SQLite database 'sanjeevani_local.db'...")

    # SQLite Local Fallback
    local_db_path = os.path.join(os.path.dirname(__file__), "sanjeevani_local.db")
    sqlite_url = f"sqlite:///{local_db_path}"
    sqlite_engine = create_engine(
        sqlite_url,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    print(f"Using local SQLite engine: {sqlite_url}")
    return sqlite_engine

engine = build_engine()

def create_db_and_tables():
    """Initializes all SQLModel database tables & ensures missing columns exist"""
    alter_statements = [
        "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS hospital_type VARCHAR(50) DEFAULT 'SMALL';",
        "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'CHC';",
        "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS registration_number VARCHAR(100);",
        "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS license_number VARCHAR(100);",
        "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS has_nabh_accreditation BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS nabh_number VARCHAR(100);",
        "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS gst_number VARCHAR(50);",
        "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'PENDING_VERIFICATION';",
        "ALTER TABLE hospitals ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;",
        "ALTER TABLE hospitals ALTER COLUMN address DROP NOT NULL;",
        "ALTER TABLE hospitals ALTER COLUMN contact_phone DROP NOT NULL;",
        "ALTER TABLE hospitals ALTER COLUMN contact_email DROP NOT NULL;",
        "ALTER TABLE hospitals ALTER COLUMN latitude DROP NOT NULL;",
        "ALTER TABLE hospitals ALTER COLUMN longitude DROP NOT NULL;",
        "ALTER TABLE hospitals ALTER COLUMN total_beds DROP NOT NULL;",
        "ALTER TABLE hospitals ALTER COLUMN available_beds DROP NOT NULL;",
        "ALTER TABLE hospitals ALTER COLUMN icu_beds DROP NOT NULL;",
        "ALTER TABLE hospitals ALTER COLUMN ventilators DROP NOT NULL;",
        "ALTER TABLE hospitals ALTER COLUMN id TYPE VARCHAR(64);",
        # HMS Missing Columns
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

    try:
        SQLModel.metadata.create_all(engine)
        print("SQLModel tables verified & initialized.")
    except Exception as e:
        print(f"SQLModel table init note: {e}")

def get_session():
    """FastAPI Dependency for database sessions"""
    with Session(engine) as session:
        yield session
