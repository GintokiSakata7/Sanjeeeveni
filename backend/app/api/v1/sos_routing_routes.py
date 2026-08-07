from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from database import get_supabase
from supabase import Client
import math

# Import WebSocket manager for real-time status sync
from app.ws_manager import manager
import asyncio

router = APIRouter(prefix="/routing", tags=["SOS Emergency Routing"])

class SOSSendPayload(BaseModel):
    hospital_id: str
    citizen_lat: float
    citizen_lng: float
    transcript: str
    triage_urgency: str
    disease: Optional[str] = None
    image_url: Optional[str] = None

class SOSResponsePayload(BaseModel):
    status: str  # "ACCEPTED" or "REJECTED"

class AssignDriverPayload(BaseModel):
    driver_id: str
    ambulance_id: Optional[str] = None  # Optional — auto-resolved from driver's assigned ambulance

class AssignDoctorPayload(BaseModel):
    doctor_id: str
    user_id: Optional[str] = None  # Optional citizen/patient identifier

class TimelinePayload(BaseModel):
    event_type: str
    actor_role: str
    actor_id: Optional[str] = None
    actor_name: Optional[str] = None
    message: str
    metadata: Optional[dict] = {}

def _net_err(e):
    """Returns 503 for network/DNS/connection errors so apiClient.js falls back to Render."""
    err_str = str(e).lower()
    is_network = any(k in err_str for k in ["getaddrinfo", "connecterror", "connection", "timeout", "network", "errno 11001"])
    if is_network:
        return JSONResponse(
            status_code=503,
            content={"detail": "Supabase unreachable from local server. Retrying via cloud backend."}
        )
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/send", status_code=status.HTTP_201_CREATED)
def send_sos_to_hospital(payload: SOSSendPayload, db: Client = Depends(get_supabase)):
    """Called by the Citizen Frontend when the radar discovers a hospital."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        sos_id = f"SOS-{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.utcnow().isoformat()
        sos_request = {
            "id": sos_id,
            "hospital_id": payload.hospital_id,
            "citizen_lat": payload.citizen_lat,
            "citizen_lng": payload.citizen_lng,
            "transcript": payload.transcript,
            "triage_urgency": payload.triage_urgency,
            "disease": payload.disease,
            "image_url": payload.image_url,
            "status": "PENDING",
            "created_at": now_iso,
            "updated_at": now_iso
        }
        db.table("sos_requests").insert(sos_request).execute()
        return {"sos_id": sos_id, "message": "SOS request routed to hospital."}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)

@router.get("/pending/{hospital_id}")
def get_pending_sos_requests(hospital_id: str, db: Client = Depends(get_supabase)):
    """Called by the Hospital Dashboard to check for incoming emergencies."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("hospital_id", hospital_id).eq("status", "PENDING").order("created_at", desc=True).execute()
        return res.data
    except Exception as e:
        return _net_err(e)

