# Sanjeevani (AERO) — Unified UML Diagrams & System Architecture

This document provides a complete set of **UML diagrams** (Mermaid format) representing the software architecture, data models, sequence flows, use cases, state transitions, and activity logic of the **Sanjeevani AI Emergency Response Orchestrator (AERO)** system.

---

## Table of Contents
1. [System Architecture & Component Diagram](#1-system-architecture--component-diagram)
2. [Class & Entity Relationship (ER) Diagram](#2-class--entity-relationship-er-diagram)
3. [Sequence Diagram: Multilingual SOS Voice Intake & Triage](#3-sequence-diagram-multilingual-sos-voice-intake--triage)
4. [Sequence Diagram: Hospital Registration & Admin Approval](#4-sequence-diagram-hospital-registration--admin-approval)
5. [Use Case Diagram](#5-use-case-diagram)
6. [State Machine Diagram: Emergency Case Lifecycle](#6-state-machine-diagram-emergency-case-lifecycle)
7. [Activity Diagram: STT, Intent & Triage Fallback Pipeline](#7-activity-diagram-stt-intent--triage-fallback-pipeline)

---

## 1. System Architecture & Component Diagram

High-level system topology showing client applications, API Gateway (FastAPI), AI Engine, Storage, and Database layer.

```mermaid
graph TB
    subgraph Client Layer
        A[Web Frontend - Vite + React]
        B[Mobile App - Flutter iOS/Android]
    end

    subgraph API Layer / FastAPI Backend
        C[FastAPI REST API Gateway]
        D[Router: /api/emergency]
        E[Router: /api/v1/hospitals]
        F[Router: /api/v1/admin]
        G[Router: /api/v1/hms]
    end

    subgraph AI Engine & Orchestrator
        H[AERO AI Engine Orchestrator]
        I[Whisper STT Service - Groq Whisper Large v3]
        J[Intent Service - Groq Llama 3.3 70B]
        K[Triage Service - Multilingual Clinical Engine]
        L[Gemini 2.0 Flash Fallback Engine]
        M[Rule-Based Emergency Fallback Engine]
    end

    subgraph External & Cloud Services
        N[Groq Cloud API - Whisper v3 & Llama 3.3 70B]
        O[Google Gemini API]
        P[Supabase Cloud Storage - hospital-documents Bucket]
    end

    subgraph Database Layer
        Q[(PostgreSQL / Supabase DB via SQLModel ORM)]
    end

    %% Connections
    A -->|REST / JSON| C
    B -->|REST / JSON| C
    C --> D
    C --> E
    C --> F
    C --> G

    D --> H
    H --> I
    H --> J
    H --> K

    I -->|Audio Bytes| N
    J -->|Prompt| N
    K -->|Prompt| N

    J -.->|Quota Fallback| O
    K -.->|Quota Fallback| O
    J -.->|Rule Fallback| M
    K -.->|Rule Fallback| M

    E -->|Upload Verification Docs| P
    E -->|CRUD Operations| Q
    F -->|Verify & Approve| Q
    G -->|Manage Doctors/Drivers/Ambulances| Q
    D -->|Persist Emergency Cases| Q
```

---

## 2. Class & Entity Relationship (ER) Diagram

Represents the **SQLModel ORM** entity schemas and database relationships across the system.

```mermaid
classDiagram
    %% Core Users & Emergency System
    class User {
        +String id (PK)
        +String name
        +String phone
        +String email
        +RoleEnum role
        +String language
        +String blood_group
        +String emergency_contact
        +DateTime created_at
    }

    class EmergencyCase {
        +String id (PK)
        +String input_text
        +String detected_language
        +String language_code
        +String translated_english
        +String category
        +SeverityEnum severity
        +String triage_code
        +String chief_complaint
        +List~String~ symptoms
        +String recommended_doctor_specialty
        +String triage_summary
        +List~JSON~ first_aid_english
        +List~JSON~ first_aid_native
        +Float patient_lat
        +Float patient_lng
        +EmergencyStatusEnum status
        +DateTime created_at
    }

    class IncidentRecord {
        +String id (PK)
        +String emergency_case_id (FK)
        +String action
        +String details
        +DateTime timestamp
    }

    class CommunityWorker {
        +String id (PK)
        +String user_id (FK)
        +String skills
        +Float current_lat
        +Float current_lng
        +Boolean is_available
    }

    %% Hospital Enterprise System
    class Hospital {
        +String id (PK)
        +String name
        +HospitalTypeEnum hospital_type
        +HospitalCategoryEnum category
        +String registration_number
        +String license_number
        +Boolean has_nabh_accreditation
        +String nabh_number
        +String gst_number
        +VerificationStatusEnum status
        +DateTime created_at
        +DateTime updated_at
    }

    class HospitalAddress {
        +String id (PK)
        +String hospital_id (FK)
        +String country
        +String state
        +String district
        +String city
        +String area
        +String pincode
        +String complete_address
        +Float latitude
        +Float longitude
    }

    class HospitalAdministrator {
        +String id (PK)
        +String hospital_id (FK)
        +String name
        +String designation
        +String email
        +String mobile
        +String password_hash
        +Boolean is_active
        +String role
    }

    class HospitalDetails {
        +String id (PK)
        +String hospital_id (FK)
        +Integer total_beds
        +Integer icu_beds
        +Boolean has_emergency_dept
        +Boolean has_trauma_center
        +Boolean has_blood_bank
        +Integer ambulance_count
        +List~String~ departments
        +List~String~ specializations
    }

    class HospitalDocuments {
        +String id (PK)
        +String hospital_id (FK)
        +String registration_cert_url
        +String govt_license_url
        +String nabh_cert_url
        +String pan_url
        +String gst_url
        +String exterior_image_url
        +String logo_url
    }

    class HospitalIntegration {
        +String id (PK)
        +String hospital_id (FK)
        +IntegrationModeEnum integration_mode
        +String base_url
        +String callback_url
        +String api_doc_url
        +String tech_contact_name
        +String tech_contact_email
    }

    class HospitalVerification {
        +String id (PK)
        +String hospital_id (FK)
        +VerificationStatusEnum verification_status
        +String reviewed_by
        +String review_notes
        +DateTime verified_at
    }

    %% Hospital Management System (HMS) Sub-entities
    class Doctor {
        +String id (PK)
        +String hospital_id (FK)
        +String name
        +String specialization
        +String contact_number
        +String email
        +String status
        +String shift_timing
        +String password_hash
        +Boolean is_active
    }

    class Driver {
        +String id (PK)
        +String hospital_id (FK)
        +String name
        +String contact_number
        +String license_number
        +String email
        +String password_hash
        +String status
        +String shift_timing
    }

    class Ambulance {
        +String id (PK)
        +String hospital_id (FK)
        +String vehicle_registration
        +String vehicle_type
        +String assigned_driver_id (FK)
        +String assigned_driver_name
        +String status
        +Float current_lat
        +Float current_lng
    }

    %% Relationships
    User "1" -- "0..1" CommunityWorker : owns
    EmergencyCase "1" -- "0..*" IncidentRecord : tracks
    Hospital "1" -- "1" HospitalAddress : located_at
    Hospital "1" -- "1" HospitalAdministrator : managed_by
    Hospital "1" -- "1" HospitalDetails : configured_with
    Hospital "1" -- "1" HospitalDocuments : verified_via
    Hospital "1" -- "1" HospitalIntegration : integrates_with
    Hospital "1" -- "0..*" HospitalVerification : audited_by
    Hospital "1" -- "0..*" Doctor : employs
    Hospital "1" -- "0..*" Driver : employs
    Hospital "1" -- "0..*" Ambulance : owns
    Driver "1" -- "0..1" Ambulance : drives
```

---

## 3. Sequence Diagram: Multilingual SOS Voice Intake & Triage

Flow of user voice audio from frontend through STT, Intent Classification, Triage Engine, Database Persistence, and TTS Voice Output.

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as 👤 Citizen / Caller
    participant Web as 💻 Web Frontend (MediaRecorder)
    participant API as ⚡ FastAPI Backend (/api/emergency/audio-sos)
    participant Whisper as 🎙️ Whisper Service (Groq v3)
    participant Intent as 🧠 Intent Classifier (Groq Llama 3.3 70B)
    participant Triage as 🩺 Triage Engine (Groq Llama 3.3 70B)
    participant DB as 🗄️ PostgreSQL Database
    participant Speech as 🔊 Web Speech API (TTS)

    Citizen->>Web: Click Microphone Orb & Speak Emergency (Telugu / Hindi / etc.)
    Web->>Web: Capture Audio Chunks via MediaRecorder (webm/ogg)
    Citizen->>Web: Click "TRANSMIT SOS SIGNAL"
    Web->>Web: Convert Audio Blob to Base64 JSON
    Web->>API: POST /api/emergency/audio-sos { audio_base64, mime_type, lat, lng }
    
    API->>Whisper: transcribe_audio_groq(audio_bytes)
    Whisper->>Whisper: Auto-detect script & language (e.g., te-IN)
    Whisper-->>API: { success: true, text: "అత్యవసర પરિస్తితులో...", detected_language: "Telugu (తెలుగు)" }

    API->>Intent: classify_intent(transcribed_text, "Telugu (తెలుగు)")
    Intent->>Intent: Extract sub_intent (e.g., CARDIAC / TRAUMA), urgency, distress level
    Intent-->>API: { intent: "EMERGENCY_MEDICAL", sub_intent: "CARDIAC", urgency: "CRITICAL" }

    API->>Triage: process_triage(transcribed_text, "te-IN", sub_intent="CARDIAC")
    Triage->>Triage: Translate to English & Generate First Aid in Telugu Script
    Triage-->>API: { category: "Cardiac Emergency", severity: "RED_CRITICAL", first_aid_native: [...] }

    API->>DB: Persist EmergencyCase SQLModel record
    DB-->>API: Saved with Case ID (AERO-AUD-20260807-XXXX)

    API-->>Web: Return JSON AITriageResult
    Web->>Web: Render Triage HUD, Category, Severity & First Aid Steps
    Web->>Speech: Speak First-Aid Guidance in Native Language (Telugu / Hindi)
    Speech-->>Citizen: Audio First-Aid Voice Playback 🔊
```

---

## 4. Sequence Diagram: Hospital Registration & Admin Approval

Workflow for hospital registration wizard, document upload to Supabase, and Super Admin approval.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as 🏥 Hospital Administrator
    participant Wizard as 🖥️ Registration Wizard (Frontend)
    participant API as ⚡ FastAPI Backend (/api/v1/hospitals)
    participant Storage as ☁️ Supabase Storage Bucket
    participant DB as 🗄️ PostgreSQL Database
    actor SuperAdmin as 🛡️ Super Admin

    Admin->>Wizard: Fill Step 1: Basic Info & Licenses
    Admin->>Wizard: Fill Step 2: Location & Address
    Admin->>Wizard: Fill Step 3: Admin User Credentials
    Admin->>Wizard: Fill Step 4: Infrastructure & Beds
    Admin->>Wizard: Upload Documents (Reg Cert, License, Logo) in Step 5
    
    Wizard->>Storage: Upload Files to `hospital-documents` Bucket
    Storage-->>Wizard: Return Public URLs for Documents
    
    Admin->>Wizard: Submit Registration
    Wizard->>API: POST /api/v1/hospitals/register { hospital_data, documents_urls }
    
    API->>DB: Create Hospital, Address, Admin, Details, Documents records
    API->>DB: Set Status = PENDING_VERIFICATION
    DB-->>API: Saved Hospital ID (HOSP-20260807-XXXX)
    API-->>Wizard: Registration Submitted (201 Created)

    SuperAdmin->>API: GET /api/v1/admin/pending-hospitals
    API->>DB: Query Hospitals WHERE status = PENDING_VERIFICATION
    DB-->>API: Return Pending Hospital List
    API-->>SuperAdmin: Display Verification Dashboard

    SuperAdmin->>API: POST /api/v1/admin/hospitals/{id}/approve
    API->>DB: Update Hospital Status = APPROVED
    API->>DB: Insert HospitalVerification Audit Log
    DB-->>API: Updated
    API-->>SuperAdmin: Hospital Approved (200 OK)
```

---

## 5. Use Case Diagram

Identifies all actors and primary system interactions across Citizen Intake, Emergency Orchestration, Hospital Operations, and Super Administration.

```mermaid
graph LR
    subgraph Actors
        C[👤 Citizen / Patient]
        H[🏥 Hospital Administrator]
        D[🩺 Hospital Doctor]
        V[🚑 Ambulance Driver]
        W[🤝 Community Helper]
        SA[🛡️ Super Admin]
    end

    subgraph AERO System Boundaries
        UC1((Transcribe Multilingual Voice SOS))
        UC2((Execute AI Triage & Severity Classification))
        UC3((Listen Native Language First-Aid Voice))
        UC4((Register Hospital & Upload License Docs))
        UC5((Manage Doctors, Drivers & Ambulances))
        UC6((View Real-Time Emergency Radar Dispatch))
        UC7((Audit & Approve Pending Hospitals))
        UC8((Accept Emergency Dispatch & Track GPS))
        UC9((Update Patient Admission & Bed Status))
    end

    C --> UC1
    C --> UC2
    C --> UC3

    H --> UC4
    H --> UC5
    H --> UC6

    D --> UC9
    V --> UC8
    W --> UC8

    SA --> UC7
    SA --> UC6
```

---

## 6. State Machine Diagram: Emergency Case Lifecycle

States and transition triggers for an emergency case from initial SOS intake through triage, dispatch, transit, and resolution.

```mermaid
stateDiagram-v2
    [*] --> REPORTED : User transmits text or voice SOS

    state REPORTED {
        [*] --> RawAudioOrTextReceived
    }

    REPORTED --> TRIAGED : Whisper STT + Groq LLM Triage complete

    state TRIAGED {
        [*] --> SeverityAssigned
        SeverityAssigned --> FirstAidGenerated
    }

    TRIAGED --> DISPATCHED : Nearest Hospital / Ambulance Radar Alerted

    state DISPATCHED {
        [*] --> DriverAssigned
        DriverAssigned --> SirenActivated
    }

    DISPATCHED --> IN_TRANSIT : Ambulance en-route to patient location

    state IN_TRANSIT {
        [*] --> LiveGpsTracking
        LiveGpsTracking --> PatientOnboard
    }

    IN_TRANSIT --> ARRIVED : Patient reaches Emergency Department

    state ARRIVED {
        [*] --> DoctorAssigned
        DoctorAssigned --> TriageHandover
    }

    ARRIVED --> RESOLVED : Patient admitted / stabilized
    TRIAGED --> CANCELLED : False alarm or duplicate report

    RESOLVED --> [*]
    CANCELLED --> [*]
```

---

## 7. Activity Diagram: STT, Intent & Triage Fallback Pipeline

Multi-tier execution and fault-tolerant fallback strategy for Speech-To-Text, Intent Classification, and Clinical Triage.

```mermaid
flowchart TD
    Start([User Initiates SOS Signal]) --> InputType{Input Mode?}
    
    InputType -->|Voice Recording| CheckGroqKey{Groq API Key Valid?}
    InputType -->|Typed Text| DetectLang[Auto-Detect Script & Language]

    %% Voice Path
    CheckGroqKey -->|Yes| GroqWhisper[Call Groq Whisper Large v3 STT]
    CheckGroqKey -->|No / Network Failure| GeminiAudio[Call Gemini Direct Audio Fallback]

    GroqWhisper --> TranscribeSuccess{Transcription Success?}
    TranscribeSuccess -->|Yes| ExtractText[Extract Transcribed Text & BCP-47 Code]
    TranscribeSuccess -->|No| GeminiAudio

    GeminiAudio --> ExtractText
    DetectLang --> ExtractText

    %% Intent Path
    ExtractText --> IntentGroq{Groq Llama 3.3 70B Available?}
    IntentGroq -->|Yes| RunIntentGroq[Execute Intent Classifier - Groq 70B]
    IntentGroq -->|No / Exception| IntentGemini{Gemini 2.0 Flash Available?}
    
    IntentGemini -->|Yes| RunIntentGemini[Execute Intent Classifier - Gemini]
    IntentGemini -->|No| RunIntentRule[Execute Keyword-based Rule Intent Engine]

    RunIntentGroq --> SubIntentExtracted[Extract Emergency Sub-Intent & Urgency]
    RunIntentGemini --> SubIntentExtracted
    RunIntentRule --> SubIntentExtracted

    %% Triage Path
    SubIntentExtracted --> TriageGroq{Groq Llama 3.3 70B Available?}
    TriageGroq -->|Yes| RunTriageGroq[Generate Clinical Triage & Native First-Aid - Groq]
    TriageGroq -->|No / Exception| TriageGemini{Gemini Available?}

    TriageGemini -->|Yes| RunTriageGemini[Generate Clinical Triage - Gemini]
    TriageGemini -->|No| RunTriageRule[Generate Generic Rule-based Triage & First-Aid]

    RunTriageGroq --> FormatJSON[Compile Final AITriageResult JSON]
    RunTriageGemini --> FormatJSON
    RunTriageRule --> FormatJSON

    FormatJSON --> SaveDB[(Save EmergencyCase to PostgreSQL)]
    SaveDB --> Output([Return Response to Frontend & Trigger TTS Voice])
```

---

*Generated for Sanjeevani (AERO) Repository — Pure Python SQLModel + FastAPI + Groq Whisper v3 + Groq Llama 3.3 70B.*
