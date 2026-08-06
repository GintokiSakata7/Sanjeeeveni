-- Sanjeevani (AERO) Supabase PostgreSQL Schema
-- Normalized relational model for Hospital Registration & Multi-tenancy

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum Types
CREATE TYPE hospital_type_enum AS ENUM ('SMALL', 'LARGE');
CREATE TYPE hospital_category_enum AS ENUM ('CHC', 'MULTI_SPECIALITY', 'SUPER_SPECIALITY');
CREATE TYPE integration_mode_enum AS ENUM ('REST_API', 'HL7_FHIR', 'CUSTOM_API', 'DASHBOARD');
CREATE TYPE verification_status_enum AS ENUM ('PENDING_VERIFICATION', 'APPROVED', 'REJECTED', 'SUSPENDED');

-- 1. Main Hospital Entity
CREATE TABLE IF NOT EXISTS hospitals (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    hospital_type hospital_type_enum NOT NULL DEFAULT 'SMALL',
    category hospital_category_enum NOT NULL DEFAULT 'CHC',
    registration_number VARCHAR(100) NOT NULL UNIQUE,
    license_number VARCHAR(100) NOT NULL UNIQUE,
    has_nabh_accreditation BOOLEAN NOT NULL DEFAULT FALSE,
    nabh_number VARCHAR(100),
    gst_number VARCHAR(50),
    status verification_status_enum NOT NULL DEFAULT 'PENDING_VERIFICATION',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Hospital Address & Location
CREATE TABLE IF NOT EXISTS hospital_addresses (
    id VARCHAR(64) PRIMARY KEY,
    hospital_id VARCHAR(64) NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    area VARCHAR(100) NOT NULL,
    pincode VARCHAR(20) NOT NULL,
    complete_address TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Hospital Administrator & Credentials
CREATE TABLE IF NOT EXISTS hospital_administrators (
    id VARCHAR(64) PRIMARY KEY,
    hospital_id VARCHAR(64) NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    mobile VARCHAR(30) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    role VARCHAR(50) NOT NULL DEFAULT 'HOSPITAL_ADMIN',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Hospital Medical Capacity & Details
CREATE TABLE IF NOT EXISTS hospital_details (
    id VARCHAR(64) PRIMARY KEY,
    hospital_id VARCHAR(64) NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    total_beds INT NOT NULL DEFAULT 0,
    icu_beds INT NOT NULL DEFAULT 0,
    has_emergency_dept BOOLEAN NOT NULL DEFAULT TRUE,
    has_trauma_center BOOLEAN NOT NULL DEFAULT FALSE,
    has_blood_bank BOOLEAN NOT NULL DEFAULT FALSE,
    ambulance_count INT NOT NULL DEFAULT 0,
    departments JSONB DEFAULT '[]'::jsonb,
    specializations JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Hospital Verification Documents (Supabase Storage URLs)
CREATE TABLE IF NOT EXISTS hospital_documents (
    id VARCHAR(64) PRIMARY KEY,
    hospital_id VARCHAR(64) NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    registration_cert_url TEXT NOT NULL,
    govt_license_url TEXT NOT NULL,
    nabh_cert_url TEXT,
    pan_url TEXT NOT NULL,
    gst_url TEXT,
    exterior_image_url TEXT NOT NULL,
    logo_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Hospital Integration Mode (Large Hospitals)
CREATE TABLE IF NOT EXISTS hospital_integrations (
    id VARCHAR(64) PRIMARY KEY,
    hospital_id VARCHAR(64) NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    integration_mode integration_mode_enum NOT NULL DEFAULT 'DASHBOARD',
    base_url VARCHAR(255),
    callback_url VARCHAR(255),
    api_doc_url VARCHAR(255),
    tech_contact_name VARCHAR(100),
    tech_contact_email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Hospital Verification Audit Trail
CREATE TABLE IF NOT EXISTS hospital_verifications (
    id VARCHAR(64) PRIMARY KEY,
    hospital_id VARCHAR(64) NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    verification_status verification_status_enum NOT NULL,
    reviewed_by VARCHAR(255),
    review_notes TEXT,
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Future compatibility: Doctors Table (Stub)
CREATE TABLE IF NOT EXISTS doctors (
    id VARCHAR(64) PRIMARY KEY,
    hospital_id VARCHAR(64) NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    mobile VARCHAR(30) NOT NULL,
    mobile_login_code VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. Future compatibility: Ambulances Table (Stub)
CREATE TABLE IF NOT EXISTS ambulances (
    id VARCHAR(64) PRIMARY KEY,
    hospital_id VARCHAR(64) NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    vehicle_number VARCHAR(50) NOT NULL,
    driver_name VARCHAR(255) NOT NULL,
    driver_mobile VARCHAR(30) NOT NULL,
    mobile_login_code VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    current_lat DOUBLE PRECISION,
    current_lng DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for spatial and lookup performance
CREATE INDEX IF NOT EXISTS idx_hospitals_status ON hospitals(status);
CREATE INDEX IF NOT EXISTS idx_hospitals_type ON hospitals(hospital_type);
CREATE INDEX IF NOT EXISTS idx_hospital_addresses_coords ON hospital_addresses(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_hospital_admins_email ON hospital_administrators(email);
