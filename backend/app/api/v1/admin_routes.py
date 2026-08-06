from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import Optional, List
import uuid

from database import get_session
from app.models.hospital_models import Hospital, HospitalVerification, HospitalDetails, VerificationStatusEnum
from app.repositories.hospital_repository import HospitalRepository
from app.schemas.admin_schemas import (
    AdminLoginRequest, AdminTokenResponse, HospitalVerifyActionPayload, AdminStatsResponse
)
from app.auth.security import create_access_token

router = APIRouter(prefix="/admin", tags=["Super Admin Orchestration"])

SUPER_ADMIN_EMAIL = "admin@sanjeevani.com"
SUPER_ADMIN_PASSWORD = "SanjeevaniAdmin2026!"

@router.post("/login", response_model=AdminTokenResponse)
def admin_login(credentials: AdminLoginRequest):
    """
    Authenticates Sanjeevani Super Admin.
    Default credentials: admin@sanjeevani.com / SanjeevaniAdmin2026!
    """
    if credentials.email.lower().strip() != SUPER_ADMIN_EMAIL.lower() or credentials.password != SUPER_ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Super Admin credentials."
        )

    token_data = {
        "sub": "SUPER_ADMIN",
        "email": SUPER_ADMIN_EMAIL,
        "role": "SUPER_ADMIN"
    }
    access_token = create_access_token(data=token_data)

    return AdminTokenResponse(
        access_token=access_token,
        token_type="bearer",
        admin_name="Sanjeevani Central Command Admin",
        email=SUPER_ADMIN_EMAIL
    )

@router.get("/stats", response_model=AdminStatsResponse)
def get_network_stats(db: Session = Depends(get_session)):
    """Retrieves overall network statistics for the Admin Dashboard"""
    repo = HospitalRepository(db)
    all_hospitals = db.exec(select(Hospital)).all()

    total = len(all_hospitals)

    def get_status_str(h):
        if hasattr(h.status, 'value'):
            return str(h.status.value)
        return str(h.status)

    pending = len([h for h in all_hospitals if get_status_str(h) == "PENDING_VERIFICATION"])
    approved = len([h for h in all_hospitals if get_status_str(h) == "APPROVED"])
    rejected = len([h for h in all_hospitals if get_status_str(h) == "REJECTED"])

    details_list = db.exec(select(HospitalDetails)).all()
    total_beds = sum(d.total_beds for d in details_list if d.total_beds)
    total_icu = sum(d.icu_beds for d in details_list if d.icu_beds)
    total_ambulances = sum(d.ambulance_count for d in details_list if d.ambulance_count)

    return AdminStatsResponse(
        total_hospitals=total,
        pending_verifications=pending,
        approved_hospitals=approved,
        rejected_hospitals=rejected,
        total_beds=total_beds,
        total_icu_beds=total_icu,
        total_ambulances=total_ambulances
    )

@router.get("/hospitals")
def list_all_hospitals_admin(
    status: Optional[str] = Query(None, description="Filter by status: PENDING_VERIFICATION, APPROVED, REJECTED"),
    query: Optional[str] = Query(None, description="Search by hospital name or registration number"),
    db: Session = Depends(get_session)
):
    """
    Returns full list of registered hospital applications with complete profiles for administrative monitoring.
    """
    repo = HospitalRepository(db)
    all_hospitals = db.exec(select(Hospital)).all()

    filtered = all_hospitals
    if status:
        filtered = [h for h in filtered if (hasattr(h.status, 'value') and h.status.value == status) or str(h.status) == status]
    if query:
        q_str = query.lower().strip()
        filtered = [h for h in filtered if (h.name and q_str in h.name.lower()) or (h.registration_number and q_str in h.registration_number.lower())]

    result_list = []
    for h in filtered:
        try:
            profile = repo.get_full_profile(h.id)
            if profile:
                result_list.append(profile)
            else:
                result_list.append({
                    "id": h.id,
                    "name": h.name or "Unnamed Hospital",
                    "hospital_type": h.hospital_type or "SMALL",
                    "category": h.category or "CHC",
                    "registration_number": h.registration_number or "N/A",
                    "license_number": h.license_number or "N/A",
                    "status": h.status or "PENDING_VERIFICATION",
                    "created_at": h.created_at,
                    "address": {},
                    "administrator": {},
                    "capacity": {},
                    "documents": {},
                    "integration": {}
                })
        except Exception as e:
            print(f"Profile build note for hospital {h.id}: {e}")
            result_list.append({
                "id": h.id,
                "name": h.name or "Hospital",
                "registration_number": h.registration_number or "N/A",
                "status": h.status or "PENDING_VERIFICATION"
            })

    return {
        "count": len(result_list),
        "hospitals": result_list
    }

@router.get("/hospital-detail/{hospital_id}")
def get_hospital_full_submission(hospital_id: str, db: Session = Depends(get_session)):
    """Retrieves full submission details for administrative review"""
    repo = HospitalRepository(db)
    profile = repo.get_full_profile(hospital_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return profile

@router.post("/verify-hospital/{hospital_id}")
def verify_hospital_action(
    hospital_id: str,
    action_payload: HospitalVerifyActionPayload,
    db: Session = Depends(get_session)
):
    """
    Approves or Rejects a hospital registration request.
    Updates status in hospitals table and appends administrative review audit note.
    """
    repo = HospitalRepository(db)
    hospital = repo.get_by_id(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital record not found")

    if isinstance(action_payload.status, str):
        target_status = VerificationStatusEnum(action_payload.status)
    else:
        target_status = action_payload.status

    hospital.status = target_status
    db.add(hospital)

    verif = HospitalVerification(
        id=f"VERIF-{uuid.uuid4().hex[:12].upper()}",
        hospital_id=hospital_id,
        verification_status=target_status,
        reviewed_by="admin@sanjeevani.com",
        review_notes=action_payload.notes or f"Application set to {target_status.value} by Super Admin."
    )
    db.add(verif)
    db.commit()

    return {
        "success": True,
        "message": f"Hospital '{hospital.name}' has been updated to {target_status.value}.",
        "hospital_id": hospital.id,
        "new_status": target_status.value
    }