@router.get("/active/{hospital_id}")
def get_active_sos(hospital_id: str, db: Client = Depends(get_supabase)):
    """Fetch all active (accepted/ongoing) SOS requests for a hospital."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("hospital_id", hospital_id).in_("status", ["ACCEPTED", "DOCTOR_ACCEPTED", "DISPATCHED", "IN_TRANSIT", "ARRIVED"]).order("updated_at", desc=True).execute()
        return res.data
    except Exception as e:
        return _net_err(e)

@router.post("/respond/{sos_id}")
def respond_to_sos(sos_id: str, payload: SOSResponsePayload, db: Client = Depends(get_supabase)):
    """Called by the Hospital Dashboard to accept/reject an SOS."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS request not found.")

        sos_request = res.data[0]
        current_status = sos_request["status"]
        
        # Idempotency: if already in the target status, just return success
        if current_status == payload.status:
            return {"message": f"SOS request already {payload.status}", "sos_id": sos_id}
        
        # Reject/REJECTED can come from PENDING or ACCEPTED states
        # Accept can only come from PENDING (or re-accepting from ACCEPTED is allowed above)
        terminal_statuses = ["COMPLETED", "CANCELLED", "DOCTOR_ACCEPTED", "DISPATCHED", "IN_TRANSIT", "ARRIVED"]
        if current_status in terminal_statuses and payload.status == "PENDING":
            raise HTTPException(status_code=400, detail=f"SOS request is currently in status '{current_status}' and cannot be reverted.")

        update_data = {"status": payload.status, "updated_at": datetime.utcnow().isoformat()}
        db.table("sos_requests").update(update_data).eq("id", sos_id).execute()

        if payload.status == "ACCEPTED":
            tl = {
                "sos_id": sos_id,
                "event_type": "HOSPITAL_ACCEPTED",
                "actor_role": "hospital",
                "actor_id": sos_request["hospital_id"],
                "message": "Hospital has ACCEPTED the emergency request.",
                "created_at": datetime.utcnow().isoformat()
            }
            db.table("sos_timelines").insert(tl).execute()
            
            # Send real-time update to the patient's tracker
            try:
                asyncio.run(manager.broadcast_to_sos(sos_id, {
                    "type": "STATUS_UPDATE",
                    "status": "ACCEPTED",
                    "message": tl["message"]
                }))
            except Exception:
                pass

        elif payload.status == "REJECTED":
            tl = {
                "sos_id": sos_id,
                "event_type": "HOSPITAL_REJECTED",
                "actor_role": "hospital",
                "actor_id": sos_request["hospital_id"],
                "message": "Hospital has rejected the emergency request. Searching for another hospital.",
                "created_at": datetime.utcnow().isoformat()
            }
            db.table("sos_timelines").insert(tl).execute()
            try:
                asyncio.run(manager.broadcast_to_sos(sos_id, {
                    "type": "STATUS_UPDATE",
                    "status": "REJECTED",
                    "message": tl["message"]
                }))
            except Exception:
                pass

        return {"message": f"SOS request {payload.status}", "sos_id": sos_id}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


# ==========================================
# 🚘 DRIVER TASK ASSIGNMENT (NEW: uses driver_tasks table)
# ==========================================

