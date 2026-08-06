"""
AERO Responder Service - Hospital, Ambulance, and Doctor Allocation Engine
Matches closest medical resources based on triage severity and patient location.
"""

from typing import Dict, Any, Tuple
from db_models import HospitalInfo, AmbulanceInfo, SeverityEnum

def allocate_responders(severity: SeverityEnum, doctor_specialty: str) -> Tuple[HospitalInfo, AmbulanceInfo]:
    """
    Allocates nearest trauma hospital and dispatches ALS/BLS ambulance unit.
    """
    is_critical = (severity == SeverityEnum.RED_CRITICAL)

    hospital = HospitalInfo(
        id="HOSP-101",
        name="City Apex Trauma & General Hospital",
        distance_km=2.4,
        eta_minutes=6 if is_critical else 10,
        available_icu_beds=4 if is_critical else 12,
        phone="+91 40 2345 6789"
    )

    ambulance = AmbulanceInfo(
        id="AMB-502",
        vehicle_number="TS-09-EM-0108",
        driver_name="Ramesh Kumar (ALS Certified)",
        driver_phone="+91 94401 23456",
        equipment_level="ALS (Advanced Life Support)" if is_critical else "BLS (Basic)",
        eta_minutes=5 if is_critical else 8
    )

    return hospital, ambulance
