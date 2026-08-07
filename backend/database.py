"""
Sanjeevani (AERO) Supabase REST API Client Configuration
Exposes both SQLModel (local SQLite fallback) and Supabase REST Client for migration.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

# Get Supabase URL and Key from .env (or environment variables)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Successfully initialized Supabase REST Client!")
else:
    supabase_client = None
    print("WARNING: Supabase keys not set.")

def get_supabase() -> Client:
    """Dependency for Supabase REST Client"""
    return supabase_client

# Keep SQLModel engine as local SQLite fallback for routes not yet migrated
engine = create_engine("sqlite:///sanjeevani.db", echo=False, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    """FastAPI Dependency. Returns local SQLite session."""
    with Session(engine) as session:
        yield session