@router.post("/assign-driver/{sos_id}")
def assign_driver(sos_id: str, payload: AssignDriverPayload, db: Client = Depends(get_supabase)):
    """Hospital assigns a driver to an SOS. Creates a dedicated driver_tasks record."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS not found")
        sos = res.data[0]

        d_res = db.table("drivers").select("*").eq("id", payload.driver_id).execute()
        driver = d_res.data[0] if d_res.data else None
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        # Auto-resolve ambulance: check if an ambulance is assigned to this driver
        ambulance = None
        if payload.ambulance_id:
            a_res = db.table("ambulances").select("*").eq("id", payload.ambulance_id).execute()
            ambulance = a_res.data[0] if a_res.data else None
        else:
            # Look up ambulance assigned to this driver
            a_res = db.table("ambulances").select("*").eq("assigned_driver_id", payload.driver_id).execute()
            ambulance = a_res.data[0] if a_res.data else None

        # --- Create dedicated driver_tasks record ---
        task_id = f"DTASK-{uuid.uuid4().hex[:8].upper()}"
        driver_task = {
            "id": task_id,
            "sos_id": sos_id,
            "hospital_id": sos["hospital_id"],
            "driver_id": driver["id"],
            "ambulance_id": ambulance["id"] if ambulance else None,
            "status": "PENDING",
            "citizen_lat": sos["citizen_lat"],
            "citizen_lng": sos["citizen_lng"],
            "disease": sos.get("disease"),
            "transcript": sos.get("transcript"),
            "triage_urgency": sos.get("triage_urgency"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        db.table("driver_tasks").insert(driver_task).execute()

        # --- Also update sos_requests for backward compatibility ---
        update_data = {
            "assigned_driver_id": driver["id"],
            "assigned_driver_name": driver.get("name", "Unknown"),
            "driver_status": "ASSIGNED",
            "updated_at": datetime.utcnow().isoformat()
        }
        if ambulance:
            update_data["assigned_ambulance_id"] = ambulance["id"]
            update_data["assigned_ambulance_reg"] = ambulance.get("vehicle_registration", "Unknown")

        db.table("sos_requests").update(update_data).eq("id", sos_id).execute()

        amb_info = f" with Ambulance {ambulance.get('vehicle_registration')}" if ambulance else ""
        tl = {
            "sos_id": sos_id,
            "event_type": "DRIVER_ASSIGNED",
            "actor_role": "hospital",
            "message": f"Driver {driver.get('name')} assigned{amb_info}.",
            "created_at": datetime.utcnow().isoformat()
        }
        db.table("sos_timelines").insert(tl).execute()
        
        # Send real-time push to the driver's mobile app via WebSocket
        try:
            asyncio.run(manager.broadcast_to_driver(driver["id"], {
                "type": "NEW_TASK_ASSIGNED",
                "task_id": task_id,
                "sos_id": sos_id,
                "citizen_lat": sos["citizen_lat"],
                "citizen_lng": sos["citizen_lng"],
                "disease": sos.get("disease"),
                "transcript": sos.get("transcript"),
                "triage_urgency": sos.get("triage_urgency"),
                "ambulance_reg": ambulance.get("vehicle_registration") if ambulance else None,
                "message": tl["message"]
            }))
        except Exception:
            pass

        # Send real-time update to the patient's tracker
        try:
            asyncio.run(manager.broadcast_to_sos(sos_id, {
                "type": "DRIVER_DISPATCHED",
                "driver_name": driver.get('name'),
                "ambulance_reg": ambulance.get('vehicle_registration') if ambulance else 'N/A',
                "message": tl["message"]
            }))
        except Exception:
            pass
        
        return {"message": "Driver assigned successfully", "sos_id": sos_id, "task_id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.post("/driver-accept/{sos_id}")
def driver_accept_sos(sos_id: str, db: Client = Depends(get_supabase)):
    """Driver accepts the assigned task. Updates both driver_tasks and sos_requests."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS not found")
        sos = res.data[0]

        db.table("sos_requests").update({"driver_status": "EN_ROUTE", "updated_at": datetime.utcnow().isoformat()}).eq("id", sos_id).execute()

        # Note: driver_tasks stays PENDING until completed (accept just means en route)
        tl = {
            "sos_id": sos_id,
            "event_type": "DRIVER_ACCEPTED",
            "actor_role": "driver",
            "actor_id": sos.get("assigned_driver_id"),
            "actor_name": sos.get("assigned_driver_name"),
            "message": "Driver has accepted and is En Route.",
            "created_at": datetime.utcnow().isoformat()
        }
        db.table("sos_timelines").insert(tl).execute()
        
        # Send real-time update to the patient's tracker
        try:
            asyncio.run(manager.broadcast_to_sos(sos_id, {
                "type": "DRIVER_EN_ROUTE",
                "message": tl["message"]
            }))
        except Exception:
            pass
        
        return {"message": "Driver accepted mission", "sos_id": sos_id}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.post("/driver-reject/{sos_id}")
