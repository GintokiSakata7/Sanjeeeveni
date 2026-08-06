import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

raw_db_url = os.getenv("DATABASE_URL", "")
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(raw_db_url)

with engine.begin() as conn:
    # Remove duplicate doctors (keep the most recently created one per email per hospital)
    result = conn.execute(text("""
        DELETE FROM doctors
        WHERE id IN (
            SELECT id FROM (
                SELECT id,
                       ROW_NUMBER() OVER (PARTITION BY hospital_id, email ORDER BY created_at DESC) as rn
                FROM doctors
            ) ranked
            WHERE rn > 1
        );
    """))
    print(f"Deleted {result.rowcount} duplicate doctor(s).")

    # Remove duplicate drivers (keep the most recently created one per license per hospital)
    result2 = conn.execute(text("""
        DELETE FROM drivers
        WHERE id IN (
            SELECT id FROM (
                SELECT id,
                       ROW_NUMBER() OVER (PARTITION BY hospital_id, license_number ORDER BY created_at DESC) as rn
                FROM drivers
            ) ranked
            WHERE rn > 1
        );
    """))
    print(f"Deleted {result2.rowcount} duplicate driver(s).")

print("Done.")
