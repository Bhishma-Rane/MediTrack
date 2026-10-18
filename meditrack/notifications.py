import asyncio
from datetime import datetime
from typing import Protocol


class SmsSender(Protocol):
    async def send(self, *, to: str, body: str) -> str: ...


class TwilioSmsSender:
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        from twilio.rest import Client
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    async def send(self, *, to: str, body: str) -> str:
        message = await asyncio.to_thread(self.client.messages.create, body=body, from_=self.from_number, to=to)
        return message.sid


class NullSmsSender:
    """Safe local default: records the event without making a network call."""

    async def send(self, *, to: str, body: str) -> str:
        return "dry-run"


async def alert_for_missed_dose(sender: SmsSender, *, patient, schedule, timestamp: datetime) -> bool:
    scheduled = datetime.combine(timestamp.date(), schedule.target_time_utc, tzinfo=timestamp.tzinfo)
    deadline = scheduled.timestamp() + schedule.grace_period_mins * 60
    if timestamp.timestamp() < deadline:
        return False
    body = (
        f"CRITICAL ALERT: Patient {patient.name} missed medication "
        f"{schedule.medication_name} scheduled for {scheduled.isoformat()}. Please check in."
    )
    await sender.send(to=patient.emergency_contact_phone, body=body)
    return True
