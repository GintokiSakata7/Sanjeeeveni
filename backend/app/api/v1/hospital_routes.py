from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlmodel import Session
from database import get_session
from app.schemas.hospital_schemas import (
    HospitalRegistrationCreate, HospitalLoginRequest, TokenResponse,
    HospitalProfileResponse
)
from app.services.hospital_service import HospitalService
from app.storage.storage_service import storage_service

router = APIRouter(prefix="/hospital", tags=["Hospital Management"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_hospital(
    payload: HospitalRegistrationCreate,
    db: Session = Depends(get_session)
):
    """
    Submits a complete 7-step Hospital Registration workflow.
    Validates hospital details, creates database entities, and sets initial status to PENDING_VERIFICATION.
    """
    service = HospitalService(db)
    return service.register_hospital(payload)

@router.post("/login", response_model=TokenResponse)
def login_hospital(
    credentials: HospitalLoginRequest,
    db: Session = Depends(get_session)
):
    """
    Authenticates a Hospital Administrator using email and password.
    Returns signed JWT bearer token and verification status.
    """
    service = HospitalService(db)
    return service.authenticate_hospital(credentials)

@router.post("/upload-doc")
async def upload_verification_document(
    file: UploadFile = File(...)
):
    """
    Uploads a verification document or image (Registration Cert, License, PAN, Exterior Photo, Logo).
    Returns file URL (Supabase Storage URL or local fallback endpoint).
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file payload provided.")

    allowed_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file.content_type}'. Allowed formats: JPG, PNG, WEBP, PDF."
        )

    file_url = await storage_service.upload_file(file, subfolder="verification_docs")
    return {
        "success": True,
        "filename": file.filename,
        "url": file_url
    }

@router.get("/verification-status/{hospital_id}")
def check_verification_status(
    hospital_id: str,
    db: Session = Depends(get_session)
):
    """Public endpoint to check the verification status of a registered hospital"""
    service = HospitalService(db)
    profile = service.get_hospital_profile(hospital_id)
    return {
        "hospital_id": profile["id"],
        "hospital_name": profile["name"],
        "status": profile["status"],
        "hospital_type": profile["hospital_type"],
        "created_at": profile["created_at"]
    }

@router.get("/profile/{hospital_id}")
def get_hospital_profile(
    hospital_id: str,
    db: Session = Depends(get_session)
):
    """Retrieves complete profile details for a hospital"""
    service = HospitalService(db)
    return service.get_hospital_profile(hospital_id)
