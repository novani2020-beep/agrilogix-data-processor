"""CLI entry point for the AgriLogix Data Processor."""

import argparse
from src.exporter import export_results
from src.parser import load_manifest
from src.validator import validate_record


def run_pipeline(input_path: str, output_path: str) -> None:
    """Execute end-to-end parsing, validation, and export."""
    raw_records = load_manifest(input_path)
    valid_records = []
    rejected_records = []

    for row in raw_records:
        is_valid, result = validate_record(row)
        if is_valid:
            valid_records.append(result)
        else:
            rejected_records.append(result)

    saved_path = export_results(valid_records, rejected_records, output_path)
    print(
        f"Processed {len(raw_records)} rows -> "
        f"{len(valid_records)} valid, {len(rejected_records)} rejected. "
        f"Saved report to {saved_path}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and process agricultural manifests.")
    parser.add_argument("--input", required=True, help="Path to input CSV manifest.")
    parser.add_argument("--output", required=True, help="Path to output JSON summary.")
    args = parser.parse_args()
    run_pipeline(args.input, args.output)


if __name__ == "__main__":
    main()
