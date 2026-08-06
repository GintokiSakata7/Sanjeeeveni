from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# --- Doctor Schemas ---
class DoctorCreatePayload(BaseModel):
    hospital_id: str
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    contact_number: str = Field(..., min_length=8)
    email: EmailStr
    password: str = Field(..., min_length=6)
    status: str = Field(default="Available")
    shift_timing: Optional[str] = Field(default="Morning Shift (08:00 AM - 04:00 PM)")

class DoctorUpdatePayload(BaseModel):
    name: Optional[str] = None
    specialization: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None
    shift_timing: Optional[str] = None

class DoctorResponse(BaseModel):
    id: str
    hospital_id: str
    name: str
    specialization: str
    contact_number: str
    email: str
    status: str
    shift_timing: Optional[str] = Field(default="Morning Shift (08:00 AM - 04:00 PM)")
    is_active: bool
    created_at: datetime

# --- Driver Schemas ---
class DriverCreatePayload(BaseModel):
    hospital_id: str
    name: str = Field(..., min_length=2)
    contact_number: str = Field(..., min_length=8)
    license_number: str = Field(..., min_length=3)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    status: str = Field(default="Available")
    shift_timing: Optional[str] = Field(default="Morning Shift (08:00 AM - 04:00 PM)")

class DriverUpdatePayload(BaseModel):
    name: Optional[str] = None
    contact_number: Optional[str] = None
    license_number: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None
    shift_timing: Optional[str] = None

class DriverResponse(BaseModel):
    id: str
    hospital_id: str
    name: str
    contact_number: str
    license_number: str
    email: Optional[str] = None
    status: str
    shift_timing: Optional[str] = Field(default="Morning Shift (08:00 AM - 04:00 PM)")
    created_at: datetime

# --- Ambulance Schemas ---
class AmbulanceCreatePayload(BaseModel):
    hospital_id: str
    vehicle_registration: str = Field(..., min_length=3)
    vehicle_type: str = Field(default="Basic")
    assigned_driver_id: Optional[str] = None
    assigned_driver_name: Optional[str] = None
    status: str = Field(default="Available")

class AmbulanceUpdatePayload(BaseModel):
    vehicle_registration: Optional[str] = None
    vehicle_type: Optional[str] = None
    assigned_driver_id: Optional[str] = None
    assigned_driver_name: Optional[str] = None
    status: Optional[str] = None

class AmbulanceResponse(BaseModel):
    id: str
    hospital_id: str
    vehicle_registration: str
    vehicle_type: str
    assigned_driver_id: Optional[str] = None
    assigned_driver_name: Optional[str] = None
    status: str
    created_at: datetime

# --- Overview Stats Schema ---
class HMSOverviewStats(BaseModel):
    total_doctors: int
    available_doctors: int
    in_surgery_doctors: int
    on_leave_doctors: int
    total_drivers: int
    available_drivers: int
    total_ambulances: int
    available_ambulances: int
    dispatched_ambulances: int
