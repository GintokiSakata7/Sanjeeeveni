from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from database import get_supabase
from supabase import Client
from app.models.hospital_models import SOSRequest, Doctor, Driver, Ambulance, SOSTimeline, Helper, HelperNotification
import math

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
    ambulance_id: str

class AssignDoctorPayload(BaseModel):
    doctor_id: str

class TimelinePayload(BaseModel):
    event_type: str
    actor_role: str
    actor_id: Optional[str] = None
    actor_name: Optional[str] = None
    message: str
    metadata: Optional[dict] = {}

@router.post("/send", status_code=status.HTTP_201_CREATED)
def send_sos_to_hospital(payload: SOSSendPayload, db: Client = Depends(get_supabase)):
    """Called by the Citizen Frontend when the radar discovers a hospital."""
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

@router.get("/pending/{hospital_id}")
def get_pending_sos_requests(hospital_id: str, db: Client = Depends(get_supabase)):
    """Called by the Hospital Dashboard to check for incoming emergencies."""
    res = db.table("sos_requests").select("*").eq("hospital_id", hospital_id).eq("status", "PENDING").order("created_at", desc=True).execute()
    return res.data

@router.post("/respond/{sos_id}")
def respond_to_sos(sos_id: str, payload: SOSResponsePayload, db: Client = Depends(get_supabase)):
    """Called by the Hospital Dashboard to accept/reject an SOS."""
    res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="SOS request not found.")
    
    sos_request = res.data[0]
    if sos_request["status"] not in ["PENDING", "ACCEPTED"]:
        raise HTTPException(status_code=400, detail=f"SOS request is currently in status '{sos_request['status']}' and cannot be reassigned.")

    update_data = {
        "status": payload.status,
        "updated_at": datetime.utcnow().isoformat()
    }
    db.table("sos_requests").update(update_data).eq("id", sos_id).execute()

    # Add to timeline
    if payload.status == "ACCEPTED":
        tl = {
            "sos_id": sos_id,
            "event_type": "HOSPITAL_ACCEPTED",
            "actor_role": "hospital",
            "actor_id": sos_request["hospital_id"],
            "message": f"Hospital has ACCEPTED the emergency request.",
            "created_at": datetime.utcnow().isoformat()
        }
        db.table("sos_timelines").insert(tl).execute()

    return {"message": f"SOS request {payload.status}", "sos_id": sos_id}

@router.post("/assign-driver/{sos_id}")
def assign_driver(sos_id: str, payload: AssignDriverPayload, db: Client = Depends(get_supabase)):
    res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="SOS not found")
    sos = res.data[0]

    d_res = db.table("drivers").select("*").eq("id", payload.driver_id).execute()
    driver = d_res.data[0] if d_res.data else None

    a_res = db.table("ambulances").select("*").eq("id", payload.ambulance_id).execute()
    ambulance = a_res.data[0] if a_res.data else None

    if not driver or not ambulance:
        raise HTTPException(status_code=404, detail="Driver or Ambulance not found")

    update_data = {
        "assigned_driver_id": driver["id"],
        "assigned_driver_name": driver.get("name", "Unknown"),
        "assigned_ambulance_id": ambulance["id"],
        "assigned_ambulance_reg": ambulance.get("vehicle_registration", "Unknown"),
        "driver_status": "ASSIGNED",
        "updated_at": datetime.utcnow().isoformat()
    }

    db.table("sos_requests").update(update_data).eq("id", sos_id).execute()

    tl = {
        "sos_id": sos_id,
        "event_type": "DRIVER_ASSIGNED",
        "actor_role": "hospital",
        "message": f"Ambulance {ambulance.get('vehicle_registration')} with Driver {driver.get('name')} assigned.",
        "created_at": datetime.utcnow().isoformat()
    }
    db.table("sos_timelines").insert(tl).execute()

    return {"message": "Driver assigned successfully", "sos_id": sos_id}

