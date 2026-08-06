from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.hospital_models import HospitalTypeEnum, HospitalCategoryEnum, IntegrationModeEnum, VerificationStatusEnum

# --- Step 1 Schema ---
class BasicInfoSchema(BaseModel):
    hospital_name: str = Field(..., min_length=2, description="Full registered hospital name")
    hospital_type: HospitalTypeEnum = Field(default=HospitalTypeEnum.SMALL)
    category: HospitalCategoryEnum = Field(default=HospitalCategoryEnum.CHC)
    registration_number: Optional[str] = Field(default="REG-PENDING")
    license_number: Optional[str] = Field(default="LIC-PENDING")
    has_nabh_accreditation: bool = Field(default=False)
    nabh_number: Optional[str] = None
    gst_number: Optional[str] = None

# --- Step 2 Schema ---
class AddressSchema(BaseModel):
    country: str = Field(default="India")
    state: Optional[str] = Field(default="Telangana")
    district: Optional[str] = Field(default="Hyderabad")
    city: Optional[str] = Field(default="Hyderabad")
    area: Optional[str] = Field(default="Hyderabad")
    pincode: Optional[str] = Field(default="500001")
    complete_address: Optional[str] = Field(default="Hyderabad, Telangana")
    latitude: float = Field(default=17.4126)
    longitude: float = Field(default=78.4482)

# --- Step 3 Schema ---
class HospitalCapacitySchema(BaseModel):
    total_beds: int = Field(default=0, ge=0)
    icu_beds: int = Field(default=0, ge=0)
    has_emergency_dept: bool = Field(default=True)
    has_trauma_center: bool = Field(default=False)
    has_blood_bank: bool = Field(default=False)
    ambulance_count: int = Field(default=0, ge=0)
    departments: List[str] = Field(default_factory=list)
    specializations: List[str] = Field(default_factory=list)

# --- Step 4 Schema ---
class AdministratorSchema(BaseModel):
    name: str = Field(..., min_length=2)
    designation: Optional[str] = Field(default="Administrator")
    email: EmailStr
    mobile: Optional[str] = Field(default="+919999999999")
    password: str = Field(..., min_length=6)

# --- Step 5 Schema ---
class DocumentUrlsSchema(BaseModel):
    registration_cert_url: Optional[str] = Field(default="")
    govt_license_url: Optional[str] = Field(default="")
    nabh_cert_url: Optional[str] = Field(default=None)
    pan_url: Optional[str] = Field(default="")
    gst_url: Optional[str] = Field(default=None)
    exterior_image_url: Optional[str] = Field(default="")
    logo_url: Optional[str] = Field(default="")

# --- Step 6 Schema ---
class IntegrationConfigSchema(BaseModel):
    integration_mode: IntegrationModeEnum = Field(default=IntegrationModeEnum.DASHBOARD)
    base_url: Optional[str] = None
    callback_url: Optional[str] = None
    api_doc_url: Optional[str] = None
    tech_contact_name: Optional[str] = None
    tech_contact_email: Optional[str] = None

# --- Full Hospital Registration Request Payload ---
class HospitalRegistrationCreate(BaseModel):
    basic_info: BasicInfoSchema
    address: AddressSchema
    capacity: HospitalCapacitySchema
    administrator: AdministratorSchema
    documents: DocumentUrlsSchema
    integration: IntegrationConfigSchema

# --- Hospital Registration Response Schema ---
class HospitalRegistrationResponse(BaseModel):
    success: bool = True
    message: str
    hospital_id: str
    status: VerificationStatusEnum
    hospital_name: str

# --- Login Request & Response Schemas ---
class HospitalLoginRequest(BaseModel):
    email: EmailStr
    password: str

class HospitalLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    hospital_id: str
    hospital_name: str
    admin_name: str
    status: VerificationStatusEnum
    hospital_type: HospitalTypeEnum

# Backward compatibility aliases
TokenResponse = HospitalLoginResponse

class HospitalProfileResponse(BaseModel):
    id: str
    name: str
    hospital_type: Optional[HospitalTypeEnum] = None
    category: Optional[HospitalCategoryEnum] = None
    registration_number: Optional[str] = None
    license_number: Optional[str] = None
    status: Optional[VerificationStatusEnum] = None
    created_at: Optional[datetime] = None
    address: Optional[dict] = None
    administrator: Optional[dict] = None
    capacity: Optional[dict] = None
    documents: Optional[dict] = None
    integration: Optional[dict] = None

