from datetime import date, datetime, timedelta, timezone
import hmac

import pandas as pd
import streamlit as st

from meditrack.analytics import average_response_time, occurrence_adherence
from meditrack.admin import create_patient, create_schedule, list_admin_records
from meditrack.config import get_settings
from meditrack.dashboard_data import load_dashboard_snapshot, scheduled_occurrences
from meditrack.db import make_session_factory
from meditrack.reporting import build_compliance_pdf


st.set_page_config(page_title="MediTrack Caregiver Dashboard", page_icon="💊", layout="wide")


@st.cache_resource
def session_factory():
    return make_session_factory(get_settings().database_url)


st.title("💊 MediTrack Portal")
st.caption("Caregiver monitoring, compliance reports, and controlled administration")
dashboard_tab, admin_tab = st.tabs(["Caregiver dashboard", "Admin portal"])

with admin_tab:
    settings = get_settings()
    if not settings.admin_username or not settings.admin_password:
        st.warning("Admin portal is disabled. Set ADMIN_USERNAME and ADMIN_PASSWORD in .env, then restart Streamlit.")
    elif not st.session_state.get("admin_authenticated", False):
        st.subheader("Administrator sign in")
        with st.form("admin_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in")
        if submitted:
            valid_user = hmac.compare_digest(username, settings.admin_username)
            valid_password = hmac.compare_digest(password, settings.admin_password)
            if valid_user and valid_password:
                st.session_state["admin_authenticated"] = True
                st.rerun()
            st.error("Invalid administrator credentials.")
    else:
        st.subheader("Administration")
        if st.button("Sign out", key="admin_logout"):
            st.session_state["admin_authenticated"] = False
            st.rerun()
        admin_db = session_factory()()
        try:
            with st.expander("Register patient", expanded=True):
                with st.form("new_patient"):
                    name = st.text_input("Patient name")
                    emergency_phone = st.text_input("Emergency contact phone", placeholder="+15551234567")
                    doctor_email = st.text_input("Doctor email (optional)")
                    if st.form_submit_button("Create patient"):
                        try:
                            patient = create_patient(admin_db, name=name, emergency_contact_phone=emergency_phone, doctor_email=doctor_email)
                            st.success(f"Created patient {patient.name} (ID {patient.patient_id}).")
                            st.rerun()
                        except ValueError as error:
                            st.error(str(error))
            records = list_admin_records(admin_db)
            if records:
                with st.expander("Add medication schedule", expanded=True):
                    patient_choice = st.selectbox("Patient", records, format_func=lambda item: f"{item['name']} (ID {item['patient_id']})")
                    with st.form("new_schedule"):
                        medication = st.text_input("Medication name")
                        dosage = st.text_input("Dosage", placeholder="10 mg")
                        target = st.time_input("Target time (UTC)", value=datetime.now(timezone.utc).replace(second=0, microsecond=0).time())
                        grace = st.number_input("Grace period (minutes)", min_value=0, max_value=1440, value=15, step=1)
                        if st.form_submit_button("Create schedule"):
                            try:
                                create_schedule(admin_db, patient_id=patient_choice["patient_id"], medication_name=medication,
                                                dosage=dosage, target_time_utc=target, grace_period_mins=grace)
                                st.success("Medication schedule created.")
                                st.rerun()
                            except ValueError as error:
                                st.error(str(error))
            else:
                st.info("Create a patient before adding a medication schedule.")
            st.subheader("Registered patients and schedules")
            for record in list_admin_records(admin_db):
                st.write(f"**{record['name']}** · {record['emergency_contact_phone']} · ID {record['patient_id']}")
                for schedule in record["schedules"]:
                    st.caption(f"{schedule['medication_name']} · {schedule['dosage']} · {schedule['target_time_utc']} UTC · grace {schedule['grace_period_mins']} min")
        finally:
            admin_db.close()

with dashboard_tab:
    st.caption("Dashboard data is read-only; use the Admin portal to provision patients and schedules.")
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
        st.info("No patients are provisioned yet. Add a patient and schedule through the Admin portal.")
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
