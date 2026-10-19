"""Dashboard read model built from Part 3's daily schedules and dose logs."""

from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select

from .db import DoseLog, Patient, Schedule


def load_dashboard_snapshot(db, *, start: date, end: date, now: datetime | None = None) -> dict:
    """Return detached, serializable dashboard data for the inclusive date range.

    Part 3 stores a daily UTC target time but does not yet store recurrence rules or
    effective dates. This read model therefore treats every active schedule as daily
    and excludes future occurrences; the limitation is explicit for later migration.
    """
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    patients = db.scalars(select(Patient).order_by(Patient.name)).all()
    schedules = db.scalars(select(Schedule)).all()
    logs = db.scalars(select(DoseLog).where(DoseLog.timestamp >= datetime.combine(start, time.min, tzinfo=timezone.utc),
                                            DoseLog.timestamp < datetime.combine(end + timedelta(days=1), time.min, tzinfo=timezone.utc))).all()
    schedule_by_id = {item.schedule_id: item for item in schedules}
    rows = []
    for log in logs:
        schedule = schedule_by_id.get(log.schedule_id)
        rows.append({"log_id": log.log_id, "patient_id": log.patient_id, "schedule_id": log.schedule_id,
                     "timestamp": log.timestamp, "status": log.status, "device_id": log.device_id,
                     "response_time_sec": log.response_time_sec,
                     "medication_name": schedule.medication_name if schedule else "—",
                     "dosage": schedule.dosage if schedule else "—",
                     "target_time": schedule.target_time_utc if schedule else None,
                     "grace_period_mins": schedule.grace_period_mins if schedule else 0})
    return {"patients": [{"patient_id": p.patient_id, "name": p.name,
                           "emergency_contact_phone": p.emergency_contact_phone,
                           "doctor_email": p.doctor_email} for p in patients],
            "schedules": [{"schedule_id": s.schedule_id, "patient_id": s.patient_id,
                           "medication_name": s.medication_name, "dosage": s.dosage,
                           "target_time_utc": s.target_time_utc, "grace_period_mins": s.grace_period_mins} for s in schedules],
            "logs": rows, "range": {"start": start, "end": end, "generated_at": now}}


def scheduled_occurrences(snapshot: dict, *, patient_id: int, start: date, end: date, now: datetime) -> list[dict]:
    """Expand daily schedules into expected occurrences through ``now``."""
    schedules = [s for s in snapshot["schedules"] if s["patient_id"] == patient_id]
    occurrences = []
    day = start
    while day <= end:
        for schedule in schedules:
            target = datetime.combine(day, schedule["target_time_utc"], tzinfo=timezone.utc)
            if target > now.astimezone(timezone.utc):
                continue
            matching = [log for log in snapshot["logs"] if log["patient_id"] == patient_id and log["schedule_id"] == schedule["schedule_id"] and log["timestamp"].date() == day]
            taken = next((log for log in matching if log["status"] == "TAKEN"), None)
            latest = max(matching, key=lambda log: log["timestamp"], default=None)
            late = bool(taken and taken["timestamp"] > target + timedelta(minutes=schedule["grace_period_mins"]))
            occurrences.append({"date": day, "schedule_id": schedule["schedule_id"], "medication_name": schedule["medication_name"],
                                "target_timestamp": target, "status": "TAKEN" if taken else ("MISSED" if latest and latest["status"] == "MISSED" or now >= target + timedelta(minutes=schedule["grace_period_mins"]) else "PENDING"),
                                "taken_timestamp": taken["timestamp"] if taken else None, "response_time_sec": taken["response_time_sec"] if taken else None,
                                "late": late})
        day += timedelta(days=1)
    return occurrences
