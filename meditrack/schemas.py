from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class TelemetryEvent(StrEnum):
    DOSE_TAKEN = "DOSE_TAKEN"
    DOSE_MISSED = "DOSE_MISSED"
    DOSE_SNOOZED = "DOSE_SNOOZED"


class TelemetryIn(BaseModel):
    device_id: str = Field(min_length=1, max_length=100)
    event: TelemetryEvent
    timestamp: datetime
    patient_id: int | None = Field(default=None, gt=0)
    schedule_id: int | None = Field(default=None, gt=0)
    compartment: int | None = Field(default=None, gt=0)
    latency_seconds: int | None = Field(default=None, ge=0)
    event_id: str | None = Field(default=None, max_length=200)

    @field_validator("timestamp")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include a timezone")
        return value


class TelemetryOut(BaseModel):
    accepted: bool
    duplicate: bool
    log_id: int
    status: str
