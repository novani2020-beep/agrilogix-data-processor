"""Module for reading and normalizing raw agricultural manifest files."""

import csv
from pathlib import Path
from typing import Any


def load_manifest(file_path: str | Path) -> list[dict[str, Any]]:
    """Read a CSV manifest and strip extraneous whitespace from keys and values."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input manifest not found: {path}")

    records: list[dict[str, Any]] = []
    with path.open(mode="r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for line_num, row in enumerate(reader, start=2):
            cleaned_row = {
                key.strip().lower(): (value.strip() if value is not None else "")
                for key, value in row.items()
                if key is not None
            }
            cleaned_row["_source_line"] = line_num
            records.append(cleaned_row)

    return records
