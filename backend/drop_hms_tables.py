import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

raw_db_url = os.getenv("DATABASE_URL", "")
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

print(f"Connecting to {raw_db_url}")
engine = create_engine(raw_db_url)

with engine.begin() as conn:
    print("Dropping HMS tables...")
    conn.execute(text('DROP TABLE IF EXISTS ambulances CASCADE;'))
    conn.execute(text('DROP TABLE IF EXISTS drivers CASCADE;'))
    conn.execute(text('DROP TABLE IF EXISTS doctors CASCADE;'))
    print("Dropped successfully.")
