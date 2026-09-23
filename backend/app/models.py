import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum, Text, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    patient = "patient"
    doctor = "doctor"


class AppointmentStatus(str, enum.Enum):
    booked = "booked"
    cancelled = "cancelled"
    completed = "completed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.patient)
    created_at = Column(DateTime, default=datetime.utcnow)

    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    appointments = relationship(
        "Appointment", back_populates="patient", foreign_keys="Appointment.patient_id"
    )


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialty = Column(String(120), nullable=False, index=True)
    bio = Column(Text, default="")
    years_experience = Column(Integer, default=0)

    user = relationship("User", back_populates="doctor_profile")
    appointments = relationship("Appointment", back_populates="doctor")


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_doctor_time", "doctor_id", "start_time", "end_time"),
    )

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.booked)
    reason = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("User", back_populates="appointments", foreign_keys=[patient_id])
    doctor = relationship("Doctor", back_populates="appointments")


class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False, index=True)
    specialty = Column(String(120), nullable=False)


class Disease(Base):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False, index=True)
    diet_dos = Column(Text, default="")
    diet_donts = Column(Text, default="")
    general_tips = Column(Text, default="")

    age_tips = relationship(
        "DiseaseAgeTip", back_populates="disease", cascade="all, delete-orphan"
    )


class AgeGroup(str, enum.Enum):
    children = "children"      # ~2-12
    teen = "teen"               # ~13-19
    adult = "adult"              # ~20-59
    senior = "senior"            # 60+


class DiseaseAgeTip(Base):
    """Age-specific diet/care guidance for a Disease (Phase 2 extension)."""
    __tablename__ = "disease_age_tips"
    __table_args__ = (UniqueConstraint("disease_id", "age_group"),)

    id = Column(Integer, primary_key=True)
    disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=False)
    age_group = Column(Enum(AgeGroup), nullable=False)
    diet_dos = Column(Text, default="")
    diet_donts = Column(Text, default="")
    general_tips = Column(Text, default="")

    disease = relationship("Disease", back_populates="age_tips")
