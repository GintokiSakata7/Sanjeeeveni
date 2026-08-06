import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select
from app.models.hospital_models import (
    Hospital, HospitalAddress, HospitalAdministrator, HospitalDetails,
    HospitalDocuments, HospitalIntegration, HospitalVerification,
    VerificationStatusEnum
)
from app.schemas.hospital_schemas import HospitalRegistrationCreate
from app.auth.security import get_password_hash

class HospitalRepository:
    def __init__(self, session: Session):
        if isinstance(session, HospitalRepository):
            self.session = session.session
        else:
            self.session = session

    def get_by_id(self, hospital_id: str) -> Optional[Hospital]:
        return self.session.get(Hospital, hospital_id)

    def get_by_registration_number(self, reg_num: str) -> Optional[Hospital]:
        statement = select(Hospital).where(Hospital.registration_number == reg_num)
        return self.session.exec(statement).first()

    def get_administrator_by_email(self, email: str) -> Optional[HospitalAdministrator]:
        statement = select(HospitalAdministrator).where(HospitalAdministrator.email == email)
        return self.session.exec(statement).first()

    def create_hospital_full(self, payload: HospitalRegistrationCreate) -> Hospital:
        hospital_id = f"HOSP-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

        # 1. Main Hospital record
        db_hospital = Hospital(
            id=hospital_id,
            name=payload.basic_info.hospital_name,
            hospital_type=payload.basic_info.hospital_type,
            category=payload.basic_info.category,
            registration_number=payload.basic_info.registration_number,
            license_number=payload.basic_info.license_number,
            has_nabh_accreditation=payload.basic_info.has_nabh_accreditation,
            nabh_number=payload.basic_info.nabh_number,
            gst_number=payload.basic_info.gst_number,
            status=VerificationStatusEnum.PENDING_VERIFICATION
        )
        self.session.add(db_hospital)

        # 2. Address record
        db_address = HospitalAddress(
            id=f"ADDR-{uuid.uuid4()}",
            hospital_id=hospital_id,
            country=payload.address.country,
            state=payload.address.state,
            district=payload.address.district,
            city=payload.address.city,
            area=payload.address.area,
            pincode=payload.address.pincode,
            complete_address=payload.address.complete_address,
            latitude=payload.address.latitude,
            longitude=payload.address.longitude
        )
        self.session.add(db_address)

        # 3. Administrator record
        hashed_password = get_password_hash(payload.administrator.password)
        db_admin = HospitalAdministrator(
            id=f"ADMIN-{uuid.uuid4()}",
            hospital_id=hospital_id,
            name=payload.administrator.name,
            designation=payload.administrator.designation,
            email=payload.administrator.email.lower().strip(),
            mobile=payload.administrator.mobile,
            password_hash=hashed_password,
            is_active=True
        )
        self.session.add(db_admin)

        # 4. Details / Capacity
        db_details = HospitalDetails(
            id=f"DET-{uuid.uuid4()}",
            hospital_id=hospital_id,
            total_beds=payload.capacity.total_beds,
            icu_beds=payload.capacity.icu_beds,
            has_emergency_dept=payload.capacity.has_emergency_dept,
            has_trauma_center=payload.capacity.has_trauma_center,
            has_blood_bank=payload.capacity.has_blood_bank,
            ambulance_count=payload.capacity.ambulance_count,
            departments=payload.capacity.departments,
            specializations=payload.capacity.specializations
        )
        self.session.add(db_details)

        # 5. Verification Documents
        db_docs = HospitalDocuments(
            id=f"DOC-{uuid.uuid4()}",
            hospital_id=hospital_id,
            registration_cert_url=payload.documents.registration_cert_url or "",
            govt_license_url=payload.documents.govt_license_url or "",
            nabh_cert_url=payload.documents.nabh_cert_url,
            pan_url=payload.documents.pan_url or "",
            gst_url=payload.documents.gst_url,
            exterior_image_url=payload.documents.exterior_image_url or "",
            logo_url=payload.documents.logo_url or ""
        )

        self.session.add(db_docs)

        # 6. Integration Config
        db_integration = HospitalIntegration(
            id=f"INT-{uuid.uuid4()}",
            hospital_id=hospital_id,
            integration_mode=payload.integration.integration_mode,
            base_url=payload.integration.base_url,
            callback_url=payload.integration.callback_url,
            api_doc_url=payload.integration.api_doc_url,
            tech_contact_name=payload.integration.tech_contact_name,
            tech_contact_email=str(payload.integration.tech_contact_email) if payload.integration.tech_contact_email else None
        )
        self.session.add(db_integration)

        # 7. Verification Audit Record
        db_verification = HospitalVerification(
            id=f"VERIF-{uuid.uuid4()}",
            hospital_id=hospital_id,
            verification_status=VerificationStatusEnum.PENDING_VERIFICATION,
            review_notes="Registration submitted. Awaiting administrative verification."
        )
        self.session.add(db_verification)

        self.session.commit()
        self.session.refresh(db_hospital)

        return db_hospital

    def get_full_profile(self, hospital_id: str) -> Optional[dict]:
        hospital = self.get_by_id(hospital_id)
        if not hospital:
            return None

        addr = self.session.exec(select(HospitalAddress).where(HospitalAddress.hospital_id == hospital_id)).first()
        admin = self.session.exec(select(HospitalAdministrator).where(HospitalAdministrator.hospital_id == hospital_id)).first()
        cap = self.session.exec(select(HospitalDetails).where(HospitalDetails.hospital_id == hospital_id)).first()
        docs = self.session.exec(select(HospitalDocuments).where(HospitalDocuments.hospital_id == hospital_id)).first()
        integ = self.session.exec(select(HospitalIntegration).where(HospitalIntegration.hospital_id == hospital_id)).first()

        return {
            "id": hospital.id,
            "name": hospital.name,
            "hospital_type": hospital.hospital_type,
            "category": hospital.category,
            "registration_number": hospital.registration_number,
            "license_number": hospital.license_number,
            "status": hospital.status,
            "created_at": hospital.created_at,
            "address": {
                "country": addr.country if addr else "",
                "state": addr.state if addr else "",
                "district": addr.district if addr else "",
                "city": addr.city if addr else "",
                "area": addr.area if addr else "",
                "pincode": addr.pincode if addr else "",
                "complete_address": addr.complete_address if addr else "",
                "latitude": addr.latitude if addr else 0.0,
                "longitude": addr.longitude if addr else 0.0,
            } if addr else {},
            "administrator": {
                "name": admin.name if admin else "",
                "designation": admin.designation if admin else "",
                "email": admin.email if admin else "",
                "mobile": admin.mobile if admin else ""
            } if admin else {},
            "capacity": {
                "total_beds": cap.total_beds if cap else 0,
                "icu_beds": cap.icu_beds if cap else 0,
                "has_emergency_dept": cap.has_emergency_dept if cap else True,
                "has_trauma_center": cap.has_trauma_center if cap else False,
                "has_blood_bank": cap.has_blood_bank if cap else False,
                "ambulance_count": cap.ambulance_count if cap else 0,
                "departments": cap.departments if cap else [],
                "specializations": cap.specializations if cap else []
            } if cap else {},
            "documents": {
                "registration_cert_url": docs.registration_cert_url if docs else "",
                "govt_license_url": docs.govt_license_url if docs else "",
                "nabh_cert_url": docs.nabh_cert_url if docs else None,
                "pan_url": docs.pan_url if docs else "",
                "gst_url": docs.gst_url if docs else None,
                "exterior_image_url": docs.exterior_image_url if docs else "",
                "logo_url": docs.logo_url if docs else ""
            } if docs else {},
            "integration": {
                "integration_mode": integ.integration_mode if integ else "DASHBOARD",
                "base_url": integ.base_url if integ else None,
                "callback_url": integ.callback_url if integ else None,
                "api_doc_url": integ.api_doc_url if integ else None,
                "tech_contact_name": integ.tech_contact_name if integ else None,
                "tech_contact_email": integ.tech_contact_email if integ else None
            } if integ else {}
        }
