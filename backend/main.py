"""
# AERO - AI Emergency Response Orchestrator & Hospital Management FastAPI Backend
AERO - AI Emergency Response Orchestrator & Hospital Management FastAPI Backend
Pure Python SQLModel + PostgreSQL / Supabase Database Architecture.
"""

import uuid
import base64
import os
from datetime import datetime
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from database import get_supabase, create_db_and_tables
from supabase import Client
from db_models import (
    SOSRequest, AudioSOSRequest, AITriageResult, FirstAidStep,
    EmergencyCase, SeverityEnum, EmergencyStatusEnum
)
from ai_engine import analyze_emergency, analyze_audio_emergency

# Import Hospital Registration & Super Admin module entities & routes
import app.models.hospital_models  # Ensures SQLModel registers hospital tables
from app.api.v1.hospital_routes import router as hospital_v1_router
from app.api.v1.admin_routes import router as admin_v1_router
from app.api.v1.hms_routes import router as hms_v1_router
from app.api.v1.mobile_auth_routes import router as mobile_auth_v1_router
from app.core.config import settings

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes PostgreSQL database tables natively via SQLModel on application startup"""
    try:
        create_db_and_tables()
        print("SQLModel DB & Tables initialized successfully.")
    except Exception as e:
        print(f"PostgreSQL connection note: {e}")
    yield

app = FastAPI(
    title="Sanjeevani (AERO) AI Emergency & Hospital Orchestrator Engine",
    version="2.0.0",
    description="FastAPI + SQLModel + AI Emergency Triage + Hospital Multi-Step Registration API.",
    lifespan=lifespan
)

# Enable CORS for Web Frontend
# Note: allow_credentials=True cannot be used with allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded verification documents locally when Supabase Storage is offline
os.makedirs(settings.LOCAL_UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.LOCAL_UPLOAD_DIR), name="uploads")

# Mount API V1 Routers
app.include_router(hospital_v1_router, prefix="/api/v1")
app.include_router(admin_v1_router, prefix="/api/v1")
app.include_router(hms_v1_router, prefix="/api/v1")
app.include_router(mobile_auth_v1_router, prefix="/api/v1")
from app.api.v1.sos_routing_routes import router as sos_routing_router
from app.api.v1.helper_routes import router as helper_routes_router
from app.api.v1.ws_routes import router as ws_router

app.include_router(sos_routing_router, prefix="/api/v1")
app.include_router(helper_routes_router, prefix="/api/v1/auth")
app.include_router(ws_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Sanjeevani (AERO) AI Emergency Triage & Hospital Management Engine",
        "version": "2.0.0",
        "health_check": "/api/emergency/health",
        "hospital_api_docs": "/docs"
    }

@app.get("/api/emergency/health")
def health_check():
    return {
        "status": "online",
        "system": "AERO - Real AI Emergency Classification Engine (SQLModel)",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test-webrtc")
async def serve_webrtc_test():
    """Serves the standalone WebRTC testing HTML page."""
    file_path = os.path.join(os.path.dirname(__file__), "static", "webrtc_test.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Test file not found")

@app.post("/api/emergency/sos", response_model=AITriageResult)
async def create_sos_case(payload: SOSRequest, db: Client = Depends(get_supabase)):
    """
    Main SOS Intake Endpoint:
    Processes user text/transcript, auto-detects language, translates to English,
    classifies severity, generates first aid, and persists case into Supabase.
    """
    if not payload.text or len(payload.text.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Emergency description cannot be empty."
        )

    case_id = f"AERO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

    triage_raw = await analyze_emergency(payload.text, payload.language)

    fa_en = triage_raw.get("first_aid_english", [])
    fa_nat = triage_raw.get("first_aid_native", [])

    return AITriageResult(
        case_id=case_id,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        input_text=payload.text,
        detected_language=triage_raw.get("detected_language", "English"),
        language_code=triage_raw.get("language_code", "en-US"),
        translated_english=triage_raw.get("translated_english", payload.text),
        category=triage_raw.get("category", "General Emergency"),
        severity=SeverityEnum(triage_raw.get("severity", "AMBER_HIGH")),
        triage_code=triage_raw.get("triage_code", "AMBER"),
        chief_complaint=triage_raw.get("chief_complaint", "Emergency reported"),
        symptoms=triage_raw.get("symptoms", []),
        recommended_doctor_specialty=triage_raw.get("recommended_doctor_specialty", "Emergency Physician"),
        triage_summary=triage_raw.get("triage_summary", "Emergency analyzed"),
        first_aid_english=[FirstAidStep(**step) for step in fa_en],
        first_aid_native=[FirstAidStep(**step) for step in fa_nat]
    )

@app.post("/api/emergency/audio-sos", response_model=AITriageResult)
async def create_audio_sos_case(payload: AudioSOSRequest, db: Client = Depends(get_supabase)):
    """
    Base64 JSON Audio SOS Intake Endpoint:
    Decodes audio string and processes with Whisper Large v3 / Gemini LLM.
    Persists case natively into PostgreSQL via SQLModel.
    """
    try:
        audio_bytes = base64.b64decode(payload.audio_base64)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid base64 audio payload: {e}"
        )

    if not audio_bytes or len(audio_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio content cannot be empty."
        )

    case_id = f"AERO-AUD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

    triage_raw = await analyze_audio_emergency(audio_bytes, payload.mime_type, payload.language)

    fa_en = triage_raw.get("first_aid_english", [])
    fa_nat = triage_raw.get("first_aid_native", [])


    return AITriageResult(
        case_id=case_id,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        input_text=triage_raw.get("transcribed_text", "Audio intake"),
        detected_language=triage_raw.get("detected_language", "English"),
        language_code=triage_raw.get("language_code", "en-US"),
        translated_english=triage_raw.get("translated_english", "Audio emergency intake"),
        category=triage_raw.get("category", "General Emergency"),
        severity=SeverityEnum(triage_raw.get("severity", "AMBER_HIGH")),
        triage_code=triage_raw.get("triage_code", "AMBER"),
        chief_complaint=triage_raw.get("chief_complaint", "Audio emergency analyzed"),
        symptoms=triage_raw.get("symptoms", []),
        recommended_doctor_specialty=triage_raw.get("recommended_doctor_specialty", "Emergency Physician"),
        triage_summary=triage_raw.get("triage_summary", "Emergency analyzed"),
        first_aid_english=[FirstAidStep(**step) for step in fa_en],
        first_aid_native=[FirstAidStep(**step) for step in fa_nat]
    )

@app.get("/api/emergency/cases")
def get_recent_cases(db: Client = Depends(get_supabase)):
    """Retrieve recent SOS requests from Supabase"""
    try:
        results = db.table("sos_requests").select("*").order("created_at", desc=True).limit(50).execute().data or []
        return {"total_cases": len(results), "cases": results}
    except Exception:
        return {"total_cases": 0, "cases": []}
