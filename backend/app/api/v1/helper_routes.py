from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import Session, select
import hashlib

from database import get_session
from db_models import User, CommunityWorker, RoleEnum

router = APIRouter(prefix="/helpers", tags=["Community Helpers"])

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class HelperRegisterRequest(BaseModel):
    name: str
    phone: str
    password: str
    role_type: str
    location: str
    certificate_id: str
    skills: List[str]
    latitude: Optional[float] = 17.3850
    longitude: Optional[float] = 78.4867

class HelperLoginRequest(BaseModel):
    phone: str
    password: str

@router.post("/register")
def register_helper(payload: HelperRegisterRequest, db: Session = Depends(get_session)):
    # Check if user already exists
    existing_user = db.exec(select(User).where(User.phone == payload.phone)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this phone number already exists.")

    # Create User
    new_user = User(
        name=payload.name,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=RoleEnum.COMMUNITY_WORKER
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create CommunityWorker
    skills_str = ", ".join(payload.skills) if payload.skills else ""
    new_worker = CommunityWorker(
        user_id=new_user.id,
        role_type=payload.role_type,
        certificate_id=payload.certificate_id,
        skills=skills_str,
        current_lat=payload.latitude,
        current_lng=payload.longitude,
        is_available=True
    )
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)

    return {
        "message": "Helper registered successfully",
        "user_id": new_user.id,
        "worker_id": new_worker.id
    }

@router.post("/login")
def login_helper(payload: HelperLoginRequest, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.phone == payload.phone)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    if user.password_hash != hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    if user.role != RoleEnum.COMMUNITY_WORKER:
        raise HTTPException(status_code=403, detail="User is not registered as a Community Helper")

    worker = db.exec(select(CommunityWorker).where(CommunityWorker.user_id == user.id)).first()

    return {
        "message": "Login successful",
        "user_id": user.id,
        "name": user.name,
        "role_type": worker.role_type if worker else None,
        "location": "Banjara Hills Sector 4, Hyderabad" # Mock location for UI compatibility
    }
