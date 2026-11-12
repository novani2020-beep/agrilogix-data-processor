"""Unit tests for record validation and spoilage risk scoring."""

from datetime import date
from src.validator import calculate_spoilage_risk, validate_record


def test_calculate_spoilage_risk_high():
    risk = calculate_spoilage_risk("Tomatoes", date(2026, 11, 1), date(2026, 11, 5))
    assert risk == "HIGH"


def test_calculate_spoilage_risk_low():
    risk = calculate_spoilage_risk("Yam", date(2026, 11, 1), date(2026, 11, 3))
    assert risk == "LOW"


def test_validate_record_success():
    sample = {
        "batch_id": "bch-001",
        "commodity": "tomatoes",
        "weight_kg": "200",
        "harvest_date": "2026-11-10",
        "destination_hub": "uyo",
        "unit_price_ngn": "500",
        "_source_line": 2,
    }
    is_valid, result = validate_record(sample, reference_date=date(2026, 11, 11))
    assert is_valid is True
    assert result["total_value_ngn"] == 100000.0
    assert result["spoilage_risk"] == "LOW"


def test_validate_record_invalid_date():
    sample = {
        "batch_id": "bch-002",
        "commodity": "plantain",
        "weight_kg": "150",
        "harvest_date": "not-a-date",
        "unit_price_ngn": "400",
        "_source_line": 3,
    }
    is_valid, result = validate_record(sample)
    assert is_valid is False
    assert "Invalid date format" in result["error"]
