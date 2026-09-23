from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/appointments", tags=["appointments"])


def _appt_out(appt: models.Appointment) -> schemas.AppointmentOut:
    return schemas.AppointmentOut(
        id=appt.id,
        doctor_id=appt.doctor_id,
        doctor_name=appt.doctor.user.name,
        doctor_specialty=appt.doctor.specialty,
        patient_id=appt.patient_id,
        patient_name=appt.patient.name,
        start_time=appt.start_time,
        end_time=appt.end_time,
        status=appt.status,
        reason=appt.reason,
    )


@router.post("", response_model=schemas.AppointmentOut, status_code=201)
def book_appointment(
    payload: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role(models.UserRole.patient)),
):
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    doctor = db.query(models.Doctor).filter(models.Doctor.id == payload.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Conflict check: any existing booked appointment for this doctor that overlaps.
    conflict = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.doctor_id == payload.doctor_id,
            models.Appointment.status == models.AppointmentStatus.booked,
            models.Appointment.start_time < payload.end_time,
            models.Appointment.end_time > payload.start_time,
        )
        .first()
    )
    if conflict:
        raise HTTPException(
            status_code=409,
            detail="That slot is no longer available. Please pick a different time.",
        )

    appt = models.Appointment(
        patient_id=current_user.id,
        doctor_id=payload.doctor_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        reason=payload.reason or "",
        status=models.AppointmentStatus.booked,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return _appt_out(appt)


@router.get("/me", response_model=List[schemas.AppointmentOut])
def my_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.Appointment).options(
        joinedload(models.Appointment.doctor).joinedload(models.Doctor.user),
        joinedload(models.Appointment.patient),
    )
    if current_user.role == models.UserRole.doctor:
        doctor = (
            db.query(models.Doctor).filter(models.Doctor.user_id == current_user.id).first()
        )
        if not doctor:
            return []
        appts = query.filter(models.Appointment.doctor_id == doctor.id).all()
    else:
        appts = query.filter(models.Appointment.patient_id == current_user.id).all()

    return [_appt_out(a) for a in appts]


@router.post("/{appointment_id}/cancel", response_model=schemas.AppointmentOut)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    appt = (
        db.query(models.Appointment)
        .options(
            joinedload(models.Appointment.doctor).joinedload(models.Doctor.user),
            joinedload(models.Appointment.patient),
        )
        .filter(models.Appointment.id == appointment_id)
        .first()
    )
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    is_owning_patient = appt.patient_id == current_user.id
    is_owning_doctor = (
        current_user.role == models.UserRole.doctor
        and appt.doctor.user_id == current_user.id
    )
    if not (is_owning_patient or is_owning_doctor):
        raise HTTPException(status_code=403, detail="Not your appointment to cancel")

    if appt.status != models.AppointmentStatus.booked:
        raise HTTPException(status_code=400, detail=f"Appointment is already {appt.status.value}")

    appt.status = models.AppointmentStatus.cancelled
    db.commit()
    db.refresh(appt)
    return _appt_out(appt)
