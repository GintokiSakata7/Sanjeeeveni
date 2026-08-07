from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from database import get_session
from app.models.hospital_models import SOSRequest, Doctor

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
    doctor_id: Optional[str] = None

@router.post("/send", status_code=status.HTTP_201_CREATED)
def send_sos_to_hospital(payload: SOSSendPayload, db: Session = Depends(get_session)):
    """Called by the Citizen Frontend when the radar discovers a hospital."""
    sos_id = f"SOS-{uuid.uuid4().hex[:8].upper()}"
    sos_request = SOSRequest(
        id=sos_id,
        hospital_id=payload.hospital_id,
        citizen_lat=payload.citizen_lat,
        citizen_lng=payload.citizen_lng,
        transcript=payload.transcript,
        triage_urgency=payload.triage_urgency,
        image_url=payload.image_url,
        status="PENDING"
    )
    db.add(sos_request)
    db.commit()
    db.refresh(sos_request)
    return {"sos_id": sos_request.id, "message": "SOS request routed to hospital."}

@router.get("/pending/{hospital_id}")
def get_pending_sos_requests(hospital_id: str, db: Session = Depends(get_session)):
    """Called by the Hospital Dashboard to check for incoming emergencies."""
    requests = db.exec(
        select(SOSRequest)
        .where(SOSRequest.hospital_id == hospital_id)
        .where(SOSRequest.status == "PENDING")
        .order_by(SOSRequest.created_at.desc())
    ).all()
    return requests

@router.post("/respond/{sos_id}")
def respond_to_sos(sos_id: str, payload: SOSResponsePayload, db: Session = Depends(get_session)):
    """Called by the Hospital Dashboard to accept/reject an SOS."""
    sos_request = db.exec(select(SOSRequest).where(SOSRequest.id == sos_id)).first()
    if not sos_request:
        raise HTTPException(status_code=404, detail="SOS request not found.")
    
    if sos_request.status not in ["PENDING", "ACCEPTED"]:
        raise HTTPException(status_code=400, detail=f"SOS request is currently in status '{sos_request.status}' and cannot be reassigned.")

    sos_request.status = payload.status
    sos_request.updated_at = datetime.utcnow()

    if payload.status == "ACCEPTED" and payload.doctor_id:
        doctor = db.exec(select(Doctor).where(Doctor.id == payload.doctor_id)).first()
        if doctor:
            sos_request.assigned_doctor_id = doctor.id
            sos_request.assigned_doctor_name = doctor.name
            doctor.status = "In Surgery"  # Update doctor status or custom status
            db.add(doctor)

    db.add(sos_request)
    db.commit()
    db.refresh(sos_request)
    return {"message": f"SOS request {payload.status}", "sos": sos_request}

@router.get("/status/{sos_id}")
def check_sos_status(sos_id: str, db: Session = Depends(get_session)):
    """Called by the Citizen Frontend to poll for hospital response."""
    sos_request = db.exec(select(SOSRequest).where(SOSRequest.id == sos_id)).first()
    if not sos_request:
        raise HTTPException(status_code=404, detail="SOS request not found.")
    
    return {
        "sos_id": sos_request.id,
        "status": sos_request.status,
        "assigned_doctor_name": sos_request.assigned_doctor_name
    }
