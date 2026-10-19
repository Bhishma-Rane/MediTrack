from datetime import date

from meditrack.analytics import adherence_rate, average_response_time, classify_log
from meditrack.reporting import build_compliance_pdf


def test_adherence_and_response_metrics_handle_empty_and_values():
    assert adherence_rate([]) == 0.0
    assert adherence_rate(["TAKEN", "MISSED", "TAKEN"]) == 66.7
    assert average_response_time([10, None, 20]) == 15.0


def test_log_category_marks_late_taken_doses():
    assert classify_log("MISSED", None, None, None) == "MISSED"
    assert classify_log("TAKEN", 30, None, None) == "LATE"
    assert classify_log("TAKEN", 0, None, None) == "TAKEN"


def test_compliance_pdf_is_a_valid_pdf_with_incident_data():
    content = build_compliance_pdf("Asha Rane", [{
        "timestamp": "2026-10-18T08:16:00+00:00", "status": "MISSED",
        "target_timestamp": "2026-10-18T08:00:00+00:00",
        "response_time_sec": None, "medication_name": "Lisinopril", "late": False,
    }], date(2026, 10, 18))
    assert content.startswith(b"%PDF")
    assert len(content) > 1000
