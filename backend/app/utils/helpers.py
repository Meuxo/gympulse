from datetime import datetime
import math


def time_decay_weight(timestamp: datetime, half_life_minutes: int = 30) -> float:
    """
    Calculate a time-decay weight for a crowd report.
    Uses exponential decay with a configurable half-life.
    Reports older than the half-life are weighted less.
    """
    now = datetime.utcnow()
    age_minutes = (now - timestamp).total_seconds() / 60
    if age_minutes < 0:
        age_minutes = 0
    return math.pow(0.5, age_minutes / half_life_minutes)


def weighted_average_busy_level(reports: list[dict], half_life_minutes: int = 30) -> float | None:
    """
    Calculate time-weighted average busy level from a list of crowd reports.
    Each report should have 'busy_level' (int) and 'timestamp' (datetime).
    Returns None if no reports.
    """
    if not reports:
        return None

    total_weight = 0.0
    weighted_sum = 0.0

    for report in reports:
        weight = time_decay_weight(report["timestamp"], half_life_minutes)
        weighted_sum += report["busy_level"] * weight
        total_weight += weight

    if total_weight == 0:
        return None

    return round(weighted_sum / total_weight, 1)


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document _id to string id."""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


def serialize_docs(docs: list[dict]) -> list[dict]:
    """Convert list of MongoDB documents."""
    return [serialize_doc(doc) for doc in docs]
