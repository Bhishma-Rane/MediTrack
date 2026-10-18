# MediTrack — Parts 3 and 4

FastAPI telemetry and real-time notification backend for the MediTrack ESP32 medication compliance system.

## What is included

- `POST /api/v1/telemetry` validates and persists ESP32 dose events in SQLite.
- `WS /ws/live-stream` broadcasts versioned dose updates to connected dashboards.
- SQLAlchemy models for `patients`, `schedules`, and `dose_logs`.
- Idempotency through `event_id` (or a deterministic device/timestamp/event key).
- Grace-period-aware missed-dose alerts. Twilio is used only when its three settings are present; otherwise the default is a safe local dry-run sender.

Part 4 adds a Streamlit caregiver dashboard and downloadable ReportLab PDF compliance reports.

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

Example telemetry request:

```bash
curl -X POST http://localhost:8000/api/v1/telemetry \
  -H 'content-type: application/json' \
  -d '{"device_id":"ESP32_MED_01","event":"DOSE_TAKEN","timestamp":"2026-10-18T08:05:00Z","patient_id":1,"schedule_id":1,"latency_seconds":300}'
```

Patients and schedules should be provisioned in the database before telemetry ingestion. The API rejects events that cannot resolve both records.

## Test

```bash
make test
```

Tests use temporary SQLite databases and a fake SMS sender, so they make no network calls and do not require Twilio credentials.

## Docker

```bash
docker build -t meditrack-backend .
docker run --rm -p 8000:8000 -v "$PWD/data:/app/data" --env-file .env meditrack-backend
```

## Deploy notes

For a demo, SQLite is suitable. For production, move `DATABASE_URL` to PostgreSQL, put the API behind TLS, authenticate device telemetry, and use a durable notification/outbox worker before sending clinical alerts. Never commit `.env` or credentials.
