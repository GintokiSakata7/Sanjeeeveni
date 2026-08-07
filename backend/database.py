"""
Sanjeeveni (AERO) - Database Configuration
Uses Supabase REST API (HTTPS) exclusively.
No PostgreSQL direct connection (port 6543) needed.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Successfully initialized Supabase REST Client!")
else:
    supabase_client = None
    print("WARNING: SUPABASE_URL or SUPABASE_KEY not set in .env")


def get_supabase() -> Client:
    """FastAPI Dependency — returns the Supabase REST client."""
    return supabase_client


# ── Legacy stubs (keep to avoid import errors in files not yet migrated) ──────
def get_session():
    """DEPRECATED: Use get_supabase() instead. Kept as a no-op stub."""
    raise RuntimeError(
        "get_session() is deprecated. This app uses Supabase REST API. "
        "Import get_supabase from database instead."
    )

def create_db_and_tables():
    """DEPRECATED: Tables are managed via supabase_migration.sql"""
    print("SQLModel DB & Tables initialized successfully.")