def driver_reject_sos(sos_id: str, db: Client = Depends(get_supabase)):
    """Driver rejects the assigned task. 
    Updates driver_tasks.status = 'REJECTED'. Hospital can reassign another driver."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS not found")
        sos = res.data[0]
        driver_id = sos.get("assigned_driver_id")

        if not driver_id:
            raise HTTPException(status_code=400, detail="No driver assigned to this SOS.")

        # Update driver_tasks status to REJECTED
        tasks = db.table("driver_tasks").select("id").eq("sos_id", sos_id).eq("driver_id", driver_id).eq("status", "PENDING").execute().data
        if tasks:
            db.table("driver_tasks").update({
                "status": "REJECTED",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", tasks[0]["id"]).execute()

        # Reset sos_requests driver assignment so hospital can reassign
        db.table("sos_requests").update({
            "assigned_driver_id": None,
            "assigned_driver_name": None,
            "assigned_ambulance_id": None,
            "assigned_ambulance_reg": None,
            "driver_status": "NOT_ASSIGNED",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", sos_id).execute()

        tl = {
            "sos_id": sos_id,
            "event_type": "DRIVER_REJECTED",
            "actor_role": "driver",
            "actor_id": driver_id,
            "actor_name": sos.get("assigned_driver_name"),
            "message": f"Driver {sos.get('assigned_driver_name', 'Unknown')} rejected the task. Hospital can reassign.",
            "created_at": datetime.utcnow().isoformat()
        }
        db.table("sos_timelines").insert(tl).execute()

        # Notify patient tracker
        try:
            asyncio.run(manager.broadcast_to_sos(sos_id, {
                "type": "DRIVER_REJECTED",
                "message": tl["message"]
            }))
        except Exception:
            pass

        return {"message": "Driver rejected task. Hospital can reassign.", "sos_id": sos_id}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.post("/driver-complete/{sos_id}")
def driver_complete_sos(sos_id: str, db: Client = Depends(get_supabase)):
    """Driver marks the task as completed. 
    Updates driver_tasks.status = 'COMPLETED'. Task disappears from mobile app."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS not found")
        sos = res.data[0]
        driver_id = sos.get("assigned_driver_id")

        if not driver_id:
            raise HTTPException(status_code=400, detail="No driver assigned to this SOS.")

        # Update driver_tasks status to COMPLETED
        tasks = db.table("driver_tasks").select("id").eq("sos_id", sos_id).eq("driver_id", driver_id).eq("status", "PENDING").execute().data
        if tasks:
            db.table("driver_tasks").update({
                "status": "COMPLETED",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", tasks[0]["id"]).execute()

        # Update sos_requests
        db.table("sos_requests").update({
            "driver_status": "ARRIVED",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", sos_id).execute()

        # Mark driver as Available again
        db.table("drivers").update({"status": "Available"}).eq("id", driver_id).execute()

        tl = {
            "sos_id": sos_id,
            "event_type": "DRIVER_COMPLETED",
            "actor_role": "driver",
            "actor_id": driver_id,
            "actor_name": sos.get("assigned_driver_name"),
            "message": f"Driver {sos.get('assigned_driver_name', 'Unknown')} completed the pickup.",
            "created_at": datetime.utcnow().isoformat()
        }
        db.table("sos_timelines").insert(tl).execute()

        # Notify patient tracker
        try:
            asyncio.run(manager.broadcast_to_sos(sos_id, {
                "type": "DRIVER_COMPLETED",
                "message": tl["message"]
            }))
        except Exception:
            pass

        return {"message": "Driver task completed", "sos_id": sos_id}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


# ==========================================
# 👨‍⚕️ DOCTOR ASSIGNMENT (NEW: uses doctor_assignments table)
# ==========================================

@router.post("/assign-doctor/{sos_id}")
def assign_doctor(sos_id: str, payload: AssignDoctorPayload, db: Client = Depends(get_supabase)):
    """Hospital assigns a doctor to an SOS. Creates a dedicated doctor_assignments record.
    Doctor CANNOT reject (hospital-assigned). Only PENDING → COMPLETED."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS not found")
        sos = res.data[0]

        doc_res = db.table("doctors").select("*").eq("id", payload.doctor_id).execute()
        if not doc_res.data:
            raise HTTPException(status_code=404, detail="Doctor not found")
        doctor = doc_res.data[0]

        # --- Create dedicated doctor_assignments record ---
        assignment_id = f"DASGN-{uuid.uuid4().hex[:8].upper()}"
        doctor_assignment = {
            "id": assignment_id,
            "sos_id": sos_id,
            "hospital_id": sos["hospital_id"],
            "doctor_id": doctor["id"],
            "user_id": payload.user_id,
            "status": "PENDING",
            "citizen_lat": sos["citizen_lat"],
            "citizen_lng": sos["citizen_lng"],
            "disease": sos.get("disease"),
            "transcript": sos.get("transcript"),
            "triage_urgency": sos.get("triage_urgency"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        db.table("doctor_assignments").insert(doctor_assignment).execute()

        # --- Also update sos_requests for backward compatibility ---
        sos_update = {
            "assigned_doctor_id": doctor["id"],
            "assigned_doctor_name": doctor.get("name", "Unknown"),
            "doctor_status": "ASSIGNED",
            "updated_at": datetime.utcnow().isoformat()
        }
        db.table("sos_requests").update(sos_update).eq("id", sos_id).execute()
        db.table("doctors").update({"status": "In Surgery"}).eq("id", payload.doctor_id).execute()

        tl = {
            "sos_id": sos_id,
            "event_type": "DOCTOR_ASSIGNED",
            "actor_role": "hospital",
            "message": f"Dr. {doctor.get('name')} assigned to emergency.",
            "created_at": datetime.utcnow().isoformat()
        }
        db.table("sos_timelines").insert(tl).execute()
        
        # Send real-time push to the doctor's mobile app via WebSocket
        try:
            asyncio.run(manager.broadcast_to_doctor(doctor["id"], {
                "type": "NEW_CASE_ASSIGNED",
                "assignment_id": assignment_id,
                "sos_id": sos_id,
                "citizen_lat": sos["citizen_lat"],
                "citizen_lng": sos["citizen_lng"],
                "disease": sos.get("disease"),
                "transcript": sos.get("transcript"),
                "triage_urgency": sos.get("triage_urgency"),
                "message": tl["message"]
            }))
        except Exception:
            pass

        # Send real-time update to the patient's tracker
        try:
            asyncio.run(manager.broadcast_to_sos(sos_id, {
                "type": "DOCTOR_ASSIGNED",
                "doctor_name": doctor.get('name'),
                "doctor_specialty": doctor.get('specialization', 'Emergency Physician'),
                "message": tl["message"]
            }))
        except Exception:
            pass
        
        return {"message": "Doctor assigned successfully", "sos_id": sos_id, "assignment_id": assignment_id}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


@router.post("/doctor-complete/{sos_id}")
def doctor_complete_sos(sos_id: str, db: Client = Depends(get_supabase)):
    """Doctor marks the assignment as completed.
    Updates doctor_assignments.status = 'COMPLETED'. Assignment disappears from mobile app."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS not found")
        sos = res.data[0]
        doctor_id = sos.get("assigned_doctor_id")

        if not doctor_id:
            raise HTTPException(status_code=400, detail="No doctor assigned to this SOS.")

        # Update doctor_assignments status to COMPLETED
        assignments = db.table("doctor_assignments").select("id").eq("sos_id", sos_id).eq("doctor_id", doctor_id).eq("status", "PENDING").execute().data
        if assignments:
            db.table("doctor_assignments").update({
                "status": "COMPLETED",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", assignments[0]["id"]).execute()

        # Update sos_requests
        db.table("sos_requests").update({
            "doctor_status": "COMPLETED",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", sos_id).execute()

        # Mark doctor as Available again
        db.table("doctors").update({"status": "Available"}).eq("id", doctor_id).execute()

        tl = {
            "sos_id": sos_id,
            "event_type": "DOCTOR_COMPLETED",
            "actor_role": "doctor",
            "actor_id": doctor_id,
            "actor_name": sos.get("assigned_doctor_name"),
            "message": f"Dr. {sos.get('assigned_doctor_name', 'Unknown')} completed the case.",
            "created_at": datetime.utcnow().isoformat()
        }
        db.table("sos_timelines").insert(tl).execute()

        # Notify patient tracker
        try:
            asyncio.run(manager.broadcast_to_sos(sos_id, {
                "type": "DOCTOR_COMPLETED",
                "message": tl["message"]
            }))
        except Exception:
            pass

        return {"message": "Doctor assignment completed", "sos_id": sos_id}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


# ==========================================
# 📋 TIMELINE
# ==========================================

@router.get("/timeline/{sos_id}")
def get_sos_timeline(sos_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_timelines").select("*").eq("sos_id", sos_id).order("created_at", desc=False).execute()
        return res.data
    except Exception as e:
        return _net_err(e)

@router.post("/timeline/{sos_id}")
def add_timeline_event(sos_id: str, payload: TimelinePayload, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        tl = {
            "sos_id": sos_id,
            "event_type": payload.event_type,
            "actor_role": payload.actor_role,
            "actor_id": payload.actor_id,
            "actor_name": payload.actor_name,
            "message": payload.message,
            "created_at": datetime.utcnow().isoformat()
        }
        res = db.table("sos_timelines").insert(tl).execute()
        return res.data[0] if res.data else tl
    except Exception as e:
        return _net_err(e)


# ==========================================
# 🤝 HELPER NOTIFICATIONS (enhanced with coordinates + disease)
# ==========================================

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@router.post("/notify-helpers/{sos_id}")
def notify_nearby_helpers(sos_id: str, db: Client = Depends(get_supabase)):
    """Notifies nearby helpers. Now includes citizen coordinates and disease info in the notification."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS not found")
        sos = res.data[0]

        helpers_res = db.table("helpers").select("*").eq("is_active", True).execute()
        helpers = helpers_res.data if helpers_res.data else []
        notified_count = 0
        radius_km = 5.0

        for h in helpers:
            if h.get("location"):
                try:
                    h_lat, h_lng = map(float, h["location"].split(","))
                    dist = haversine(sos["citizen_lat"], sos["citizen_lng"], h_lat, h_lng)
                    if dist <= radius_km:
                        # Insert enriched notification with coordinates + disease
                        notif = {
                            "sos_id": sos["id"],
                            "helper_id": h["id"],
                            "citizen_lat": sos["citizen_lat"],
                            "citizen_lng": sos["citizen_lng"],
                            "disease": sos.get("disease"),
                            "transcript": sos.get("transcript"),
                            "triage_urgency": sos.get("triage_urgency"),
                        }
                        db.table("helper_notifications").insert(notif).execute()
                        notified_count += 1

                        # Send real-time push to helper via WebSocket
                        try:
                            asyncio.run(manager.broadcast_to_helper(h["id"], {
                                "type": "SOS_ALERT",
                                "sos_id": sos["id"],
                                "citizen_lat": sos["citizen_lat"],
                                "citizen_lng": sos["citizen_lng"],
                                "disease": sos.get("disease"),
                                "transcript": sos.get("transcript"),
                                "triage_urgency": sos.get("triage_urgency"),
                                "message": f"Emergency nearby! {sos.get('transcript', 'Help needed')}"
                            }))
                        except Exception:
                            pass
                except Exception:
                    pass

        if notified_count > 0:
            tl = {
                "sos_id": sos["id"],
                "event_type": "HELPER_NOTIFIED",
                "actor_role": "system",
                "message": f"{notified_count} nearby helpers notified.",
                "created_at": datetime.utcnow().isoformat()
            }
            db.table("sos_timelines").insert(tl).execute()

        return {"message": f"Notified {notified_count} nearby helpers"}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)


# ==========================================
# 📊 STATUS & VOICE CALL
# ==========================================

@router.get("/status/{sos_id}")
def check_sos_status(sos_id: str, db: Client = Depends(get_supabase)):
    """Called by the Citizen Frontend to poll for hospital response."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS request not found.")

        sos_request = res.data[0]
        return {
            "sos_id": sos_request["id"],
            "status": sos_request["status"],
            "disease": sos_request.get("disease"),
            "doctor_status": sos_request.get("doctor_status"),
            "assigned_doctor_name": sos_request.get("assigned_doctor_name"),
            "assigned_doctor_id": sos_request.get("assigned_doctor_id"),
            "assigned_driver_name": sos_request.get("assigned_driver_name"),
            "assigned_ambulance_reg": sos_request.get("assigned_ambulance_reg"),
            "driver_status": sos_request.get("driver_status")
        }
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)

@router.post("/initiate-call/{sos_id}")
async def initiate_call(sos_id: str, db: Client = Depends(get_supabase)):
    """Called by the Hospital Dashboard 'Contact Doctor' button. 
    Sends an INITIATE_CALL WebSocket message to the patient's browser to start the WebRTC call."""
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("assigned_doctor_id, assigned_doctor_name").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS request not found.")
        
        sos = res.data[0]
        doctor_id = sos.get("assigned_doctor_id")
        doctor_name = sos.get("assigned_doctor_name", "Your Doctor")
        
        if not doctor_id:
            raise HTTPException(status_code=400, detail="No doctor assigned to this SOS request.")
        
        # Push INITIATE_CALL to the patient's WebSocket so IncomingCallModal appears
        await manager.broadcast_to_sos(sos_id, {
            "type": "INITIATE_CALL",
            "doctor_id": doctor_id,
            "name": doctor_name,
            "sdp": None  # Signaling will be exchanged over WS after patient accepts
        })
        
        # Also notify the doctor that hospital is trying to connect
        await manager.broadcast_to_doctor(doctor_id, {
            "type": "CALL_REQUESTED",
            "sos_id": sos_id,
            "message": "Hospital admin is connecting you to the patient."
        })
        
        return {"success": True, "message": f"Call initiated for SOS {sos_id}"}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)
