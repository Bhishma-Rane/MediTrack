from contextlib import asynccontextmanager
from datetime import timezone

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from .config import get_settings
from .db import DeviceEvent, DoseLog, Patient, Schedule, get_db, init_db, make_engine, make_session_factory
from .live import ConnectionManager
from .notifications import NullSmsSender, TwilioSmsSender, alert_for_missed_dose
from .schemas import TelemetryEvent, TelemetryIn, TelemetryOut


def create_app(database_url: str | None = None, sms_sender=None) -> FastAPI:
    settings = get_settings()
    session_factory = make_session_factory(database_url or settings.database_url)
    engine = session_factory.kw["bind"]
    init_db(engine)
    manager = ConnectionManager()
    if sms_sender is None:
        sms_sender = (
            TwilioSmsSender(settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_from_number)
            if settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_from_number
            else NullSmsSender()
        )

    @asynccontextmanager
    async def lifespan(_app):
        yield

    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.state.database_url = database_url or settings.database_url

    def db_dependency():
        yield from get_db(session_factory)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/v1/telemetry", response_model=TelemetryOut)
    async def ingest(payload: TelemetryIn, db: Session = Depends(db_dependency)):
        event_id = payload.event_id or f"{payload.device_id}:{payload.timestamp.isoformat()}:{payload.event}"
        duplicate = db.query(DoseLog).filter(DoseLog.event_id == event_id).one_or_none()
        device_duplicate = db.query(DeviceEvent).filter(DeviceEvent.event_id == event_id).one_or_none()
        if duplicate:
            duplicate_event = duplicate.event_type or {
                "TAKEN": "DOSE_TAKEN", "MISSED": "DOSE_MISSED", "SNOOZED": "DOSE_SNOOZED",
            }.get(duplicate.status, duplicate.status)
            return TelemetryOut(accepted=True, duplicate=True, log_id=duplicate.log_id,
                                status=duplicate.status, event=TelemetryEvent(duplicate_event))
        if device_duplicate:
            return TelemetryOut(accepted=True, duplicate=True, log_id=device_duplicate.event_id_pk,
                                status=device_duplicate.event_type, event=TelemetryEvent(device_duplicate.event_type))
        occurred = payload.timestamp.astimezone(timezone.utc)
        if payload.event == TelemetryEvent.DEVICE_HEARTBEAT:
            heartbeat = DeviceEvent(device_id=payload.device_id, timestamp=occurred,
                                    event_type=payload.event.value, event_id=event_id)
            db.add(heartbeat)
            db.commit()
            db.refresh(heartbeat)
            await manager.broadcast({"type": "device.updated", "version": 1, "log_id": heartbeat.event_id_pk,
                                     "device_id": payload.device_id, "event": payload.event.value,
                                     "status": payload.event.value, "event_id": event_id,
                                     "timestamp": occurred.isoformat(), "alerted": False})
            return TelemetryOut(accepted=True, duplicate=False, log_id=heartbeat.event_id_pk,
                                status=payload.event.value, event=payload.event)
        schedule = db.get(Schedule, payload.schedule_id) if payload.schedule_id else None
        patient = db.get(Patient, payload.patient_id) if payload.patient_id else None
        if schedule and patient is None:
            patient = db.get(Patient, schedule.patient_id)
        if schedule is None and patient is not None:
            schedule = patient.schedules[0] if patient.schedules else None
        if not schedule or not patient:
            raise HTTPException(status_code=404, detail="patient and schedule are required or must exist")
        status = {"DOSE_TAKEN": "TAKEN", "DOSE_MISSED": "MISSED", "DOSE_SNOOZED": "SNOOZED"}.get(
            payload.event.value, payload.event.value
        )
        prior_missed = db.query(DoseLog).filter(
            DoseLog.patient_id == patient.patient_id,
            DoseLog.schedule_id == schedule.schedule_id,
            DoseLog.status == "MISSED",
        ).first() is not None
        log = DoseLog(patient_id=patient.patient_id, schedule_id=schedule.schedule_id, device_id=payload.device_id,
                      timestamp=occurred, status=status, response_time_sec=payload.latency_seconds,
                      event_id=event_id, event_type=payload.event.value, compartment=payload.compartment)
        db.add(log)
        db.commit()
        db.refresh(log)
        alerted = False
        if status == "MISSED" and not prior_missed:
            alerted = await alert_for_missed_dose(sms_sender, patient=patient, schedule=schedule, timestamp=occurred)
        await manager.broadcast({"type": "dose.updated", "version": 1, "log_id": log.log_id,
                                 "device_id": payload.device_id, "event": payload.event.value,
                                 "status": status, "patient_id": patient.patient_id,
                                 "schedule_id": schedule.schedule_id, "compartment": payload.compartment,
                                 "latency_seconds": payload.latency_seconds, "event_id": event_id,
                                 "timestamp": occurred.isoformat(), "alerted": alerted})
        return TelemetryOut(accepted=True, duplicate=False, log_id=log.log_id, status=status,
                            event=payload.event, alerted=alerted)

    @app.websocket("/ws/live-stream")
    async def live_stream(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await manager.disconnect(websocket)

    return app


app = create_app()
