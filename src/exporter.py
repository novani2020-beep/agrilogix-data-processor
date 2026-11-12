"""Module for writing structured validation summaries to JSON."""

import json
from pathlib import Path
from typing import Any


def export_results(
    valid_records: list[dict[str, Any]],
    rejected_records: list[dict[str, Any]],
    output_path: str | Path,
) -> Path:
    """Write processed records and summary metrics to a JSON file."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    high_risk_count = sum(1 for r in valid_records if r.get("spoilage_risk") == "HIGH")

    payload = {
        "summary": {
            "total_records": len(valid_records) + len(rejected_records),
            "valid_records": len(valid_records),
            "rejected_records": len(rejected_records),
            "high_spoilage_alerts": high_risk_count,
        },
        "records": valid_records,
        "errors": rejected_records,
    }

    with out_file.open(mode="w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return out_file
