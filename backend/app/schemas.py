from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field

from app.models import UserRole, AppointmentStatus


# ---------- Auth / Users ----------

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: UserRole = UserRole.patient
    # required + used only when role == doctor
    specialty: Optional[str] = None
    bio: Optional[str] = ""
    years_experience: Optional[int] = 0


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True


# ---------- Doctors ----------

class DoctorOut(BaseModel):
    id: int
    specialty: str
    bio: str
    years_experience: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class SlotOut(BaseModel):
    start_time: datetime
    end_time: datetime


# ---------- Appointments ----------

class AppointmentCreate(BaseModel):
    doctor_id: int
    start_time: datetime
    end_time: datetime
    reason: Optional[str] = ""


class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    doctor_name: str
    doctor_specialty: str
    patient_id: int
    patient_name: str
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    reason: str

    class Config:
        from_attributes = True


# ---------- Symptom Advisor (Phase 2) ----------

class SymptomLookupResponse(BaseModel):
    matched_symptom: Optional[str]
    specialty: Optional[str]
    doctors: List[DoctorOut]
    message: str


class AgeGroupTipsOut(BaseModel):
    age_group: str
    label: str
    diet_dos: str
    diet_donts: str
    general_tips: str


class DiseaseTipsOut(BaseModel):
    name: str
    diet_dos: str
    diet_donts: str
    general_tips: str
    age_specific: List[AgeGroupTipsOut] = []