@router.post("/assign-doctor/{sos_id}")
def assign_doctor(sos_id: str, payload: AssignDoctorPayload, db: Client = Depends(get_supabase)):
    sos = db.exec(select(SOSRequest).where(SOSRequest.id == sos_id)).first()
    if not sos:
        raise HTTPException(status_code=404, detail="SOS not found")

    doctor = db.exec(select(Doctor).where(Doctor.id == payload.doctor_id)).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    sos.assigned_doctor_id = doctor.id
    sos.assigned_doctor_name = doctor.name
    sos.doctor_status = "ASSIGNED"
    sos.updated_at = datetime.utcnow()
    
    doctor.status = "In Surgery"
    db.add(doctor)
    db.add(sos)

    tl = SOSTimeline(
        sos_id=sos.id,
        event_type="DOCTOR_ASSIGNED",
        actor_role="hospital",
        message=f"Dr. {doctor.name} assigned to emergency."
    )
    db.add(tl)
    db.commit()
    db.refresh(sos)

    return {"message": "Doctor assigned successfully", "sos": sos}

@router.post("/driver-accept/{sos_id}")
def driver_accept_sos(sos_id: str, db: Client = Depends(get_supabase)):
    sos = db.exec(select(SOSRequest).where(SOSRequest.id == sos_id)).first()
    if not sos:
        raise HTTPException(status_code=404, detail="SOS not found")

    sos.driver_status = "EN_ROUTE"
    sos.updated_at = datetime.utcnow()
    db.add(sos)

    tl = SOSTimeline(
        sos_id=sos.id,
        event_type="DRIVER_ACCEPTED",
        actor_role="driver",
        actor_id=sos.assigned_driver_id,
        actor_name=sos.assigned_driver_name,
        message=f"Driver has accepted and is En Route."
    )
    db.add(tl)
    db.commit()
    db.refresh(sos)

    return {"message": "Driver accepted mission", "sos": sos}

@router.get("/timeline/{sos_id}")
def get_sos_timeline(sos_id: str, db: Client = Depends(get_supabase)):
    timeline = db.exec(
        select(SOSTimeline)
        .where(SOSTimeline.sos_id == sos_id)
        .order_by(SOSTimeline.created_at.asc())
    ).all()
    return timeline

@router.post("/timeline/{sos_id}")
def add_timeline_event(sos_id: str, payload: TimelinePayload, db: Client = Depends(get_supabase)):
    tl = SOSTimeline(
        sos_id=sos_id,
        event_type=payload.event_type,
        actor_role=payload.actor_role,
        actor_id=payload.actor_id,
        actor_name=payload.actor_name,
        message=payload.message,
        event_metadata=payload.metadata
    )
    db.add(tl)
    db.commit()
    db.refresh(tl)
    return tl

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
    sos = db.exec(select(SOSRequest).where(SOSRequest.id == sos_id)).first()
    if not sos:
        raise HTTPException(status_code=404, detail="SOS not found")

    helpers = db.exec(select(Helper).where(Helper.is_active == True)).all()
    notified_count = 0
    radius_km = 5.0

    for h in helpers:
        if h.location:
            try:
                h_lat, h_lng = map(float, h.location.split(","))
                dist = haversine(sos.citizen_lat, sos.citizen_lng, h_lat, h_lng)
                if dist <= radius_km:
                    hn = HelperNotification(sos_id=sos.id, helper_id=h.id)
                    db.add(hn)
                    notified_count += 1
            except Exception:
                pass

    if notified_count > 0:
        tl = SOSTimeline(
            sos_id=sos.id,
            event_type="HELPER_NOTIFIED",
            actor_role="system",
            message=f"{notified_count} nearby helpers notified."
        )
        db.add(tl)

    db.commit()
    return {"message": f"Notified {notified_count} nearby helpers"}

@router.get("/status/{sos_id}")
def check_sos_status(sos_id: str, db: Client = Depends(get_supabase)):
    """Called by the Citizen Frontend to poll for hospital response."""
    res = db.table("sos_requests").select("*").eq("id", sos_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="SOS request not found.")
    
    sos_request = res.data[0]
    
    return {
        "sos_id": sos_request["id"],
        "status": sos_request["status"],
        "assigned_driver_name": sos_request.get("assigned_driver_name"),
        "assigned_ambulance_reg": sos_request.get("assigned_ambulance_reg"),
        "driver_status": sos_request.get("driver_status")
    }
