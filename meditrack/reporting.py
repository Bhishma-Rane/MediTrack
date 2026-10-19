from datetime import date, datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Flowable

from .analytics import adherence_rate, average_response_time


class DailyBarChart(Flowable):
    def __init__(self, daily_counts: dict[str, int], width=6.8 * inch, height=1.8 * inch):
        super().__init__()
        self.daily_counts, self.width, self.height = daily_counts, width, height

    def draw(self):
        canvas = self.canv
        maximum = max(max(self.daily_counts.values(), default=0), 1)
        bar_width = self.width / max(len(self.daily_counts), 1) * 0.65
        for index, (day, count) in enumerate(sorted(self.daily_counts.items())):
            x = index * self.width / max(len(self.daily_counts), 1) + 12
            bar_height = (count / maximum) * (self.height - 25)
            canvas.setFillColor(colors.HexColor("#2F80ED"))
            canvas.rect(x, 18, bar_width, bar_height, fill=1, stroke=0)
            canvas.setFillColor(colors.black)
            canvas.setFont("Helvetica", 7)
            canvas.drawCentredString(x + bar_width / 2, 6, day[-5:])


class TimingChart(Flowable):
    """Compare scheduled and actual hour for each daily dose occurrence."""
    def __init__(self, rows: list[dict], width=6.8 * inch, height=2.0 * inch):
        super().__init__()
        self.rows, self.width, self.height = rows, width, height

    def draw(self):
        canvas = self.canv
        rows = sorted(self.rows, key=lambda row: str(row.get("target_timestamp")))
        if not rows:
            return
        slot = self.width / len(rows)
        for index, row in enumerate(rows):
            x = index * slot + slot * 0.2
            target_value = row["target_timestamp"]
            if isinstance(target_value, str):
                target_value = datetime.fromisoformat(target_value)
            target = target_value.hour + target_value.minute / 60
            actual_value = row.get("timestamp")
            if isinstance(actual_value, str):
                actual_value = datetime.fromisoformat(actual_value)
            actual = actual_value.hour + actual_value.minute / 60 if actual_value else target
            scale = (self.height - 28) / 24
            canvas.setFillColor(colors.HexColor("#BDBDBD"))
            canvas.rect(x, 18, slot * 0.25, target * scale, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor("#2F80ED") if actual_value else colors.HexColor("#E57373"))
            canvas.rect(x + slot * 0.3, 18, slot * 0.25, actual * scale, fill=1, stroke=0)
            canvas.setFillColor(colors.black)
            canvas.setFont("Helvetica", 7)
            canvas.drawCentredString(x + slot * 0.28, 6, str(target_value)[:10][-5:])


def build_compliance_pdf(patient_name: str, logs: list[dict], report_date: date | None = None) -> bytes:
    """Build a portable medical compliance report from dashboard-ready records."""
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    taken = [log for log in logs if log["status"] == "TAKEN"]
    missed = [log for log in logs if log["status"] == "MISSED"]
    daily_counts: dict[str, int] = {}
    for log in logs:
        day = str(log["timestamp"])[:10]
        daily_counts[day] = daily_counts.get(day, 0) + (1 if log["status"] == "TAKEN" else 0)
    story = [Paragraph("MediTrack Medication Compliance Report", styles["Title"]),
             Paragraph(f"Patient: {patient_name}", styles["Heading2"]),
             Paragraph(f"Report date: {report_date or date.today()}", styles["Normal"]), Spacer(1, 12)]
    metrics = [["Adherence", "Average response time", "Missed doses"],
               [f"{adherence_rate(log['status'] for log in logs):.1f}%",
                f"{average_response_time(log.get('response_time_sec') for log in logs):.1f} sec",
                str(len(missed))]]
    metric_table = Table(metrics, colWidths=[2.15 * inch] * 3)
    metric_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF2FF")),
                                      ("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story += [metric_table, Spacer(1, 18), Paragraph("Daily taken doses", styles["Heading2"]), DailyBarChart(daily_counts), Spacer(1, 18),
              Paragraph("Target time (gray) vs actual time (blue; red means not taken)", styles["Heading2"]), TimingChart(logs), Spacer(1, 18)]
    incidents = [["Timestamp", "Status", "Medication", "Response (sec)"]]
    for log in logs:
        if log["status"] == "MISSED" or log.get("late"):
            incidents.append([str(log["timestamp"]), "MISSED" if log["status"] == "MISSED" else "LATE",
                              log.get("medication_name", "—"), str(log.get("response_time_sec") or "—")])
    if len(incidents) == 1:
        incidents.append(["—", "No incidents", "—", "—"])
    story += [Paragraph("Missed or delayed dose incidents", styles["Heading2"]), Table(incidents, repeatRows=1, colWidths=[2.2 * inch, 1.0 * inch, 2.0 * inch, 1.2 * inch])]
    story[-1].setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF2FF")), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 8)]))
    document.build(story)
    return buffer.getvalue()
