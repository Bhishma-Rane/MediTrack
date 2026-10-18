from datetime import time

import pytest
from fastapi.testclient import TestClient

from meditrack.db import Patient, Schedule
from meditrack.main import create_app


class FakeSmsSender:
    def __init__(self):
        self.calls = []

    async def send(self, *, to: str, body: str) -> str:
        self.calls.append((to, body))
        return "fake-message"


@pytest.fixture
def setup_app(tmp_path):
    sender = FakeSmsSender()
    app = create_app(f"sqlite:///{tmp_path / 'test.db'}", sender)
    # Seed through the app's dependency so the test uses the same database.
    from meditrack.db import make_session_factory
    db = make_session_factory(f"sqlite:///{tmp_path / 'test.db'}")()
    patient = Patient(name="Asha Rane", emergency_contact_phone="+15551234567", doctor_email="doctor@example.com")
    patient.schedules.append(Schedule(medication_name="Lisinopril", dosage="10 mg", target_time_utc=time(8, 0), grace_period_mins=15))
    db.add(patient)
    db.commit()
    db.close()
    return app, sender


def test_health_and_telemetry_are_persisted(setup_app):
    app, sender = setup_app
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        response = client.post("/api/v1/telemetry", json={
            "device_id": "ESP32_MED_01", "event": "DOSE_TAKEN",
            "timestamp": "2026-10-18T08:05:00+00:00", "patient_id": 1,
            "schedule_id": 1, "latency_seconds": 300, "event_id": "evt-1",
        })
        assert response.status_code == 200
        assert response.json()["status"] == "TAKEN"
        duplicate = client.post("/api/v1/telemetry", json={
            "device_id": "ESP32_MED_01", "event": "DOSE_TAKEN",
            "timestamp": "2026-10-18T08:05:00+00:00", "patient_id": 1,
            "schedule_id": 1, "event_id": "evt-1",
        })
        assert duplicate.json()["duplicate"] is True
        assert sender.calls == []


def test_missed_after_grace_period_sends_one_alert(setup_app):
    app, sender = setup_app
    with TestClient(app) as client:
        payload = {
            "device_id": "ESP32_MED_01", "event": "DOSE_MISSED",
            "timestamp": "2026-10-18T08:16:00+00:00", "patient_id": 1,
            "schedule_id": 1, "event_id": "evt-missed",
        }
        response = client.post("/api/v1/telemetry", json=payload)
        assert response.json()["status"] == "MISSED"
        assert response.json()["alerted"] is True
        assert len(sender.calls) == 1
        assert "Asha Rane" in sender.calls[0][1]


def test_naive_timestamp_is_rejected(setup_app):
    app, _ = setup_app
    with TestClient(app) as client:
        response = client.post("/api/v1/telemetry", json={
            "device_id": "ESP32_MED_01", "event": "DOSE_TAKEN",
            "timestamp": "2026-10-18T08:05:00", "patient_id": 1, "schedule_id": 1,
        })
        assert response.status_code == 422


def test_websocket_receives_live_update(setup_app):
    app, _ = setup_app
    with TestClient(app) as client:
        with client.websocket_connect("/ws/live-stream") as websocket:
            response = client.post("/api/v1/telemetry", json={
                "device_id": "ESP32_MED_01", "event": "DOSE_SNOOZED",
                "timestamp": "2026-10-18T07:55:00+00:00", "patient_id": 1,
                "schedule_id": 1, "event_id": "evt-snoozed",
            })
            assert response.status_code == 200
            update = websocket.receive_json()
            assert update["type"] == "dose.updated"
            assert update["status"] == "SNOOZED"
