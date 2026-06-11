from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE_DIR = BACKEND_ROOT / "app" / "data" / "import_templates"
DEFAULT_CSV_DIR = DEFAULT_TEMPLATE_DIR / "csv"
MANIFEST_PATH = DEFAULT_TEMPLATE_DIR / "schema_manifest.json"

VALID_FLAGS = {"Y", "N"}
VALID_CONTACT_TYPES = {"Company Contact", "Contact Person", "Social Media"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ValidationError(Exception):
    pass


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValidationError(f"Missing schema manifest: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        raise ValidationError(f"Missing CSV file: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        rows = [
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
            if any((value or "").strip() for value in row.values())
        ]

    return headers, rows


def is_template_blank_row(row: dict[str, str]) -> bool:
    return not any(value.strip() for value in row.values())


def validate_headers(table_name: str, expected_headers: list[str], actual_headers: list[str]) -> list[str]:
    errors: list[str] = []
    if actual_headers != expected_headers:
        errors.append(
            f"{table_name}: headers do not match template.\n"
            f"  Expected: {expected_headers}\n"
            f"  Actual:   {actual_headers}"
        )
    return errors


def validate_required(table_name: str, required: list[str], rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(rows, start=2):
        for field in required:
            if not row.get(field):
                errors.append(f"{table_name}: row {index} missing required field '{field}'.")
    return errors


def validate_value_rules(table_name: str, rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []

    for index, row in enumerate(rows, start=2):
        for flag_field in ("show_flag", "show_pack_flag"):
            value = row.get(flag_field)
            if value and value not in VALID_FLAGS:
                errors.append(f"{table_name}: row {index} field '{flag_field}' must be Y or N.")

        contact_type = row.get("contact_type")
        if contact_type and contact_type not in VALID_CONTACT_TYPES:
            errors.append(
                f"{table_name}: row {index} contact_type must be one of: "
                f"{', '.join(sorted(VALID_CONTACT_TYPES))}."
            )

        for number_field in ("display_seq", "price", "sale_price", "stock_quantity", "low_stock_threshold"):
            value = row.get(number_field)
            if value:
                try:
                    float(value)
                except ValueError:
                    errors.append(f"{table_name}: row {index} field '{number_field}' must be numeric.")

        completed_date = row.get("completed_date")
        if completed_date and not DATE_RE.match(completed_date):
            errors.append(f"{table_name}: row {index} completed_date must use YYYY-MM-DD.")

        phone = row.get("phone_number")
        if phone:
            digits = re.sub(r"\D+", "", phone)
            if not (
                (digits.startswith("639") and len(digits) == 12)
                or (digits.startswith("09") and len(digits) == 11)
                or (digits.startswith("9") and len(digits) == 10)
                or (digits.startswith("0639") and len(digits) == 13)
            ):
                errors.append(
                    f"{table_name}: row {index} phone_number should be a Philippines mobile number "
                    f"such as +63 919 123 4567 or 0919 123 4567."
                )

    return errors


def validate_table(table_name: str, table_schema: dict[str, Any], csv_dir: Path) -> dict[str, Any]:
    csv_path = csv_dir / table_schema["file"]
    expected_headers = table_schema["headers"]
    required = table_schema.get("required", [])

    headers, rows = read_csv(csv_path)

    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(validate_headers(table_name, expected_headers, headers))
    errors.extend(validate_required(table_name, required, rows))
    errors.extend(validate_value_rules(table_name, rows))

    if not rows:
        warnings.append(f"{table_name}: no data rows found.")

    return {
        "table": table_name,
        "csv_file": str(csv_path),
        "rows": len(rows),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate RSA CMS launch CSV templates.")
    parser.add_argument("--csv-dir", default=str(DEFAULT_CSV_DIR), help="Folder containing CSV files.")
    parser.add_argument("--table", default="all", help="Table to validate, or all.")
    args = parser.parse_args()

    manifest = load_manifest(MANIFEST_PATH)
    tables: dict[str, Any] = manifest["tables"]
    csv_dir = Path(args.csv_dir)

    selected_tables = list(tables.keys()) if args.table == "all" else [args.table]
    for table in selected_tables:
        if table not in tables:
            raise SystemExit(f"Unknown table '{table}'. Valid tables: all, {', '.join(sorted(tables))}")

    print("RSA CMS / Mini-CRM Launch Data CSV Template Validator")
    print(f"CSV folder: {csv_dir}")
    print(f"Selected table(s): {', '.join(selected_tables)}")
    print("")

    total_errors = 0
    total_warnings = 0
    results = []

    for table in selected_tables:
        result = validate_table(table, tables[table], csv_dir)
        results.append(result)
        status = "OK" if not result["errors"] else "ERROR"
        print(f"{status:5} {table:16} rows={result['rows']} file={Path(result['csv_file']).name}")

        for warning in result["warnings"]:
            total_warnings += 1
            print(f"  WARNING: {warning}")

        for error in result["errors"]:
            total_errors += 1
            print(f"  ERROR: {error}")

    print("")
    print(f"Validation complete: {total_errors} error(s), {total_warnings} warning(s).")

    if total_errors:
        return 1

    print("Launch CSV templates are structurally valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
