from datetime import date, datetime, time, timezone

from meditrack.analytics import occurrence_adherence
from meditrack.dashboard_data import scheduled_occurrences


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
