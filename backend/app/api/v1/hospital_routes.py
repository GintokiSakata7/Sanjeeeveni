from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from supabase import Client
from database import get_supabase
from app.schemas.hospital_schemas import (
    HospitalRegistrationCreate, HospitalLoginRequest, TokenResponse,
    HospitalProfileResponse
)
from app.services.hospital_service import HospitalService
from app.storage.storage_service import storage_service

router = APIRouter(prefix="/hospital", tags=["Hospital Management"])

def _network_error_response(e):
    """Returns 503 for network/DNS errors so the frontend falls back to Render."""
    err_str = str(e).lower()
    is_network_err = any(k in err_str for k in ["getaddrinfo", "connecterror", "connection", "timeout", "network"])
    if is_network_err:
        return JSONResponse(
            status_code=503,
            content={"detail": "Supabase unreachable from local server. Retrying via cloud backend."}
        )
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_hospital(
    payload: HospitalRegistrationCreate,
    db: Client = Depends(get_supabase)
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
    db: Client = Depends(get_supabase)
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
    db: Client = Depends(get_supabase)
):
    """Public endpoint to check the verification status of a registered hospital"""
    try:
        service = HospitalService(db)
        profile = service.get_hospital_profile(hospital_id)
        return {
            "hospital_id": profile["id"],
            "hospital_name": profile["name"],
            "status": profile["status"],
            "hospital_type": profile["hospital_type"],
            "created_at": profile["created_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        return _network_error_response(e)

@router.get("/profile/{hospital_id}")
def get_hospital_profile(
    hospital_id: str,
    db: Client = Depends(get_supabase)
):
    """Retrieves complete profile details for a hospital"""
    try:
        service = HospitalService(db)
        return service.get_hospital_profile(hospital_id)
    except HTTPException:
        raise
    except Exception as e:
        return _network_error_response(e)

@router.get("/all")
def get_all_hospitals(db: Client = Depends(get_supabase)):
    """Retrieves all hospitals with their location data for the radar."""
    try:
        hospitals_res = db.table("hospitals").select("*").execute()
        addresses_res = db.table("hospital_addresses").select("*").execute()

        hospitals = hospitals_res.data if hospitals_res.data else []
        addresses = {addr["hospital_id"]: addr for addr in (addresses_res.data if addresses_res.data else [])}

        results = []
        for h in hospitals:
            addr = addresses.get(h["id"])
            results.append({
                "id": h["id"],
                "name": h["name"],
                "category": h.get("category"),
                "status": h.get("status"),
                "latitude": h.get("latitude") or (addr["latitude"] if addr else None),
                "longitude": h.get("longitude") or (addr["longitude"] if addr else None),
                "complete_address": addr["complete_address"] if addr else None
            })
        return results
    except Exception as e:
        return _network_error_response(e)
