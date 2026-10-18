from datetime import date, datetime, timedelta, timezone

import pandas as pd
import streamlit as st
from sqlalchemy import select

from meditrack.analytics import adherence_rate, classify_log
from meditrack.config import get_settings
from meditrack.db import DoseLog, Patient, Schedule, make_engine, make_session_factory
from meditrack.reporting import build_compliance_pdf


st.set_page_config(page_title="MediTrack Caregiver Dashboard", page_icon="💊", layout="wide")


@st.cache_resource
def session_factory():
    return make_session_factory(get_settings().database_url)


def load_data():
    db = session_factory()()
    try:
        patients = db.scalars(select(Patient).order_by(Patient.name)).all()
        logs = db.scalars(select(DoseLog).order_by(DoseLog.timestamp.desc())).all()
        schedules = db.scalars(select(Schedule)).all()
        schedule_map = {schedule.schedule_id: schedule for schedule in schedules}
        rows = []
        for log in logs:
            schedule = schedule_map.get(log.schedule_id)
            rows.append({"log_id": log.log_id, "timestamp": log.timestamp, "status": log.status,
                         "device_id": log.device_id, "response_time_sec": log.response_time_sec,
                         "patient_id": log.patient_id, "medication_name": schedule.medication_name if schedule else "—",
                         "target_time": schedule.target_time_utc if schedule else None,
                         "late": log.status == "TAKEN" and (log.response_time_sec or 0) > 0})
        return patients, pd.DataFrame(rows)
    finally:
        db.close()


st.title("💊 MediTrack Caregiver Dashboard")
st.caption("Live medication adherence and compliance reporting")
patients, logs = load_data()
if not patients:
    st.info("No patients are provisioned yet. Add a patient and schedule through the backend before opening this dashboard.")
    st.stop()

patient = st.sidebar.selectbox("Patient", patients, format_func=lambda item: item.name)
patient_logs = logs[logs["patient_id"] == patient.patient_id].copy() if not logs.empty else logs
st.sidebar.caption(f"Emergency contact: {patient.emergency_contact_phone}")

if patient_logs.empty:
    st.warning("No telemetry has been received for this patient yet.")
    filtered = patient_logs
else:
    latest = pd.to_datetime(patient_logs["timestamp"], utc=True).max().to_pydatetime()
    online = datetime.now(timezone.utc) - latest <= timedelta(minutes=5)
    col1, col2, col3 = st.columns(3)
    col1.metric("Node status", "ONLINE" if online else "OFFLINE")
    col2.metric("Last ping", latest.strftime("%Y-%m-%d %H:%M UTC"))
    col3.metric("Hardware health", "OK" if online else "CHECK DEVICE")
    status_filter = st.multiselect("Log status", ["TAKEN", "MISSED", "LATE"], default=["TAKEN", "MISSED", "LATE"])
    patient_logs["category"] = [classify_log(row.status, row.response_time_sec, row.target_time, row.timestamp)
                                 for row in patient_logs.itertuples()]
    filtered = patient_logs[patient_logs["category"].isin(status_filter)]

    taken_count = int((patient_logs["status"] == "TAKEN").sum())
    adherence = adherence_rate(patient_logs["status"])
    c1, c2 = st.columns(2)
    c1.metric("Adherence score", f"{adherence:.1f}%", help="Taken doses divided by received dose events")
    c2.metric("Taken doses", taken_count)
    st.progress(min(adherence / 100, 1.0), text=f"Adherence: {adherence:.1f}%")

st.subheader("Dose log")
if filtered.empty:
    st.info("No logs match the selected filters.")
else:
    st.dataframe(filtered[["timestamp", "medication_name", "status", "category", "response_time_sec", "device_id"]],
                 use_container_width=True, hide_index=True)

st.subheader("Compliance report")
report_rows = filtered.to_dict("records") if not filtered.empty else []
pdf = build_compliance_pdf(patient.name, report_rows, date.today())
st.download_button("Download PDF compliance report", data=pdf, file_name=f"meditrack-{patient.patient_id}-compliance.pdf", mime="application/pdf")
