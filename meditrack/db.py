from collections.abc import Generator
from datetime import datetime, time

from sqlalchemy import DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class Patient(Base):
    __tablename__ = "patients"
    patient_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    emergency_contact_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    doctor_email: Mapped[str | None] = mapped_column(String(320))
    schedules: Mapped[list["Schedule"]] = relationship(back_populates="patient", cascade="all, delete-orphan")


class Schedule(Base):
    __tablename__ = "schedules"
    schedule_id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False)
    medication_name: Mapped[str] = mapped_column(String(200), nullable=False)
    dosage: Mapped[str] = mapped_column(String(100), nullable=False)
    target_time_utc: Mapped[time] = mapped_column(nullable=False)
    grace_period_mins: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    patient: Mapped[Patient] = relationship(back_populates="schedules")


class DoseLog(Base):
    __tablename__ = "dose_logs"
    log_id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.schedule_id"), nullable=False)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    response_time_sec: Mapped[int | None] = mapped_column(Integer)
    event_id: Mapped[str | None] = mapped_column(String(200), unique=True)


def make_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


def make_session_factory(database_url: str):
    return sessionmaker(bind=make_engine(database_url), expire_on_commit=False)


def init_db(engine) -> None:
    Base.metadata.create_all(engine)


def get_db(session_factory) -> Generator:
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
