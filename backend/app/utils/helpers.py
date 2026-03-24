from datetime import datetime


def average_busy_level(reports: list[dict]) -> float | None:
    """
    Calculate simple average busy level from a list of crowd reports.
    Each report should have 'busy_level' (int).
    Returns None if no reports.
    """
    if not reports:
        return None

    total = sum(r["busy_level"] for r in reports)
    return round(total / len(reports), 1)


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document _id to string id."""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


def serialize_docs(docs: list[dict]) -> list[dict]:
    """Convert list of MongoDB documents."""
    return [serialize_doc(doc) for doc in docs]
