from fastapi import HTTPException, status
from supabase import Client
from app.repositories.hospital_repository import HospitalRepository
from app.schemas.hospital_schemas import (
    HospitalRegistrationCreate, HospitalLoginRequest, TokenResponse
)
from app.auth.security import verify_password, create_access_token

class HospitalService:
    def __init__(self, session: Client):
        self.repo = HospitalRepository(session)

    def register_hospital(self, payload: HospitalRegistrationCreate) -> dict:
        # Check duplicate registration number
        existing_reg = self.repo.get_by_registration_number(payload.basic_info.registration_number)
        if existing_reg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hospital with Registration Number '{payload.basic_info.registration_number}' is already registered."
            )

        # Check duplicate email
        existing_email = self.repo.get_administrator_by_email(payload.administrator.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Administrator email '{payload.administrator.email}' is already registered."
            )

        hospital = self.repo.create_hospital_full(payload)

        return {
            "success": True,
            "message": "Hospital registration submitted successfully! Your account is currently PENDING_VERIFICATION.",
            "hospital_id": hospital.get("id"),
            "status": hospital.get("status"),
            "hospital_name": hospital.get("name")
        }

    def authenticate_hospital(self, credentials: HospitalLoginRequest) -> TokenResponse:
        admin = self.repo.get_administrator_by_email(credentials.email)
        if not admin or not verify_password(credentials.password, admin.get("password_hash")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid administrator email or password."
            )

        hospital = self.repo.get_by_id(admin.get("hospital_id"))
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated hospital record not found."
            )

        token_data = {
            "sub": admin.get("id"),
            "hospital_id": hospital.get("id"),
            "email": admin.get("email"),
            "role": "ADMIN" # Fallback role
        }
        access_token = create_access_token(data=token_data)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            hospital_id=hospital.get("id"),
            hospital_name=hospital.get("name"),
            admin_name=admin.get("name"),
            status=hospital.get("status"),
            hospital_type=hospital.get("hospital_type")
        )

    def get_hospital_profile(self, hospital_id: str) -> dict:
        profile = self.repo.get_full_profile(hospital_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hospital with ID '{hospital_id}' not found."
            )
        return profile
