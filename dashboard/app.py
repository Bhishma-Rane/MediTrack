from datetime import date, datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from meditrack.analytics import average_response_time, occurrence_adherence
from meditrack.config import get_settings
from meditrack.dashboard_data import load_dashboard_snapshot, scheduled_occurrences
from meditrack.db import make_session_factory
from meditrack.reporting import build_compliance_pdf


st.set_page_config(page_title="MediTrack Caregiver Dashboard", page_icon="💊", layout="wide")


@st.cache_resource
def session_factory():
    return make_session_factory(get_settings().database_url)


st.title("💊 MediTrack Caregiver Dashboard")
st.caption("Live medication adherence and compliance reporting")
end_date = st.sidebar.date_input("Report through", date.today())
start_date = st.sidebar.date_input("Report from", end_date - timedelta(days=29))
if start_date > end_date:
    st.error("The report start date must be on or before the end date.")
    st.stop()

db = session_factory()()
try:
    snapshot = load_dashboard_snapshot(db, start=start_date, end=end_date)
finally:
    db.close()

if not snapshot["patients"]:
    st.info("No patients are provisioned yet. Add a patient and schedule through the backend before opening this dashboard.")
    st.stop()

patient = st.sidebar.selectbox("Patient", snapshot["patients"], format_func=lambda item: item["name"])
patient_id = patient["patient_id"]
now = datetime.now(timezone.utc)
occurrences = scheduled_occurrences(snapshot, patient_id=patient_id, start=start_date, end=end_date, now=now)
patient_logs = [log for log in snapshot["logs"] if log["patient_id"] == patient_id]
latest = max((log["timestamp"] for log in patient_logs), default=None)
online = latest is not None and now - latest.astimezone(timezone.utc) <= timedelta(minutes=5)

c1, c2, c3 = st.columns(3)
c1.metric("Node status", "ONLINE" if online else "OFFLINE")
c2.metric("Last telemetry", latest.strftime("%Y-%m-%d %H:%M UTC") if latest else "No telemetry")
c3.metric("Hardware health", "Unavailable" if latest is None else "Telemetry active")

status_filter = st.multiselect("Log status", ["TAKEN", "MISSED", "LATE"], default=["TAKEN", "MISSED", "LATE"])
adherence = occurrence_adherence(occurrences)
taken = [item for item in occurrences if item["status"] == "TAKEN"]
late = [item for item in taken if item["late"]]
missed = [item for item in occurrences if item["status"] == "MISSED"]
metrics = st.columns(4)
metrics[0].metric("Adherence score", f"{adherence:.1f}%", help="Taken scheduled occurrences divided by due occurrences")
metrics[1].metric("Due occurrences", len([item for item in occurrences if item["status"] != "PENDING"]))
metrics[2].metric("Missed doses", len(missed))
avg_response = average_response_time(item["response_time_sec"] for item in taken)
metrics[3].metric("Average response", f"{avg_response:.1f} sec")
st.progress(min(adherence / 100, 1.0), text=f"Adherence: {adherence:.1f}%")

rows = []
for item in occurrences:
    category = "LATE" if item["late"] else item["status"]
    if category in status_filter:
        rows.append({"scheduled": item["target_timestamp"], "medication": item["medication_name"],
                     "status": item["status"], "category": category, "taken_at": item["taken_timestamp"],
                     "response_time_sec": item["response_time_sec"]})
st.subheader("Scheduled dose log")
if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("No scheduled doses match the selected filters.")

report_rows = [{"timestamp": item["taken_timestamp"] or item["target_timestamp"], "status": item["status"],
                "target_timestamp": item["target_timestamp"], "response_time_sec": item["response_time_sec"],
                "medication_name": item["medication_name"], "late": item["late"]}
               for item in occurrences if item["status"] != "PENDING"]
st.subheader("Compliance report")
pdf = build_compliance_pdf(patient["name"], report_rows, end_date)
st.download_button("Download PDF compliance report", data=pdf,
                   file_name=f"meditrack-{patient_id}-compliance.pdf", mime="application/pdf")
