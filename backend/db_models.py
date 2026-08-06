"""
AERO SQLModel Database Models & API Schemas
Pure Python ORM models matching the AERO system architecture (No Node/Prisma needed).
"""

import uuid
from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, JSON, Column

# Import real multi-tenant SQLModel models for Hospital, Doctor, Ambulance
from app.models.hospital_models import Hospital, Doctor, Ambulance

class RoleEnum(str, Enum):
    CITIZEN = "CITIZEN"
    HOSPITAL_ADMIN = "HOSPITAL_ADMIN"
    DOCTOR = "DOCTOR"
    AMBULANCE_DRIVER = "AMBULANCE_DRIVER"
    COMMUNITY_WORKER = "COMMUNITY_WORKER"
    SUPER_ADMIN = "SUPER_ADMIN"

class SeverityEnum(str, Enum):
    RED_CRITICAL = "RED_CRITICAL"
    AMBER_HIGH = "AMBER_HIGH"
    GREEN_LOW = "GREEN_LOW"

class EmergencyStatusEnum(str, Enum):
    REPORTED = "REPORTED"
    TRIAGED = "TRIAGED"
    DISPATCHED = "DISPATCHED"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED = "ARRIVED"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"

# --- SQLModel Database Tables ---

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    phone: str = Field(unique=True, index=True)
    email: Optional[str] = Field(default=None, unique=True)
    role: RoleEnum = Field(default=RoleEnum.CITIZEN)
    language: str = Field(default="en-US")
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityWorker(SQLModel, table=True):
    __tablename__ = "community_workers"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    skills: str
    current_lat: float
    current_lng: float
    is_available: bool = Field(default=True)

class EmergencyCase(SQLModel, table=True):
    __tablename__ = "emergency_cases"
    id: str = Field(default_factory=lambda: f"AERO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}", primary_key=True)
    input_text: str
    detected_language: str = Field(default="English")
    language_code: str = Field(default="en-US")
    translated_english: str
    category: str
    severity: SeverityEnum = Field(default=SeverityEnum.AMBER_HIGH)
    triage_code: str = Field(default="AMBER")
    chief_complaint: str
    symptoms: List[str] = Field(default=[], sa_column=Column(JSON))
    recommended_doctor_specialty: str
    triage_summary: str
    first_aid_english: List[dict] = Field(default=[], sa_column=Column(JSON))
    first_aid_native: List[dict] = Field(default=[], sa_column=Column(JSON))
    patient_lat: float = Field(default=17.3850)
    patient_lng: float = Field(default=78.4867)
    status: EmergencyStatusEnum = Field(default=EmergencyStatusEnum.TRIAGED)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class IncidentRecord(SQLModel, table=True):
    __tablename__ = "incident_records"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    emergency_case_id: str = Field(foreign_key="emergency_cases.id")
    action: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# --- FastAPI Request & Response Schemas ---

class SOSRequest(BaseModel):
    text: str
    input_mode: str = "voice"
    language: str = "auto"
    latitude: Optional[float] = 17.3850
    longitude: Optional[float] = 78.4867

class AudioSOSRequest(BaseModel):
    audio_base64: str
    mime_type: str = "audio/webm"
    language: str = "auto"
    latitude: Optional[float] = 17.3850
    longitude: Optional[float] = 78.4867

class FirstAidStep(BaseModel):
    step_number: int
    instruction: str
    icon: Optional[str] = "⚠️"

class AITriageResult(BaseModel):
    case_id: str
    created_at: str
    input_text: str
    detected_language: str
    language_code: str
    translated_english: str
    category: str
    severity: SeverityEnum
    triage_code: str
    chief_complaint: str
    symptoms: List[str] = []
    recommended_doctor_specialty: str
    triage_summary: str
    first_aid_english: List[FirstAidStep] = []
    first_aid_native: List[FirstAidStep] = []
