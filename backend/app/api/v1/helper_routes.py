"""
Helper (Community Worker) Authentication Routes - Supabase REST Version
Migrated from deprecated SQLModel get_session() to Supabase REST client.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_supabase
from supabase import Client
from app.auth.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/helpers", tags=["Community Helpers"])


class HelperRegisterRequest(BaseModel):
    name: str
    phone: str
    password: str
    role_type: str
    location: str
    certificate_id: Optional[str] = None
    skills: List[str] = []
    latitude: Optional[float] = 17.3850
    longitude: Optional[float] = 78.4867


class HelperLoginRequest(BaseModel):
    phone: str
    password: str


def _net_err(e):
    err_str = str(e).lower()
    is_network = any(k in err_str for k in ["getaddrinfo", "connecterror", "connection", "timeout", "network", "errno 11001"])
    if is_network:
        return JSONResponse(status_code=503, content={"detail": "Supabase unreachable. Retrying via cloud backend."})
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_helper(payload: HelperRegisterRequest, db: Client = Depends(get_supabase)):
    """Register a new community helper via Supabase REST."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        # Check if phone already exists
        existing = db.table("helpers").select("id").eq("phone", payload.phone.strip()).execute().data
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Phone '{payload.phone}' is already registered. Please login."
            )

        helper_id = f"HLP-{uuid.uuid4().hex[:8].upper()}"
        helper = {
            "id": helper_id,
            "name": payload.name.strip(),
            "phone": payload.phone.strip(),
            "password_hash": get_password_hash(payload.password),
            "location": payload.location,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "role_type": payload.role_type,
            "cert_id": payload.certificate_id,
            "skills": payload.skills or [],
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        db.table("helpers").insert(helper).execute()

        token = create_access_token(data={"sub": helper_id, "role": "helper"})
        return {
            "message": "Helper registered successfully",
            "user_id": helper_id,
            "name": payload.name.strip(),
            "token": token,
            "role": "helper"
        }
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.post("/login")
def login_helper(payload: HelperLoginRequest, db: Client = Depends(get_supabase)):
    """Login an existing community helper via Supabase REST."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        helpers = db.table("helpers").select("*").eq("phone", payload.phone.strip()).execute().data
        if not helpers:
            raise HTTPException(status_code=401, detail="No helper account found. Please register first.")
        helper = helpers[0]

        if not verify_password(payload.password, helper["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid phone number or password")

        if not helper.get("is_active", True):
            raise HTTPException(status_code=403, detail="Account deactivated.")

        token = create_access_token(data={"sub": helper["id"], "role": "helper"})

        return {
            "message": "Login successful",
            "user_id": helper["id"],
            "name": helper["name"],
            "token": token,
            "role": "helper",
            "role_type": helper.get("role_type"),
            "location": helper.get("location")
        }
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.get("/notifications/{helper_id}")
def get_helper_notifications_by_sos(helper_id: str, sos_id: Optional[str] = None, db: Client = Depends(get_supabase)):
    """Fetch helper notifications, optionally filtered by SOS ID.
    Returns enriched notifications with citizen coordinates and disease info."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        query = db.table("helper_notifications").select("*").eq("helper_id", helper_id)
        if sos_id:
            query = query.eq("sos_id", sos_id)
        notifs = query.order("created_at", desc=True).execute().data or []

        formatted = []
        for notif in notifs:
            formatted.append({
                "notification_id": notif["id"],
                "sos_id": notif["sos_id"],
                "status": notif["status"],
                "citizen_lat": notif.get("citizen_lat"),
                "citizen_lng": notif.get("citizen_lng"),
                "disease": notif.get("disease"),
                "transcript": notif.get("transcript"),
                "triage_urgency": notif.get("triage_urgency"),
                "timestamp": notif.get("created_at")
            })
        return {"total": len(formatted), "notifications": formatted}
    except Exception as e:
        return _net_err(e)
