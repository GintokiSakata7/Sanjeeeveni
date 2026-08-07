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
    image_url: Optional[str] = None

class SOSResponsePayload(BaseModel):
    status: str  # "ACCEPTED" or "REJECTED"

class AssignDriverPayload(BaseModel):
    driver_id: str
    ambulance_id: Optional[str] = None  # Optional — auto-resolved from driver's assigned ambulance

class AssignDoctorPayload(BaseModel):
    doctor_id: str

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

@router.post("/assign-driver/{sos_id}")
def assign_driver(sos_id: str, payload: AssignDriverPayload, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS not found")

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
        
        return {"message": "Driver assigned successfully", "sos_id": sos_id}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)

@router.post("/assign-doctor/{sos_id}")
def assign_doctor(sos_id: str, payload: AssignDoctorPayload, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS not found")

        doc_res = db.table("doctors").select("*").eq("id", payload.doctor_id).execute()
        if not doc_res.data:
            raise HTTPException(status_code=404, detail="Doctor not found")
        doctor = doc_res.data[0]

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
        
        # Send push notification via WebSocket to the assigned doctor
        try:
            asyncio.run(manager.broadcast_to_doctor(doctor["id"], {
                "type": "NEW_CASE_ASSIGNED",
                "sos_id": sos_id,
                "patient_name": res.data[0].get("patient_name", "Unknown Patient"),
                "severity": res.data[0].get("triage_urgency", "CRITICAL")
            }))
        except Exception:
            pass
        
        return {"message": "Doctor assigned successfully", "sos_id": sos_id}
    except HTTPException:
        raise
    except Exception as e:
        return _net_err(e)

@router.post("/driver-accept/{sos_id}")
def driver_accept_sos(sos_id: str, db: Client = Depends(get_supabase)):
    if not db:
        return JSONResponse(status_code=503, content={"detail": "Supabase client not initialized."})
    try:
        res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="SOS not found")
        sos = res.data[0]

        db.table("sos_requests").update({"driver_status": "EN_ROUTE", "updated_at": datetime.utcnow().isoformat()}).eq("id", sos_id).execute()

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
                        db.table("helper_notifications").insert({"sos_id": sos["id"], "helper_id": h["id"]}).execute()
                        notified_count += 1
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

