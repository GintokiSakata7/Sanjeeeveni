from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
import uuid

from database import get_session
from app.models.hospital_models import Doctor, Driver, Ambulance
from app.schemas.hms_schemas import (
    DoctorCreatePayload, DoctorUpdatePayload, DoctorResponse,
    DriverCreatePayload, DriverUpdatePayload, DriverResponse,
    AmbulanceCreatePayload, AmbulanceUpdatePayload, AmbulanceResponse,
    HMSOverviewStats
)
from app.auth.security import get_password_hash

router = APIRouter(prefix="/hms", tags=["Hospital Management System (HMS)"])

# ==========================================
# 📊 TELEMETRY OVERVIEW STATS
# ==========================================
@router.get("/overview-stats/{hospital_id}", response_model=HMSOverviewStats)
def get_hms_overview_stats(hospital_id: str, db: Session = Depends(get_session)):
    doctors = db.exec(select(Doctor).where(Doctor.hospital_id == hospital_id)).all()
    drivers = db.exec(select(Driver).where(Driver.hospital_id == hospital_id)).all()
    ambulances = db.exec(select(Ambulance).where(Ambulance.hospital_id == hospital_id)).all()

    return HMSOverviewStats(
        total_doctors=len(doctors),
        available_doctors=len([d for d in doctors if d.status == "Available"]),
        in_surgery_doctors=len([d for d in doctors if d.status == "In Surgery"]),
        on_leave_doctors=len([d for d in doctors if d.status == "On Leave"]),
        total_drivers=len(drivers),
        available_drivers=len([d for d in drivers if d.status == "Available"]),
        total_ambulances=len(ambulances),
        available_ambulances=len([a for a in ambulances if a.status == "Available"]),
        dispatched_ambulances=len([a for a in ambulances if a.status == "Dispatched"])
    )


# ==========================================
# 👨‍⚕️ DOCTORS CRUD
# ==========================================
@router.get("/doctors/{hospital_id}", response_model=List[DoctorResponse])
def list_doctors(hospital_id: str, db: Session = Depends(get_session)):
    return db.exec(select(Doctor).where(Doctor.hospital_id == hospital_id).order_by(Doctor.created_at.desc())).all()

