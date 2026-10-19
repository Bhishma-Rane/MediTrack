"""Small transaction services used by the portal's admin area."""

from datetime import time

from sqlalchemy import select

from .db import Patient, Schedule


def create_patient(db, *, name: str, emergency_contact_phone: str, doctor_email: str | None = None) -> Patient:
    name = name.strip()
    phone = emergency_contact_phone.strip()
    if not name:
        raise ValueError("Patient name is required")
    if not phone:
        raise ValueError("Emergency contact phone is required")
    patient = Patient(name=name, emergency_contact_phone=phone, doctor_email=doctor_email.strip() or None if doctor_email else None)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def create_schedule(db, *, patient_id: int, medication_name: str, dosage: str, target_time_utc: time, grace_period_mins: int) -> Schedule:
    medication_name = medication_name.strip()
    dosage = dosage.strip()
    if not db.get(Patient, patient_id):
        raise ValueError("Patient does not exist")
    if not medication_name or not dosage:
        raise ValueError("Medication name and dosage are required")
    if grace_period_mins < 0 or grace_period_mins > 24 * 60:
        raise ValueError("Grace period must be between 0 and 1440 minutes")
    schedule = Schedule(patient_id=patient_id, medication_name=medication_name, dosage=dosage,
                        target_time_utc=target_time_utc, grace_period_mins=grace_period_mins)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def list_admin_records(db) -> list[dict]:
    patients = db.scalars(select(Patient).order_by(Patient.name)).all()
    return [{"patient_id": patient.patient_id, "name": patient.name,
             "emergency_contact_phone": patient.emergency_contact_phone,
             "doctor_email": patient.doctor_email,
             "schedules": [{"schedule_id": schedule.schedule_id, "medication_name": schedule.medication_name,
                            "dosage": schedule.dosage, "target_time_utc": schedule.target_time_utc,
                            "grace_period_mins": schedule.grace_period_mins} for schedule in patient.schedules]}
            for patient in patients]
