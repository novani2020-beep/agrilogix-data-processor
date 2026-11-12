"""Validation rules and post-harvest spoilage risk evaluation."""

from datetime import date, datetime
from typing import Any

# Maximum recommended transit/storage days before high spoilage risk
SHELF_LIFE_DAYS: dict[str, int] = {
    "tomatoes": 5,
    "leafy greens": 3,
    "plantain": 10,
    "cassava tubers": 7,
    "yam": 30,
    "dried grains": 180,
}

DEFAULT_SHELF_LIFE = 7


def calculate_spoilage_risk(commodity: str, harvest_dt: date, reference_dt: date) -> str:
    """Classify post-harvest spoilage risk based on elapsed days."""
    elapsed_days = max((reference_dt - harvest_dt).days, 0)
    max_days = SHELF_LIFE_DAYS.get(commodity.lower(), DEFAULT_SHELF_LIFE)
    ratio = elapsed_days / max_days

    if ratio >= 0.75:
        return "HIGH"
    if ratio >= 0.40:
        return "MEDIUM"
    return "LOW"


def validate_record(
    raw_record: dict[str, Any], reference_date: date | None = None
) -> tuple[bool, dict[str, Any]]:
    """Validate a single manifest row and return (is_valid, processed_or_error_dict)."""
    ref_date = reference_date or date.today()
    required_fields = ["batch_id", "commodity", "weight_kg", "harvest_date", "unit_price_ngn"]

    for field in required_fields:
        if not raw_record.get(field):
            return False, {
                "line": raw_record.get("_source_line"),
                "batch_id": raw_record.get("batch_id", "UNKNOWN"),
                "error": f"Missing required field: {field}",
            }

    try:
        weight = float(raw_record["weight_kg"])
        unit_price = float(raw_record["unit_price_ngn"])
        if weight <= 0 or unit_price < 0:
            raise ValueError("Weight must be positive and price non-negative.")
    except ValueError as exc:
        return False, {
            "line": raw_record.get("_source_line"),
            "batch_id": raw_record["batch_id"],
            "error": f"Numeric parsing error: {exc}",
        }

    try:
        harvest_dt = datetime.strptime(raw_record["harvest_date"], "%Y-%m-%d").date()
    except ValueError:
        return False, {
            "line": raw_record.get("_source_line"),
            "batch_id": raw_record["batch_id"],
            "error": f"Invalid date format (expected YYYY-MM-DD): {raw_record['harvest_date']}",
        }

    commodity = raw_record["commodity"].title()
    risk_level = calculate_spoilage_risk(commodity, harvest_dt, ref_date)

    return True, {
        "batch_id": raw_record["batch_id"].upper(),
        "commodity": commodity,
        "weight_kg": round(weight, 2),
        "unit_price_ngn": round(unit_price, 2),
        "total_value_ngn": round(weight * unit_price, 2),
        "harvest_date": harvest_dt.isoformat(),
        "destination_hub": raw_record.get("destination_hub", "Unassigned").title(),
        "spoilage_risk": risk_level,
    }