@router.post("/doctors", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(payload: DoctorCreatePayload, db: Session = Depends(get_session)):
    # Check for duplicate email within same hospital
    existing = db.exec(
        select(Doctor).where(Doctor.hospital_id == payload.hospital_id, Doctor.email == payload.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A doctor with email '{payload.email}' is already registered at this hospital."
        )

    doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
    pwd_hash = get_password_hash(payload.password)

    doctor = Doctor(
        id=doc_id,
        hospital_id=payload.hospital_id,
        name=payload.name,
        specialization=payload.specialization,
        contact_number=payload.contact_number,
        email=payload.email,
        password_hash=pwd_hash,
        status=payload.status,
        shift_timing=payload.shift_timing or "Morning Shift (08:00 AM - 04:00 PM)"
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.put("/doctors/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: str, payload: DoctorUpdatePayload, db: Session = Depends(get_session)):
    doctor = db.exec(select(Doctor).where(Doctor.id == doctor_id)).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor record not found")

    if payload.name is not None: doctor.name = payload.name
    if payload.specialization is not None: doctor.specialization = payload.specialization
    if payload.contact_number is not None: doctor.contact_number = payload.contact_number
    if payload.email is not None: doctor.email = payload.email
    if payload.status is not None: doctor.status = payload.status
    if payload.shift_timing is not None: doctor.shift_timing = payload.shift_timing

    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

@router.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: str, db: Session = Depends(get_session)):
    doctor = db.exec(select(Doctor).where(Doctor.id == doctor_id)).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor record not found")

    # Nullify any SOS request references to avoid FK constraint violation
    try:
        from app.models.hospital_models import SOSRequest
        sos_refs = db.exec(
            select(SOSRequest).where(SOSRequest.assigned_doctor_id == doctor_id)
        ).all()
        for sos in sos_refs:
            sos.assigned_doctor_id = None
            db.add(sos)
    except Exception:
        pass  # Table may not exist yet

    db.delete(doctor)
    db.commit()
    return {"success": True, "message": f"Doctor {doctor.name} deleted successfully"}


# ==========================================
# 🚘 DRIVERS CRUD
# ==========================================
@router.get("/drivers/{hospital_id}", response_model=List[DriverResponse])
def list_drivers(hospital_id: str, db: Session = Depends(get_session)):
    return db.exec(select(Driver).where(Driver.hospital_id == hospital_id).order_by(Driver.created_at.desc())).all()

@router.post("/drivers", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreatePayload, db: Session = Depends(get_session)):
    # Check for duplicate license number within same hospital
    existing = db.exec(
        select(Driver).where(Driver.hospital_id == payload.hospital_id, Driver.license_number == payload.license_number)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A driver with license number '{payload.license_number}' is already registered at this hospital."
        )

    driver_id = f"DRV-{uuid.uuid4().hex[:8].upper()}"
    pwd_hash = get_password_hash(payload.password)

    driver = Driver(
        id=driver_id,
        hospital_id=payload.hospital_id,
        name=payload.name,
        contact_number=payload.contact_number,
        license_number=payload.license_number,
        email=payload.email,
        password_hash=pwd_hash,
        status=payload.status,
        shift_timing=payload.shift_timing or "Morning Shift (08:00 AM - 04:00 PM)"
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver

@router.put("/drivers/{driver_id}", response_model=DriverResponse)
def update_driver(driver_id: str, payload: DriverUpdatePayload, db: Session = Depends(get_session)):
    driver = db.exec(select(Driver).where(Driver.id == driver_id)).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver record not found")

    if payload.name is not None: driver.name = payload.name
    if payload.contact_number is not None: driver.contact_number = payload.contact_number
    if payload.license_number is not None: driver.license_number = payload.license_number
    if payload.email is not None: driver.email = payload.email
    if payload.status is not None: driver.status = payload.status
    if payload.shift_timing is not None: driver.shift_timing = payload.shift_timing

    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.delete("/drivers/{driver_id}")
def delete_driver(driver_id: str, db: Session = Depends(get_session)):
    driver = db.exec(select(Driver).where(Driver.id == driver_id)).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver record not found")
    db.delete(driver)
    db.commit()
    return {"success": True, "message": f"Driver {driver.name} deleted successfully"}


# ==========================================
# 🚑 AMBULANCES CRUD
# ==========================================
@router.get("/ambulances/{hospital_id}", response_model=List[AmbulanceResponse])
def list_ambulances(hospital_id: str, db: Session = Depends(get_session)):
    return db.exec(select(Ambulance).where(Ambulance.hospital_id == hospital_id).order_by(Ambulance.created_at.desc())).all()

@router.post("/ambulances", response_model=AmbulanceResponse, status_code=status.HTTP_201_CREATED)
def create_ambulance(payload: AmbulanceCreatePayload, db: Session = Depends(get_session)):
    amb_id = f"AMB-{uuid.uuid4().hex[:8].upper()}"

    ambulance = Ambulance(
        id=amb_id,
        hospital_id=payload.hospital_id,
        vehicle_registration=payload.vehicle_registration,
        vehicle_type=payload.vehicle_type,
        assigned_driver_id=payload.assigned_driver_id,
        assigned_driver_name=payload.assigned_driver_name,
        status=payload.status
    )
    db.add(ambulance)
    db.commit()
    db.refresh(ambulance)
    return ambulance

@router.put("/ambulances/{ambulance_id}", response_model=AmbulanceResponse)
def update_ambulance(ambulance_id: str, payload: AmbulanceUpdatePayload, db: Session = Depends(get_session)):
    ambulance = db.exec(select(Ambulance).where(Ambulance.id == ambulance_id)).first()
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance record not found")

    if payload.vehicle_registration is not None: ambulance.vehicle_registration = payload.vehicle_registration
    if payload.vehicle_type is not None: ambulance.vehicle_type = payload.vehicle_type
    if payload.assigned_driver_id is not None: ambulance.assigned_driver_id = payload.assigned_driver_id
    if payload.assigned_driver_name is not None: ambulance.assigned_driver_name = payload.assigned_driver_name
    if payload.status is not None: ambulance.status = payload.status

    db.add(ambulance)
    db.commit()
    db.refresh(ambulance)
    return ambulance

@router.delete("/ambulances/{ambulance_id}")
def delete_ambulance(ambulance_id: str, db: Session = Depends(get_session)):
    ambulance = db.exec(select(Ambulance).where(Ambulance.id == ambulance_id)).first()
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance record not found")
    db.delete(ambulance)
    db.commit()
    return {"success": True, "message": f"Ambulance {ambulance.vehicle_registration} deleted successfully"}
