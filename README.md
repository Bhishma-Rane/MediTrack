# MediTrack — software and Part 1 hardware

FastAPI telemetry and real-time notification backend for the MediTrack ESP32 medication compliance system.

## What is included

- `POST /api/v1/telemetry` validates and persists ESP32 dose events in SQLite.
- `WS /ws/live-stream` broadcasts versioned dose updates to connected dashboards.
- SQLAlchemy models for `patients`, `schedules`, and `dose_logs`.
- Idempotency through `event_id` (or a deterministic device/timestamp/event key).
- Grace-period-aware missed-dose alerts. Twilio is used only when its three settings are present; otherwise the default is a safe local dry-run sender.

Part 4 adds a Streamlit caregiver dashboard and downloadable ReportLab PDF compliance reports.

Part 1 hardware is specified in [`hardware/README.md`](hardware/README.md).
It includes the ESP32 pinout, point-to-point harness tables, a renderable SVG
electrical diagram, bill of materials, power/fail-safe design, bring-up
checklist, and a parametric OpenSCAD enclosure. The hardware is a low-voltage
prototype access verifier; it is not a validated medical device and does not
prove medication ingestion.

## Part 2 and Part 3 integration

The uploadable ESP32 firmware is in
[`firmware/esp32_meditrack`](firmware/esp32_meditrack). It implements the
fail-closed dispensing state machine, NTP time, Wi-Fi reconnect, LittleFS
offline telemetry queue, and Preferences recovery. The backend accepts
`DISPENSE_ATTEMPTED`, `DISPENSE_CONFIRMED`, `DISPENSE_UNCONFIRMED`,
`DISPENSE_FAULT`, and `DEVICE_HEARTBEAT` without treating a dispense event as
proof that medication was swallowed.

See the [firmware upload guide](firmware/esp32_meditrack/README.md) and the
[ESP32 wiring quick reference](hardware/wiring/esp32_firmware_wiring.md).
Before uploading, edit the local `firmware/esp32_meditrack/include/config.h`
with Wi-Fi, backend URL, patient ID, and schedule ID values. Keep credentials
out of git. The API must be reachable from the ESP32; `localhost` on the ESP32
is the ESP32 itself, not the computer running FastAPI.

## Setup

Requires Python 3.11+ and a network connection for the first dependency install. The application itself and its tests run offline after installation.

```bash
python3.11 -m venv .venv
. .venv/bin/activate
make install
cp .env.example .env
```

## Run

```bash
make run
```

The API is available at `http://localhost:8000`; health check: `GET /health`.

Start the caregiver dashboard in a second terminal:

```bash
make dashboard
```

The dashboard is available at `http://localhost:8501`. It reads the configured SQLite database, shows node online/offline status based on the latest telemetry, computes adherence, filters TAKEN/MISSED/LATE logs, and generates a downloadable PDF report.

### Portal administration

Patient and medication setup no longer requires direct database access. Set `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env`, restart Streamlit, then open the **Admin portal** tab. The administrator can register patients and add daily UTC medication schedules with dosage and grace period. The caregiver tab is read-only for these records.

This is local/demo authentication for the portal. For deployment on a network, put Streamlit behind HTTPS and an identity-aware reverse proxy or replace this shared admin secret with organization authentication before handling real patient data.

Example telemetry request:

```bash
curl -X POST http://localhost:8000/api/v1/telemetry \
  -H 'content-type: application/json' \
  -d '{"device_id":"ESP32_MED_01","event":"DOSE_TAKEN","timestamp":"2026-10-18T08:05:00Z","patient_id":1,"schedule_id":1,"latency_seconds":300}'
```

Patients and schedules can be provisioned through the Admin portal. The API rejects telemetry events that cannot resolve both records.

## Test

```bash
make test

# Validate Part 1 hardware artifacts offline
make hardware-test
```

`make test` runs the backend tests and the host-side ESP32 firmware validator.
Tests use temporary SQLite databases and a fake SMS sender, so they make no
network calls and do not require Twilio credentials. The actual ESP32 compile
and upload are documented in the firmware README and require PlatformIO.

## Docker

```bash
docker build -t meditrack-backend .
docker run --rm -p 8000:8000 -v "$PWD/data:/app/data" --env-file .env meditrack-backend
```

## Deploy notes

For a demo, SQLite is suitable. For production, move `DATABASE_URL` to PostgreSQL, put the API behind TLS, authenticate device telemetry, and use a durable notification/outbox worker before sending clinical alerts. Never commit `.env` or credentials.
