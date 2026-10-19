from datetime import date, datetime, time, timezone

from meditrack.analytics import occurrence_adherence
from meditrack.admin import create_patient, create_schedule
from meditrack.dashboard_data import scheduled_occurrences
from meditrack.db import Base, make_engine, make_session_factory


def test_admin_services_create_patient_and_schedule(tmp_path):
    url = f"sqlite:///{tmp_path / 'admin.db'}"
    engine = make_engine(url)
    Base.metadata.create_all(engine)
    db = make_session_factory(url)()
    patient = create_patient(db, name="Asha Rane", emergency_contact_phone="+15551234567", doctor_email="doctor@example.com")
    schedule = create_schedule(db, patient_id=patient.patient_id, medication_name="Lisinopril", dosage="10 mg", target_time_utc=time(8), grace_period_mins=15)
    assert patient.patient_id > 0
    assert schedule.patient_id == patient.patient_id
    db.close()


def test_daily_occurrences_count_scheduled_doses_not_raw_events():
    snapshot = {"schedules": [{"schedule_id": 1, "patient_id": 7, "medication_name": "A", "target_time_utc": time(8), "grace_period_mins": 15}], "logs": [{
        "patient_id": 7, "schedule_id": 1, "timestamp": datetime(2026, 10, 18, 8, 5, tzinfo=timezone.utc), "status": "TAKEN", "response_time_sec": 300,
    }]}
    occurrences = scheduled_occurrences(snapshot, patient_id=7, start=date(2026, 10, 18), end=date(2026, 10, 19), now=datetime(2026, 10, 19, 12, tzinfo=timezone.utc))
    assert len(occurrences) == 2
    assert occurrence_adherence(occurrences) == 50.0


def test_late_taken_is_retained_as_taken_and_marked_late():
    snapshot = {"schedules": [{"schedule_id": 1, "patient_id": 7, "medication_name": "A", "target_time_utc": time(8), "grace_period_mins": 15}], "logs": [{
        "patient_id": 7, "schedule_id": 1, "timestamp": datetime(2026, 10, 18, 8, 20, tzinfo=timezone.utc), "status": "TAKEN", "response_time_sec": 1200,
    }]}
    occurrence = scheduled_occurrences(snapshot, patient_id=7, start=date(2026, 10, 18), end=date(2026, 10, 18), now=datetime(2026, 10, 18, 12, tzinfo=timezone.utc))[0]
    assert occurrence["status"] == "TAKEN"
    assert occurrence["late"] is True
