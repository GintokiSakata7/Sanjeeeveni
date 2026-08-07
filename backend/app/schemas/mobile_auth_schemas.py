from pydantic import BaseModel, Field
from typing import Optional, List


class DoctorLoginRequest(BaseModel):
    """Doctor logs in using email + password (credentials from HMS admin)"""
    identifier: str = Field(..., min_length=2, description="Doctor email or doctor ID")
    password: str = Field(..., min_length=1)


class DriverLoginRequest(BaseModel):
    """Driver logs in using contact number or email + password (credentials from HMS admin)"""
    identifier: str = Field(..., min_length=2, description="Driver contact number, email, or driver ID")
    password: str = Field(..., min_length=1)


class HelperRegisterRequest(BaseModel):
    """Helper (ASHA/community worker) self-registers via mobile app"""
    name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=8)
    password: str = Field(..., min_length=6)
    location: Optional[str] = None
    role_type: str = Field(default="ASHA Community Health Worker")
    cert_id: Optional[str] = None
    skills: List[str] = Field(default=[])
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class HelperLoginRequest(BaseModel):
    """Helper logs in using phone + password"""
    phone: str = Field(..., min_length=8)
    password: str = Field(..., min_length=1)


class MobileAuthResponse(BaseModel):
    """Unified auth response returned to Flutter on successful login/register"""
    success: bool = True
    token: str
    role: str
    user_id: str
    user_name: str
    hospital_id: Optional[str] = None
    hospital_name: Optional[str] = None
    specialization: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    shift_timing: Optional[str] = None
    badge_id: Optional[str] = None
    license_number: Optional[str] = None
    location: Optional[str] = None
    role_type: Optional[str] = None
