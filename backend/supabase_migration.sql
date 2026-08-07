-- ============================================================
-- SANJEEVENI (AERO) - Complete Supabase Schema Migration
-- Run this entire script in your Supabase SQL Editor:
--   https://supabase.com/dashboard/project/tdbtgoqwetpwuujzccbw/sql/new
-- ============================================================

-- ─── 1. HOSPITALS ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hospitals (
    id                      TEXT PRIMARY KEY,
    name                    TEXT NOT NULL,
    hospital_type           TEXT NOT NULL DEFAULT 'SMALL',
    category                TEXT NOT NULL DEFAULT 'CHC',
    registration_number     TEXT UNIQUE,
    license_number          TEXT UNIQUE,
    has_nabh_accreditation  BOOLEAN DEFAULT FALSE,
    nabh_number             TEXT,
    gst_number              TEXT,
    status                  TEXT NOT NULL DEFAULT 'PENDING_VERIFICATION',
    latitude                DOUBLE PRECISION DEFAULT 17.4126,
    longitude               DOUBLE PRECISION DEFAULT 78.4482,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 2. HOSPITAL ADDRESSES ───────────────────────────────────
CREATE TABLE IF NOT EXISTS hospital_addresses (
    id               TEXT PRIMARY KEY,
    hospital_id      TEXT NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    country          TEXT DEFAULT 'India',
    state            TEXT,
    district         TEXT,
    city             TEXT,
    area             TEXT,
    pincode          TEXT,
    complete_address TEXT,
    latitude         DOUBLE PRECISION,
    longitude        DOUBLE PRECISION,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 3. HOSPITAL ADMINISTRATORS ──────────────────────────────
CREATE TABLE IF NOT EXISTS hospital_administrators (
    id          TEXT PRIMARY KEY,
    hospital_id TEXT NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    designation TEXT,
    email       TEXT UNIQUE NOT NULL,
    mobile      TEXT,
    password_hash TEXT NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    role        TEXT DEFAULT 'HOSPITAL_ADMIN',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 4. HOSPITAL DETAILS ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS hospital_details (
    id                  TEXT PRIMARY KEY,
    hospital_id         TEXT NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    total_beds          INTEGER DEFAULT 0,
    icu_beds            INTEGER DEFAULT 0,
    has_emergency_dept  BOOLEAN DEFAULT TRUE,
    has_trauma_center   BOOLEAN DEFAULT FALSE,
    has_blood_bank      BOOLEAN DEFAULT FALSE,
    ambulance_count     INTEGER DEFAULT 0,
    departments         JSONB DEFAULT '[]',
    specializations     JSONB DEFAULT '[]',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 5. HOSPITAL DOCUMENTS ───────────────────────────────────
CREATE TABLE IF NOT EXISTS hospital_documents (
    id                      TEXT PRIMARY KEY,
    hospital_id             TEXT NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    registration_cert_url   TEXT,
    govt_license_url        TEXT,
    nabh_cert_url           TEXT,
    pan_url                 TEXT,
    gst_url                 TEXT,
    exterior_image_url      TEXT,
    logo_url                TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 6. HOSPITAL INTEGRATIONS ────────────────────────────────
CREATE TABLE IF NOT EXISTS hospital_integrations (
    id                  TEXT PRIMARY KEY,
    hospital_id         TEXT NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    integration_mode    TEXT DEFAULT 'DASHBOARD',
    base_url            TEXT,
    callback_url        TEXT,
    api_doc_url         TEXT,
    tech_contact_name   TEXT,
    tech_contact_email  TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 7. HOSPITAL VERIFICATIONS ───────────────────────────────
CREATE TABLE IF NOT EXISTS hospital_verifications (
    id                  TEXT PRIMARY KEY,
    hospital_id         TEXT NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    verification_status TEXT NOT NULL,
    reviewed_by         TEXT,
    review_notes        TEXT,
    verified_at         TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 8. DOCTORS ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS doctors (
    id              TEXT PRIMARY KEY,
    hospital_id     TEXT NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    specialization  TEXT NOT NULL,
    contact_number  TEXT NOT NULL,
    email           TEXT NOT NULL,
    password_hash   TEXT,
    status          TEXT DEFAULT 'Available',
    shift_timing    TEXT DEFAULT 'Morning Shift (08:00 AM - 04:00 PM)',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Add missing columns if already exists (safe)
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS name TEXT;
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS shift_timing TEXT DEFAULT 'Morning Shift (08:00 AM - 04:00 PM)';
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- ─── 9. DRIVERS ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS drivers (
    id              TEXT PRIMARY KEY,
    hospital_id     TEXT NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    contact_number  TEXT NOT NULL,
    license_number  TEXT NOT NULL,
    email           TEXT,
    password_hash   TEXT,
    status          TEXT DEFAULT 'Available',
    shift_timing    TEXT DEFAULT 'Morning Shift (08:00 AM - 04:00 PM)',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE drivers ADD COLUMN IF NOT EXISTS name TEXT;
ALTER TABLE drivers ADD COLUMN IF NOT EXISTS shift_timing TEXT DEFAULT 'Morning Shift (08:00 AM - 04:00 PM)';
ALTER TABLE drivers ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- ─── 10. AMBULANCES ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ambulances (
    id                      TEXT PRIMARY KEY,
    hospital_id             TEXT NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    vehicle_registration    TEXT NOT NULL,
    vehicle_type            TEXT DEFAULT 'Basic',
    assigned_driver_id      TEXT REFERENCES drivers(id) ON DELETE SET NULL,
    assigned_driver_name    TEXT,
    status                  TEXT DEFAULT 'Available',
    current_lat             DOUBLE PRECISION,
    current_lng             DOUBLE PRECISION,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE ambulances ADD COLUMN IF NOT EXISTS vehicle_type TEXT DEFAULT 'Basic';
ALTER TABLE ambulances ADD COLUMN IF NOT EXISTS assigned_driver_name TEXT;

-- ─── 11. HELPERS ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS helpers (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    phone         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    location      TEXT,
    latitude      DOUBLE PRECISION,
    longitude     DOUBLE PRECISION,
    role_type     TEXT DEFAULT 'ASHA Community Health Worker',
    cert_id       TEXT,
    skills        JSONB DEFAULT '[]',
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE helpers ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION;
ALTER TABLE helpers ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION;
ALTER TABLE helpers ADD COLUMN IF NOT EXISTS location TEXT;
ALTER TABLE helpers ADD COLUMN IF NOT EXISTS role_type TEXT DEFAULT 'ASHA Community Health Worker';
ALTER TABLE helpers ADD COLUMN IF NOT EXISTS cert_id TEXT;
ALTER TABLE helpers ADD COLUMN IF NOT EXISTS skills JSONB DEFAULT '[]';
ALTER TABLE helpers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- ─── 12. SOS REQUESTS ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sos_requests (
    id                      TEXT PRIMARY KEY,
    hospital_id             TEXT NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    citizen_lat             DOUBLE PRECISION NOT NULL,
    citizen_lng             DOUBLE PRECISION NOT NULL,
    transcript              TEXT NOT NULL,
    triage_urgency          TEXT NOT NULL,
    image_url               TEXT,
    status                  TEXT DEFAULT 'PENDING',
    -- Driver assignment
    assigned_driver_id      TEXT REFERENCES drivers(id) ON DELETE SET NULL,
    assigned_driver_name    TEXT,
    assigned_ambulance_id   TEXT REFERENCES ambulances(id) ON DELETE SET NULL,
    assigned_ambulance_reg  TEXT,
    driver_status           TEXT DEFAULT 'NOT_ASSIGNED',
    -- Doctor assignment
    assigned_doctor_id      TEXT REFERENCES doctors(id) ON DELETE SET NULL,
    assigned_doctor_name    TEXT,
    doctor_status           TEXT DEFAULT 'NOT_ASSIGNED',
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE sos_requests ADD COLUMN IF NOT EXISTS assigned_driver_name TEXT;
ALTER TABLE sos_requests ADD COLUMN IF NOT EXISTS assigned_ambulance_id TEXT;
ALTER TABLE sos_requests ADD COLUMN IF NOT EXISTS assigned_ambulance_reg TEXT;
ALTER TABLE sos_requests ADD COLUMN IF NOT EXISTS driver_status TEXT DEFAULT 'NOT_ASSIGNED';
ALTER TABLE sos_requests ADD COLUMN IF NOT EXISTS assigned_doctor_id TEXT;
ALTER TABLE sos_requests ADD COLUMN IF NOT EXISTS assigned_doctor_name TEXT;
ALTER TABLE sos_requests ADD COLUMN IF NOT EXISTS doctor_status TEXT DEFAULT 'NOT_ASSIGNED';
ALTER TABLE sos_requests ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- ─── 13. SOS TIMELINES ───────────────────────────────────────
-- Note: Code uses 'sos_timelines' (plural) so create with that name
CREATE TABLE IF NOT EXISTS sos_timelines (
    id           TEXT PRIMARY KEY DEFAULT ('TL-' || upper(substring(gen_random_uuid()::text, 1, 12))),
    sos_id       TEXT NOT NULL REFERENCES sos_requests(id) ON DELETE CASCADE,
    event_type   TEXT NOT NULL,
    actor_role   TEXT NOT NULL,
    actor_id     TEXT,
    actor_name   TEXT,
    message      TEXT NOT NULL,
    metadata     JSONB DEFAULT '{}',
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 14. HELPER NOTIFICATIONS ────────────────────────────────
CREATE TABLE IF NOT EXISTS helper_notifications (
    id         TEXT PRIMARY KEY DEFAULT ('HN-' || upper(substring(gen_random_uuid()::text, 1, 12))),
    sos_id     TEXT NOT NULL REFERENCES sos_requests(id) ON DELETE CASCADE,
    helper_id  TEXT NOT NULL REFERENCES helpers(id) ON DELETE CASCADE,
    status     TEXT DEFAULT 'SENT',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 15. ENABLE ROW LEVEL SECURITY (RLS) BYPASS FOR SERVICE ROLE ────
-- The service_role key (SUPABASE_KEY) bypasses RLS automatically.
-- Enable RLS but ensure the service key still has full access.
ALTER TABLE hospitals ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospital_addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospital_administrators ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospital_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospital_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospital_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospital_verifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE drivers ENABLE ROW LEVEL SECURITY;
ALTER TABLE ambulances ENABLE ROW LEVEL SECURITY;
ALTER TABLE helpers ENABLE ROW LEVEL SECURITY;
ALTER TABLE sos_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE sos_timelines ENABLE ROW LEVEL SECURITY;
ALTER TABLE helper_notifications ENABLE ROW LEVEL SECURITY;

-- Allow service_role (used by backend) to do everything
CREATE POLICY IF NOT EXISTS "service_role_all" ON hospitals FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON hospital_addresses FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON hospital_administrators FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON hospital_details FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON hospital_documents FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON hospital_integrations FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON hospital_verifications FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON doctors FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON drivers FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON ambulances FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON helpers FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON sos_requests FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON sos_timelines FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "service_role_all" ON helper_notifications FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ─── Done ────────────────────────────────────────────────────
SELECT 'Schema migration complete! All tables created/verified.' AS result;
