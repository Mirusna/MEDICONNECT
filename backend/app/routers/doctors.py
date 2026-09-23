from datetime import datetime, timedelta, date as date_cls, time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/doctors", tags=["doctors"])

# Working hours used to generate candidate slots. Simple + fixed for Phase 1.
WORK_START = time(9, 0)
WORK_END = time(17, 0)
SLOT_MINUTES = 30


def _doctor_out(doctor: models.Doctor) -> schemas.DoctorOut:
    return schemas.DoctorOut(
        id=doctor.id,
        specialty=doctor.specialty,
        bio=doctor.bio,
        years_experience=doctor.years_experience,
        name=doctor.user.name,
        email=doctor.user.email,
    )


@router.get("", response_model=List[schemas.DoctorOut])
def list_doctors(
    specialty: Optional[str] = Query(None, description="Filter by specialty, case-insensitive substring match"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Doctor).options(joinedload(models.Doctor.user))
    if specialty:
        query = query.filter(models.Doctor.specialty.ilike(f"%{specialty}%"))
    doctors = query.all()
    return [_doctor_out(d) for d in doctors]


@router.get("/{doctor_id}", response_model=schemas.DoctorOut)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = (
        db.query(models.Doctor)
        .options(joinedload(models.Doctor.user))
        .filter(models.Doctor.id == doctor_id)
        .first()
    )
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return _doctor_out(doctor)


@router.get("/{doctor_id}/slots", response_model=List[schemas.SlotOut])
def get_available_slots(
    doctor_id: int,
    for_date: date_cls = Query(..., description="Date to check, format YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """
    Generates 30-minute candidate slots between working hours for the given
    date, then filters out any that overlap an existing 'booked' appointment.
    """
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    day_start = datetime.combine(for_date, WORK_START)
    day_end = datetime.combine(for_date, WORK_END)

    booked = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.doctor_id == doctor_id,
            models.Appointment.status == models.AppointmentStatus.booked,
            models.Appointment.start_time < day_end,
            models.Appointment.end_time > day_start,
        )
        .all()
    )

    free_slots = []
    cursor = day_start
    delta = timedelta(minutes=SLOT_MINUTES)
    now = datetime.utcnow()

    while cursor + delta <= day_end:
        slot_start, slot_end = cursor, cursor + delta
        if slot_start > now:  # don't offer slots in the past
            overlaps = any(
                a.start_time < slot_end and a.end_time > slot_start for a in booked
            )
            if not overlaps:
                free_slots.append(schemas.SlotOut(start_time=slot_start, end_time=slot_end))
        cursor += delta

    return free_slots
