"""
Mobile Authentication API Routes - Supabase REST Version
- Doctor login (credentials from HMS admin)
- Driver login (credentials from HMS admin)
- Helper self-registration
- Helper login
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime

from database import get_supabase
from supabase import Client
from app.schemas.mobile_auth_schemas import (
    DoctorLoginRequest, DriverLoginRequest,
    HelperRegisterRequest, HelperLoginRequest,
    MobileAuthResponse
)
from app.auth.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/mobile", tags=["Mobile App Authentication"])


def _net_err(e):
    err_str = str(e).lower()
    is_network = any(k in err_str for k in ["getaddrinfo", "connecterror", "connection", "timeout", "network", "errno 11001"])
    if is_network:
        return JSONResponse(status_code=503, content={"detail": "Supabase unreachable. Retrying via cloud backend."})
    raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────
# 👨‍⚕️ DOCTOR LOGIN
# ──────────────────────────────────────────
@router.post("/login/doctor", response_model=MobileAuthResponse)
def login_doctor(payload: DoctorLoginRequest, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        identifier = payload.identifier.strip()
        ident_lower = identifier.lower()

        # Fetch all doctors and filter in Python (Supabase REST doesn't support OR filters easily)
        all_docs = db.table("doctors").select("*").execute().data or []
        doctor = None
        for d in all_docs:
            if (d.get("email") and d["email"].lower() == ident_lower) or \
               (d.get("contact_number") and d["contact_number"].strip() == identifier) or \
               (d.get("id") and d["id"].lower() == ident_lower):
                doctor = d
                break

        if not doctor:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"No doctor account found matching '{identifier}'.")

        if not doctor.get("password_hash"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Doctor account has no password set. Contact hospital admin.")

        if not verify_password(payload.password, doctor["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password.")

        if not doctor.get("is_active", True):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor account is deactivated.")

        hospital_name = "Unknown Hospital"
        hosp = db.table("hospitals").select("name").eq("id", doctor["hospital_id"]).execute().data
        if hosp:
            hospital_name = hosp[0]["name"]

        token = create_access_token(data={"sub": doctor["id"], "role": "doctor", "hospital_id": doctor["hospital_id"]})

        return MobileAuthResponse(
            success=True, token=token, role="doctor",
            user_id=doctor["id"], user_name=doctor["name"],
            hospital_id=doctor["hospital_id"], hospital_name=hospital_name,
            specialization=doctor.get("specialization"),
            contact_number=doctor.get("contact_number"),
            email=doctor.get("email"),
            shift_timing=doctor.get("shift_timing")
        )
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


# ──────────────────────────────────────────
# 🚘 DRIVER LOGIN
# ──────────────────────────────────────────
@router.post("/login/driver", response_model=MobileAuthResponse)
def login_driver(payload: DriverLoginRequest, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        identifier = payload.identifier.strip()
        ident_lower = identifier.lower()

        all_drivers = db.table("drivers").select("*").execute().data or []
        driver = None
        for drv in all_drivers:
            if (drv.get("contact_number") and drv["contact_number"].strip() == identifier) or \
               (drv.get("email") and drv["email"].lower() == ident_lower) or \
               (drv.get("id") and drv["id"].lower() == ident_lower):
                driver = drv
                break

        if not driver:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"No driver account found matching '{identifier}'.")

        if not driver.get("password_hash"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Driver account has no password set. Contact hospital admin.")

        if not verify_password(payload.password, driver["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password.")

        hospital_name = "Unknown Hospital"
        hosp = db.table("hospitals").select("name").eq("id", driver["hospital_id"]).execute().data
        if hosp:
            hospital_name = hosp[0]["name"]

        token = create_access_token(data={"sub": driver["id"], "role": "driver", "hospital_id": driver["hospital_id"]})

        return MobileAuthResponse(
            success=True, token=token, role="driver",
            user_id=driver["id"], user_name=driver["name"],
            hospital_id=driver["hospital_id"], hospital_name=hospital_name,
            contact_number=driver.get("contact_number"),
            email=driver.get("email"),
            license_number=driver.get("license_number"),
            badge_id=driver["id"],
            shift_timing=driver.get("shift_timing")
        )
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


# ──────────────────────────────────────────
# 🤝 HELPER REGISTRATION
# ──────────────────────────────────────────
@router.post("/register/helper", response_model=MobileAuthResponse, status_code=status.HTTP_201_CREATED)
def register_helper(payload: HelperRegisterRequest, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        existing = db.table("helpers").select("id").eq("phone", payload.phone.strip()).execute().data
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail=f"Phone '{payload.phone}' is already registered. Please login.")

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
            "cert_id": payload.cert_id,
            "skills": payload.skills or [],
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        db.table("helpers").insert(helper).execute()
        token = create_access_token(data={"sub": helper_id, "role": "helper"})

        return MobileAuthResponse(
            success=True, token=token, role="helper",
            user_id=helper_id, user_name=payload.name.strip(),
            contact_number=payload.phone.strip(),
            location=payload.location, role_type=payload.role_type
        )
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


# ──────────────────────────────────────────
# 🤝 HELPER LOGIN
# ──────────────────────────────────────────
@router.post("/login/helper", response_model=MobileAuthResponse)
def login_helper(payload: HelperLoginRequest, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        helpers = db.table("helpers").select("*").eq("phone", payload.phone.strip()).execute().data
        if not helpers:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No helper account found. Please register first.")
        helper = helpers[0]

        if not verify_password(payload.password, helper["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password.")

        if not helper.get("is_active", True):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated.")

        token = create_access_token(data={"sub": helper["id"], "role": "helper"})

        return MobileAuthResponse(
            success=True, token=token, role="helper",
            user_id=helper["id"], user_name=helper["name"],
            contact_number=helper["phone"],
            location=helper.get("location"), role_type=helper.get("role_type")
        )
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


# ──────────────────────────────────────────
# 🚨 DOCTOR ASSIGNED CASES (mobile polling)
# ──────────────────────────────────────────
@router.get("/doctor/assigned-cases/{doctor_id}")
def get_doctor_assigned_cases(doctor_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        clean_id = doctor_id.strip()
        ident_lower = clean_id.lower()

        # Resolve identifier to actual doctor ID
        all_docs = db.table("doctors").select("*").execute().data or []
        doctor = None
        for d in all_docs:
            if (d.get("id") and d["id"].lower() == ident_lower) or \
               (d.get("email") and d["email"].lower() == ident_lower) or \
               (d.get("contact_number") and d["contact_number"].strip() == clean_id):
                doctor = d
                break

        target_id = doctor["id"] if doctor else clean_id

        sos_items = db.table("sos_requests").select("*").eq("assigned_doctor_id", target_id).order("updated_at", desc=True).execute().data or []

        hospital_name = "Emergency Trauma Center"
        if doctor:
            hosp = db.table("hospitals").select("name").eq("id", doctor["hospital_id"]).execute().data
            if hosp:
                hospital_name = hosp[0]["name"]

        cases = []
        for sos in sos_items:
            cases.append({
                "id": sos["id"],
                "patient_name": f"Emergency Victim ({sos['id'][-4:]})",
                "patient_age": 45,
                "patient_gender": "Emergency Intake",
                "blood_group": "O+",
                "emergency_type": sos.get("transcript", "Severe Trauma Emergency"),
                "severity": sos.get("triage_urgency", "CRITICAL"),
                "location_address": f"GPS ({sos['citizen_lat']:.4f}° N, {sos['citizen_lng']:.4f}° E)",
                "latitude": sos["citizen_lat"],
                "longitude": sos["citizen_lng"],
                "distance_km": 1.5,
                "eta_minutes": 5,
                "vitals": {"Pulse": "115 bpm", "BP": "98/62 mmHg", "SpO2": "94%", "Resp Rate": "22 /min"},
                "reported_symptoms": [sos.get("transcript", "Citizen SOS"), f"Status: {sos.get('status', 'PENDING')}"],
                "assigned_ambulance_unit": sos.get("assigned_ambulance_reg", "ALS-108"),
                "assigned_hospital": hospital_name,
                "caller_phone": "+91 98765 43210",
                "status": sos.get("status"),
                "timestamp": sos.get("updated_at") or sos.get("created_at")
            })

        return {"total": len(cases), "cases": cases}
    except Exception as e:
        return _net_err(e)


@router.post("/doctor/accept-case/{sos_id}")
def accept_doctor_case(sos_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        sos = db.table("sos_requests").select("id").eq("id", sos_id).execute().data
        if not sos:
            raise HTTPException(status_code=404, detail="SOS case not found")

        db.table("sos_requests").update({"status": "DOCTOR_ACCEPTED", "updated_at": datetime.utcnow().isoformat()}).eq("id", sos_id).execute()
        return {"success": True, "message": f"Case {sos_id} accepted. ER Trauma Bay reserved.", "status": "DOCTOR_ACCEPTED"}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


# ──────────────────────────────────────────
# 🚑 LIVE CASES FOR DRIVER / HELPER
# ──────────────────────────────────────────
@router.get("/cases/live")
def get_live_cases(db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        sos_items = db.table("sos_requests").select("*").order("created_at", desc=True).execute().data or []
        cases = []
        for sos in sos_items:
            cases.append({
                "id": sos["id"],
                "patient_name": f"Emergency Patient ({sos['id'][-4:]})",
                "emergency_type": sos.get("transcript", "Road Traffic Trauma"),
                "severity": sos.get("triage_urgency", "CRITICAL"),
                "latitude": sos["citizen_lat"],
                "longitude": sos["citizen_lng"],
                "status": sos.get("status"),
                "timestamp": sos.get("created_at")
            })
        return {"total": len(cases), "cases": cases}
    except Exception as e:
        return _net_err(e)


@router.get("/driver/assigned-cases/{driver_id}")
def get_driver_assigned_cases(driver_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        sos_items = db.table("sos_requests").select("*").eq("assigned_driver_id", driver_id).order("updated_at", desc=True).execute().data or []
        cases = []
        for sos in sos_items:
            cases.append({
                "id": sos["id"],
                "patient_name": f"Victim ({sos['id'][-4:]})",
                "emergency_type": sos.get("transcript", "Trauma"),
                "severity": sos.get("triage_urgency", "CRITICAL"),
                "latitude": sos["citizen_lat"],
                "longitude": sos["citizen_lng"],
                "status": sos.get("driver_status"),
                "timestamp": sos.get("updated_at") or sos.get("created_at")
            })
        return {"total": len(cases), "cases": cases}
    except Exception as e:
        return _net_err(e)


@router.get("/helper/nearby-alerts/{helper_id}")
def get_helper_alerts(helper_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        notifs = db.table("helper_notifications").select("*").eq("helper_id", helper_id).order("created_at", desc=True).execute().data or []
        formatted = []
        for notif in notifs:
            sos_res = db.table("sos_requests").select("*").eq("id", notif["sos_id"]).execute().data
            if not sos_res:
                continue
            sos = sos_res[0]
            formatted.append({
                "id": sos.get("id"),
                "notification_id": notif["id"],
                "status": notif["status"],
                "patient_name": "Emergency Victim",
                "patient_age": 45,
                "patient_gender": "Unknown",
                "blood_group": "O+",
                "emergency_type": sos.get("transcript", "Emergency Intake"),
                "severity": sos.get("severity", "HIGH"),
                "latitude": sos.get("citizen_lat"),
                "longitude": sos.get("citizen_lng"),
                "location_address": "Emergency Scene Coordinates",
                "distance_km": 1.5,
                "eta_minutes": 5,
                "assigned_ambulance_unit": sos.get("assigned_ambulance_reg", "None"),
                "assigned_hospital": "None",
                "caller_phone": "+91 98765 43210",
                "timestamp": notif.get("created_at")
            })
        return {"total": len(formatted), "alerts": formatted}
    except Exception as e:
        return _net_err(e)


from pydantic import BaseModel

class NotifyHelperPayload(BaseModel):
    sos_id: str
    helper_id: str

import uuid

@router.post("/helper/notify")
def helper_notify(payload: NotifyHelperPayload, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        notif = {
            "id": f"NOTIF-{str(uuid.uuid4())[:8].upper()}",
            "sos_id": payload.sos_id,
            "helper_id": payload.helper_id,
            "status": "PENDING",
            "created_at": datetime.utcnow().isoformat()
        }
        res = db.table("helper_notifications").insert(notif).execute()
        return {"success": True, "notification": res.data[0] if res.data else None}
    except Exception as e:
        return _net_err(e)

@router.post("/helper/accept/{notification_id}")
def accept_helper_alert(notification_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        notifs = db.table("helper_notifications").select("*").eq("id", notification_id).execute().data
        if not notifs:
            raise HTTPException(status_code=404, detail="Notification not found")
        notif = notifs[0]
        
        db.table("helper_notifications").update({"status": "ACCEPTED"}).eq("id", notification_id).execute()
        
        helpers = db.table("helpers").select("name").eq("id", notif["helper_id"]).execute().data
        helper_name = helpers[0]["name"] if helpers else "Unknown Helper"
        
        db.table("sos_requests").update({
            "status": "HELPER_ACCEPTED",
            "assigned_helper_id": notif["helper_id"],
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", notif["sos_id"]).execute()
        
        tl = {
            "sos_id": notif["sos_id"],
            "event_type": "HELPER_RESPONDING",
            "actor_role": "helper",
            "actor_id": notif["helper_id"],
            "actor_name": helper_name,
            "message": f"Community Helper {helper_name} accepted the alert and is en route.",
            "created_at": datetime.utcnow().isoformat()
        }
        db.table("sos_timelines").insert(tl).execute()
        
        return {"success": True, "message": "Response logged and SOS updated."}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)

@router.post("/helper/reject/{notification_id}")
def reject_helper_alert(notification_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        db.table("helper_notifications").update({"status": "REJECTED"}).eq("id", notification_id).execute()
        return {"success": True, "message": "Notification rejected."}
    except Exception as e:
        return _net_err(e)
