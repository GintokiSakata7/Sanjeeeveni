from enum import Enum
from datetime import datetime
from typing import Optional, List
import uuid
from sqlmodel import SQLModel, Field, Column, JSON, Relationship

class HospitalTypeEnum(str, Enum):
    SMALL = "SMALL"
    LARGE = "LARGE"

class HospitalCategoryEnum(str, Enum):
    CHC = "CHC"
    MULTI_SPECIALITY = "MULTI_SPECIALITY"
    SUPER_SPECIALITY = "SUPER_SPECIALITY"

class IntegrationModeEnum(str, Enum):
    REST_API = "REST_API"
    HL7_FHIR = "HL7_FHIR"
    CUSTOM_API = "CUSTOM_API"
    DASHBOARD = "DASHBOARD"

class VerificationStatusEnum(str, Enum):
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"

# --- Main SQLModel Tables ---

class Hospital(SQLModel, table=True):
    __tablename__ = "hospitals"
    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    hospital_type: HospitalTypeEnum = Field(default=HospitalTypeEnum.SMALL)
    category: HospitalCategoryEnum = Field(default=HospitalCategoryEnum.CHC)
    registration_number: str = Field(unique=True, index=True)
    license_number: str = Field(unique=True)
    has_nabh_accreditation: bool = Field(default=False)
    nabh_number: Optional[str] = Field(default=None)
    gst_number: Optional[str] = Field(default=None)
    status: VerificationStatusEnum = Field(default=VerificationStatusEnum.PENDING_VERIFICATION, index=True)
    latitude: Optional[float] = Field(default=17.4126)
    longitude: Optional[float] = Field(default=78.4482)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    address: Optional["HospitalAddress"] = Relationship(back_populates="hospital")
    administrator: Optional["HospitalAdministrator"] = Relationship(back_populates="hospital")
    details: Optional["HospitalDetails"] = Relationship(back_populates="hospital")
    documents: Optional["HospitalDocuments"] = Relationship(back_populates="hospital")
    integration: Optional["HospitalIntegration"] = Relationship(back_populates="hospital")


class HospitalAddress(SQLModel, table=True):
    __tablename__ = "hospital_addresses"
    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    hospital_id: str = Field(foreign_key="hospitals.id", index=True)
    country: str = Field(default="India")
    state: str
    district: str
    city: str
    area: str
    pincode: str
    complete_address: str
    latitude: float
    longitude: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

    hospital: Optional[Hospital] = Relationship(back_populates="address")


class HospitalAdministrator(SQLModel, table=True):
    __tablename__ = "hospital_administrators"
    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    hospital_id: str = Field(foreign_key="hospitals.id", index=True)
    name: str
    designation: str
    email: str = Field(unique=True, index=True)
    mobile: str
    password_hash: str
    is_active: bool = Field(default=True)
    role: str = Field(default="HOSPITAL_ADMIN")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    hospital: Optional[Hospital] = Relationship(back_populates="administrator")


