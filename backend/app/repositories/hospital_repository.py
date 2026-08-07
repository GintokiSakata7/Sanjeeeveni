import uuid
from datetime import datetime
from typing import Optional, List
from supabase import Client

from app.schemas.hospital_schemas import HospitalRegistrationCreate
from app.auth.security import get_password_hash

class HospitalRepository:
    def __init__(self, session: Client):
        self.session = session
    
    def get_by_id(self, hospital_id: str) -> Optional[dict]:
        res = self.session.table("hospitals").select("*").eq("id", hospital_id).execute()
        return res.data[0] if res.data else None

    def get_by_registration_number(self, reg_num: str) -> Optional[dict]:
        res = self.session.table("hospitals").select("*").eq("registration_number", reg_num).execute()
        return res.data[0] if res.data else None

    def get_administrator_by_email(self, email: str) -> Optional[dict]:
        res = self.session.table("hospital_administrators").select("*").eq("email", email).execute()
        return res.data[0] if res.data else None

    def create_hospital_full(self, payload: HospitalRegistrationCreate) -> dict:
        hospital_id = f"HOSP-{datetime.utcnow().strftime('%Y+m%d')}-{str(uuid.uuid4())[:6].upper()}"

        # 1. Main Hospital record
        hospital_data = {
            "id": hospital_id,
            "name": payload.basic_info.hospital_name,
            "hospital_type": payload.basic_info.hospital_type,
            "category": payload.basic_info.category,
            "registration_number": payload.basic_info.registration_number,
            "license_number": payload.basic_info.license_number,
            "has_nabh_accreditation": payload.basic_info.has_nabh_accreditation,
            "nabh_number": payload.basic_info.nabh_number,
            "gst_number": payload.basic_info.gst_number,
            "status": "PENDING_VERIFICATION",
            "latitude": payload.address.latitude,
            "longitude": payload.address.longitude,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.session.table("hospitals").insert(hospital_data).execute()

        # 2. Address record
        address_data = {
            "id": f"ADDR-{uuid.uuid4()}",
            "hospital_id": hospital_id,
            "country": payload.address.country,
            "state": payload.basic_info.hospital_name,
            "district": payload.address.district,
            "city": payload.address.city,
            "area": payload.address.area,
            "pincode": payload.address.pincode,
            "complete_address": payload.address.complete_address,
            "latitude": payload.address.latitude,
            "longitude": payload.address.longitude
        }
        self.session.table("hospital_addresses").insert(address_data).execute()

        # 3. Administrator record
        hashed_password = get_password_hash(payload.administrator.password)
        admin_data = {
            "id": f"ADMIN-{uuid.uuid4()}",
            "hospital_id": hospital_id,
            "name": payload.administrator.name,
            "designation": payload.administrator.designation,
            "email": payload.administrator.email.lower().strip(),
            "mobile": payload.administrator.mobile,
            "password_hash": hashed_password,
            "is_active": True
        }
        self.session.table("hospital_administrators").insert(admin_data).execute()

        # 4. Details / Capacity
        details_data = {
            "id": f"DET-{uuid.uuid4()}",
            "hospital_id": hospital_id,
            "total_beds": payload.capacity.total_beds,
            "icu_beds": payload.capacity.icu_beds,
            "has_emergency_dept": payload.capacity.has_emergency_dept,
            "has_trauma_center": payload.capacity.has_trauma_center,
            "has_blood_bank": payload.capacity.has_blood_bank,
            "ambulance_count": payload.capacity.ambulance_count,
            "departments": payload.capacity.departments,
            "specializations": payload.capacity.specializations
        }
        self.session.table("hospital_details").insert(details_data).execute()

        # 5. Verification Documents
        docs_data = {
            "id": f"DOC-{uuid.uuid4()}",
            "hospital_id": hospital_id,
            "registration_cert_url": payload.documents.registration_cert_url or "",
            "govt_license_url": payload.documents.govt_license_url or "",
            "nabh_cert_url": payload.documents.nabh_cert_url,
            "pan_url": payload.documents.pan_url or "",
            "gst_url": payload.documents.gst_url,
            "exterior_image_url": payload.documents.exterior_image_url or "",
            "logo_url": payload.documents.logo_url or ""
        }
        self.session.table("hospital_documents").insert(docs_data).execute()

        # 6. Integration Config
        integration_data = {
            "id": f"INT-{uuid.uuid4()}",
            "hospital_id": hospital_id,
            "integration_mode": payload.integration.integration_mode,
            "base_url": payload.integration.base_url,
            "callback_url": payload.integration.callback_url,
            "api_doc_url": payload.integration.api_doc_url,
            "tech_contact_name": payload.integration.tech_contact_name,
            "tech_contact_email": str(payload.integration.tech_contact_email) if payload.integration.tech_contact_email else None
        }
        self.session.table("hospital_integrations").insert(integration_data).execute()

        # 7. Verification Audit Record
        verif_data = {
            "id": f"VERIF-{uuid.uuid4()}",
            "hospital_id": hospital_id,
            "verification_status": "PENDING_VERIFICATION",
            "review_notes": "Registration submitted. Awaiting administrative verification.",
            "verified_at": datetime.utcnow().isoformat()
        }
        self.session.table("hospital_verifications").insert(verif_data).execute()

        return hospital_data

    def get_full_profile(self, hospital_id: str) -> Optional[dict]:
        hospital = self.get_by_id(hospital_id)
        if not hospital:
            return None

        addr_res = self.session.table("hospital_addresses").select("*").eq("hospital_id", hospital_id).execute()
        addr = addr_res.data[0] if addr_res.data else None

        admin_res = self.session.table("hospital_administrators").select("*").eq("hospital_id", hospital_id).execute()
        admin = admin_res.data[0] if admin_res.data else None

        cap_res = self.session.table("hospital_details").select("*").eq("hospital_id", hospital_id).execute()
        cap = cap_res.data[0] if cap_res.data else None

        docs_res = self.session.table("hospital_documents").select("*").eq("hospital_id", hospital_id).execute()
        docs = docs_res.data[0] if docs_res.data else None

        integ_res = self.session.table("hospital_integrations").select("*").eq("hospital_id", hospital_id).execute()
        integ = integ_res.data[0] if integ_res.data else None

        return {
            "id": hospital.get("id"),
            "name": hospital.get("name"),
            "hospital_type": hospital.get("hospital_type"),
            "category": hospital.get("category"),
            "registration_number": hospital.get("registration_number"),
            "license_number": hospital.get("license_number"),
            "status": hospital.get("status"),
            "latitude": hospital.get("latitude") or (addr.get("latitude") if addr else 17.4126),
            "longitude": hospital.get("longitude") or (addr.get("longitude") if addr else 78.4482),
            "created_at": hospital.get("created_at"),
            "address": addr or {},
            "administrator": {
                "name": admin.get("name") if admin else "",
                "designation": admin.get("designation") if admin else "",
              "email": admin.get("email") if admin else "",
              "mobile": admin.get("mobile") if admin else ""
            },
            "capacity": cap or {},
            "documents": docs or {},
            "integration": integ or {}
        }
