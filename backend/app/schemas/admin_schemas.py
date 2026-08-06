from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.hospital_models import VerificationStatusEnum

class AdminLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Super Admin Email")
    password: str = Field(..., min_length=6, description="Super Admin Password")

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_name: str
    email: str

class HospitalVerifyActionPayload(BaseModel):
    status: VerificationStatusEnum = Field(..., description="APPROVED or REJECTED")
    notes: Optional[str] = Field(None, description="Admin review feedback notes")

class AdminStatsResponse(BaseModel):
    total_hospitals: int
    pending_verifications: int
    approved_hospitals: int
    rejected_hospitals: int
    total_beds: int
    total_icu_beds: int
    total_ambulances: int