class HospitalDetails(SQLModel, table=True):
    __tablename__ = "hospital_details"
    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    hospital_id: str = Field(foreign_key="hospitals.id", index=True)
    total_beds: int = Field(default=0)
    icu_beds: int = Field(default=0)
    has_emergency_dept: bool = Field(default=True)
    has_trauma_center: bool = Field(default=False)
    has_blood_bank: bool = Field(default=False)
    ambulance_count: int = Field(default=0)
    departments: List[str] = Field(default=[], sa_column=Column(JSON))
    specializations: List[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    hospital: Optional[Hospital] = Relationship(back_populates="details")


class HospitalDocuments(SQLModel, table=True):
    __tablename__ = "hospital_documents"
    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    hospital_id: str = Field(foreign_key="hospitals.id", index=True)
    registration_cert_url: str
    govt_license_url: str
    nabh_cert_url: Optional[str] = Field(default=None)
    pan_url: str
    gst_url: Optional[str] = Field(default=None)
    exterior_image_url: str
    logo_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    hospital: Optional[Hospital] = Relationship(back_populates="documents")


class HospitalIntegration(SQLModel, table=True):
    __tablename__ = "hospital_integrations"
    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    hospital_id: str = Field(foreign_key="hospitals.id", index=True)
    integration_mode: IntegrationModeEnum = Field(default=IntegrationModeEnum.DASHBOARD)
    base_url: Optional[str] = Field(default=None)
    callback_url: Optional[str] = Field(default=None)
    api_doc_url: Optional[str] = Field(default=None)
    tech_contact_name: Optional[str] = Field(default=None)
    tech_contact_email: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    hospital: Optional[Hospital] = Relationship(back_populates="integration")


class HospitalVerification(SQLModel, table=True):
    __tablename__ = "hospital_verifications"
    __table_args__ = {"extend_existing": True}

    id: str = Field(default_factory=lambda: f"VERIF-{uuid.uuid4().hex[:12].upper()}", primary_key=True)
    hospital_id: str = Field(foreign_key="hospitals.id", index=True)
    verification_status: VerificationStatusEnum
    reviewed_by: Optional[str] = Field(default=None)
    review_notes: Optional[str] = Field(default=None)
    verified_at: datetime = Field(default_factory=datetime.utcnow)


# --- Hospital Management System (HMS) Models ---

class Doctor(SQLModel, table=True):
    __tablename__ = "doctors"
    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    hospital_id: str = Field(foreign_key="hospitals.id", index=True)
    name: str
    specialization: str
    contact_number: str
    email: str
    status: str = Field(default="Available")  # Available, On Leave, In Surgery
    shift_timing: Optional[str] = Field(default="Morning Shift (08:00 AM - 04:00 PM)")
    password_hash: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Driver(SQLModel, table=True):
    __tablename__ = "drivers"
    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    hospital_id: str = Field(foreign_key="hospitals.id", index=True)
    name: str
    contact_number: str
    license_number: str
    email: Optional[str] = Field(default=None)
    password_hash: Optional[str] = Field(default=None)
    status: str = Field(default="Available")  # Available, Off Duty, Dispatched
    shift_timing: Optional[str] = Field(default="Morning Shift (08:00 AM - 04:00 PM)")
    created_at: datetime = Field(default_factory=datetime.utcnow)



class Ambulance(SQLModel, table=True):
    __tablename__ = "ambulances"
    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    hospital_id: str = Field(foreign_key="hospitals.id", index=True)
    vehicle_registration: str
    vehicle_type: str = Field(default="Basic")  # Basic, Advanced Life Support
    assigned_driver_id: Optional[str] = Field(default=None, foreign_key="drivers.id")
    assigned_driver_name: Optional[str] = Field(default=None)
    status: str = Field(default="Available")  # Available, Dispatched, Maintenance
    current_lat: Optional[float] = Field(default=None)
    current_lng: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Helper(SQLModel, table=True):
    __tablename__ = "helpers"
    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    name: str
    phone: str = Field(unique=True, index=True)
    password_hash: str
    location: Optional[str] = Field(default=None)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    role_type: str = Field(default="ASHA Community Health Worker")
    cert_id: Optional[str] = Field(default=None)
    skills: List[str] = Field(default=[], sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)



class SOSRequest(SQLModel, table=True):
    __tablename__ = "sos_requests"
    __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    hospital_id: str = Field(foreign_key="hospitals.id", index=True)
    citizen_lat: float
    citizen_lng: float
    transcript: str
    triage_urgency: str
    image_url: Optional[str] = Field(default=None)
    status: str = Field(default="PENDING")  # PENDING, ACCEPTED, REJECTED
    
    # PRIMARY: Ambulance Driver Assignment
    assigned_driver_id: Optional[str] = Field(default=None, foreign_key="drivers.id")
    assigned_driver_name: Optional[str] = Field(default=None)
    assigned_ambulance_id: Optional[str] = Field(default=None, foreign_key="ambulances.id")
    assigned_ambulance_reg: Optional[str] = Field(default=None)
    driver_status: str = Field(default="NOT_ASSIGNED")  # NOT_ASSIGNED, ASSIGNED, ACCEPTED, EN_ROUTE, ARRIVED
    
    # SECONDARY: Doctor Assignment
    assigned_doctor_id: Optional[str] = Field(default=None, foreign_key="doctors.id")
    assigned_doctor_name: Optional[str] = Field(default=None)
    doctor_status: str = Field(default="NOT_ASSIGNED")  # NOT_ASSIGNED, ASSIGNED, ACCEPTED
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SOSTimeline(SQLModel, table=True):
    """Tracks every event in an SOS lifecycle for the info/chat feed"""
    __tablename__ = "sos_timeline"
    __table_args__ = {"extend_existing": True}
    
    id: str = Field(default_factory=lambda: f"TL-{uuid.uuid4().hex[:12].upper()}", primary_key=True)
    sos_id: str = Field(foreign_key="sos_requests.id", index=True)
    event_type: str  # CREATED, HOSPITAL_NOTIFIED, HOSPITAL_ACCEPTED, DRIVER_ASSIGNED, DRIVER_ACCEPTED, EN_ROUTE, ARRIVED, DOCTOR_ASSIGNED, HELPER_NOTIFIED, MESSAGE
    actor_role: str  # citizen, hospital, driver, doctor, helper, system
    actor_id: Optional[str] = None
    actor_name: Optional[str] = None
    message: str
    event_metadata: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HelperNotification(SQLModel, table=True):
    __tablename__ = "helper_notifications"
    __table_args__ = {"extend_existing": True}
    
    id: str = Field(default_factory=lambda: f"HN-{uuid.uuid4().hex[:12].upper()}", primary_key=True)
    sos_id: str = Field(foreign_key="sos_requests.id", index=True)
    helper_id: str = Field(foreign_key="helpers.id", index=True)
    status: str = Field(default="SENT")  # SENT, SEEN, RESPONDING, ARRIVED
    created_at: datetime = Field(default_factory=datetime.utcnow)
