"""Pure analytics helpers shared by the dashboard and PDF report."""

from collections.abc import Iterable


def adherence_rate(statuses: Iterable[str]) -> float:
    values = list(statuses)
    return round(sum(status == "TAKEN" for status in values) / len(values) * 100, 1) if values else 0.0


def average_response_time(response_times: Iterable[int | None]) -> float:
    values = [value for value in response_times if value is not None]
    return round(sum(values) / len(values), 1) if values else 0.0


def classify_log(status: str, response_time_sec: int | None, target_time, timestamp) -> str:
    """Return the UI category required by the Part 4 log filter."""
    if status == "MISSED":
        return "MISSED"
    if status == "TAKEN" and response_time_sec is not None and target_time is not None:
        return "LATE" if response_time_sec > 0 else "TAKEN"
    return status
