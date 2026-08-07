from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_supabase
from supabase import Client
from app.schemas.hms_schemas import (
    DoctorCreatePayload, DoctorUpdatePayload, DoctorResponse,
    DriverCreatePayload, DriverUpdatePayload, DriverResponse,
    AmbulanceCreatePayload, AmbulanceUpdatePayload, AmbulanceResponse,
    HMSOverviewStats
)
from app.auth.security import get_password_hash

router = APIRouter(prefix="/hms", tags=["Hospital Management System (HMS)"])


def _net_err(e):
    """Returns 503 for network/DNS errors so apiClient.js falls back to Render."""
    err_str = str(e).lower()
    is_network = any(k in err_str for k in ["getaddrinfo", "connecterror", "connection", "timeout", "network", "errno 11001"])
    if is_network:
        return JSONResponse(
            status_code=503,
            content={"detail": "Supabase unreachable from local server. Retrying via cloud backend."}
        )
    raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 📊 TELEMETRY OVERVIEW STATS
# ==========================================
@router.get("/overview-stats/{hospital_id}")
def get_hms_overview_stats(hospital_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        doctors = (db.table("doctors").select("status").eq("hospital_id", hospital_id).execute()).data or []
        drivers = (db.table("drivers").select("status").eq("hospital_id", hospital_id).execute()).data or []
        ambulances = (db.table("ambulances").select("status").eq("hospital_id", hospital_id).execute()).data or []

        return {
            "total_doctors": len(doctors),
            "available_doctors": len([d for d in doctors if d.get("status") == "Available"]),
            "in_surgery_doctors": len([d for d in doctors if d.get("status") == "In Surgery"]),
            "on_leave_doctors": len([d for d in doctors if d.get("status") == "On Leave"]),
            "total_drivers": len(drivers),
            "available_drivers": len([d for d in drivers if d.get("status") == "Available"]),
            "total_ambulances": len(ambulances),
            "available_ambulances": len([a for a in ambulances if a.get("status") == "Available"]),
            "dispatched_ambulances": len([a for a in ambulances if a.get("status") == "Dispatched"]),
        }
    except Exception as e:
        return _net_err(e)


# ==========================================
# 👨‍⚕️ DOCTORS CRUD
# ==========================================
@router.get("/doctors/{hospital_id}")
def list_doctors(hospital_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("doctors").select("*").eq("hospital_id", hospital_id).order("created_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        return _net_err(e)


@router.post("/doctors", status_code=status.HTTP_201_CREATED)
def create_doctor(payload: DoctorCreatePayload, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        # Check for duplicate email within same hospital
        existing = db.table("doctors").select("id").eq("hospital_id", payload.hospital_id).eq("email", payload.email).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A doctor with email '{payload.email}' is already registered at this hospital."
            )

        doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
        pwd_hash = get_password_hash(payload.password)
        now = datetime.utcnow().isoformat()

        doctor = {
            "id": doc_id,
            "hospital_id": payload.hospital_id,
            "name": payload.name,
            "specialization": payload.specialization,
            "contact_number": payload.contact_number,
            "email": payload.email,
            "password_hash": pwd_hash,
            "status": payload.status or "Available",
            "shift_timing": payload.shift_timing or "Morning Shift (08:00 AM - 04:00 PM)",
            "is_active": True,
            "created_at": now,
        }
        res = db.table("doctors").insert(doctor).execute()
        return res.data[0] if res.data else doctor
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: str, payload: DoctorUpdatePayload, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        existing = db.table("doctors").select("id").eq("id", doctor_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Doctor record not found")

        update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        res = db.table("doctors").update(update_data).eq("id", doctor_id).execute()
        return res.data[0] if res.data else {"id": doctor_id, **update_data}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        existing = db.table("doctors").select("id, name").eq("id", doctor_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Doctor record not found")
        name = existing.data[0].get("name", doctor_id)

        # Nullify any SOS references to avoid FK issues
        db.table("sos_requests").update({"assigned_doctor_id": None, "assigned_doctor_name": None}).eq("assigned_doctor_id", doctor_id).execute()
        db.table("doctors").delete().eq("id", doctor_id).execute()
        return {"success": True, "message": f"Doctor {name} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


# ==========================================
# 🚘 DRIVERS CRUD
# ==========================================
@router.get("/drivers/{hospital_id}")
def list_drivers(hospital_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("drivers").select("*").eq("hospital_id", hospital_id).order("created_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        return _net_err(e)


@router.post("/drivers", status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreatePayload, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        # Check for duplicate license number within same hospital
        existing = db.table("drivers").select("id").eq("hospital_id", payload.hospital_id).eq("license_number", payload.license_number).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A driver with license number '{payload.license_number}' is already registered at this hospital."
            )

        driver_id = f"DRV-{uuid.uuid4().hex[:8].upper()}"
        pwd_hash = get_password_hash(payload.password)
        now = datetime.utcnow().isoformat()

        driver = {
            "id": driver_id,
            "hospital_id": payload.hospital_id,
            "name": payload.name,
            "contact_number": payload.contact_number,
            "license_number": payload.license_number,
            "email": payload.email,
            "password_hash": pwd_hash,
            "status": payload.status or "Available",
            "shift_timing": payload.shift_timing or "Morning Shift (08:00 AM - 04:00 PM)",
            "created_at": now,
        }
        res = db.table("drivers").insert(driver).execute()
        return res.data[0] if res.data else driver
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.put("/drivers/{driver_id}")
def update_driver(driver_id: str, payload: DriverUpdatePayload, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        existing = db.table("drivers").select("id").eq("id", driver_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Driver record not found")

        update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        res = db.table("drivers").update(update_data).eq("id", driver_id).execute()
        return res.data[0] if res.data else {"id": driver_id, **update_data}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.delete("/drivers/{driver_id}")
def delete_driver(driver_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        existing = db.table("drivers").select("id, name").eq("id", driver_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Driver record not found")
        name = existing.data[0].get("name", driver_id)
        db.table("drivers").delete().eq("id", driver_id).execute()
        return {"success": True, "message": f"Driver {name} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


# ==========================================
# 🚑 AMBULANCES CRUD
# ==========================================
@router.get("/ambulances/{hospital_id}")
def list_ambulances(hospital_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("ambulances").select("*").eq("hospital_id", hospital_id).order("created_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        return _net_err(e)


@router.post("/ambulances", status_code=status.HTTP_201_CREATED)
def create_ambulance(payload: AmbulanceCreatePayload, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        amb_id = f"AMB-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.utcnow().isoformat()

        ambulance = {
            "id": amb_id,
            "hospital_id": payload.hospital_id,
            "vehicle_registration": payload.vehicle_registration,
            "vehicle_type": payload.vehicle_type or "Basic",
            "assigned_driver_id": payload.assigned_driver_id,
            "assigned_driver_name": payload.assigned_driver_name,
            "status": payload.status or "Available",
            "created_at": now,
        }
        res = db.table("ambulances").insert(ambulance).execute()
        return res.data[0] if res.data else ambulance
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.put("/ambulances/{ambulance_id}")
def update_ambulance(ambulance_id: str, payload: AmbulanceUpdatePayload, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        existing = db.table("ambulances").select("id").eq("id", ambulance_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Ambulance record not found")

        update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        res = db.table("ambulances").update(update_data).eq("id", ambulance_id).execute()
        return res.data[0] if res.data else {"id": ambulance_id, **update_data}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.delete("/ambulances/{ambulance_id}")
def delete_ambulance(ambulance_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        existing = db.table("ambulances").select("id, vehicle_registration").eq("id", ambulance_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Ambulance record not found")
        reg = existing.data[0].get("vehicle_registration", ambulance_id)
        db.table("ambulances").delete().eq("id", ambulance_id).execute()
        return {"success": True, "message": f"Ambulance {reg} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)
