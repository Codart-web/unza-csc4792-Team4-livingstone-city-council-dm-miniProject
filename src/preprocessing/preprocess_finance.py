"""Phase 5 preprocessing for the Finance final datasets.

Phase 4 (cleaning) produced data/final/db-unza26-csc4792-livingstone_city_
council_finance_*.csv with whitespace stripped, numeric columns comma-free,
and exact duplicates removed. Phase 5 (preprocessing) goes one step further,
per the project's Phase 5 definition - "standardise/transform data" so it is
"analysis-ready", with every transformation justified:

1. Dates -> ISO 8601 (YYYY-MM-DD). The source documents write dates as
   free-text English ("1st January 2025", "31St March 2025" - note the
   inconsistent capitalisation in the source itself, "1-Jan-2025"). Each of
   these is an unambiguous representation of a single real date, so
   reformatting it to ISO is a pure notation change, not an inferred value.
   Applies to finance_capital_projects_raw's start_date/end_date and
   finance_debt_arrears_raw's outstanding_start_date/outstanding_end_date.

2. The free-text `period` column ("01-Jan-2025 to 30-Jun-2025", a report-
   level attribute repeated on every row) is replaced by two ISO columns,
   `period_start_date` and `period_end_date`, in finance_performance_raw and
   finance_capital_projects_raw. A sentence is not filterable/sortable; two
   explicit date columns are, and no information is lost since both bounds
   are preserved exactly.

3. Year columns (approved_budget_year, revised_budget_year,
   estimated_budget_year) and the two new period-date columns are validated
   to be sane (4-digit years in 2020-2035, valid ISO dates). Anomalies are
   reported, never silently corrected.

4. Categorical columns that appear in more than one source document
   (revenue_category across the three annual budgets) are checked for
   case/whitespace variants that should be the same category. None are
   changed unless a genuine case-only duplicate is found; if one is found it
   is reported, not silently merged.

Nothing here invents a value or changes what a value means - only how it is
written. This is idempotent: re-running it against its own output is a
no-op (dates already in ISO form parse straight through unchanged).
"""

from __future__ import annotations

import csv
import re
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FINAL_DIR = REPO_ROOT / "data" / "final"

ORDINAL_RE = re.compile(r"(\d+)(st|nd|rd|th)", re.IGNORECASE)
DATE_FORMATS = ("%d %B %Y", "%d-%b-%Y", "%Y-%m-%d")


def parse_date(text: str) -> str:
    """Convert a free-text or already-ISO date to YYYY-MM-DD.

    Returns the original text, unchanged, if it cannot be confidently
    parsed - never guesses at a date.
    """
    text = text.strip()
    if not text:
        return ""
    normalized = ORDINAL_RE.sub(r"\1", text)
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(normalized, fmt).date().isoformat()
        except ValueError:
            continue
    return text


def is_valid_year(value: str, low: int = 2020, high: int = 2035) -> bool:
    return bool(re.fullmatch(r"\d{4}", value)) and low <= int(value) <= high


def is_valid_iso_date(value: str) -> bool:
    if not value:
        return True  # blank is allowed, just not garbage text
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    return fieldnames, rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        writer.writerows(rows)


def split_period_column(
    fieldnames: list[str], rows: list[dict[str, str]]
) -> tuple[list[str], list[dict[str, str]], list[str]]:
    """Replace a free-text `period` column with period_start_date/period_end_date."""
    if "period" not in fieldnames:
        return fieldnames, rows, []

    warnings: list[str] = []
    new_fieldnames = [
        "period_start_date" if name == "period" else name
        for name in fieldnames
    ]
    new_fieldnames.insert(new_fieldnames.index("period_start_date") + 1, "period_end_date")

    new_rows = []
    for row in rows:
        period_text = row.get("period", "").strip()
        start_text, _, end_text = period_text.partition(" to ")
        start_iso = parse_date(start_text)
        end_iso = parse_date(end_text)
        if start_text and not is_valid_iso_date(start_iso):
            warnings.append(f"could not parse period start date: {start_text!r}")
        if end_text and not is_valid_iso_date(end_iso):
            warnings.append(f"could not parse period end date: {end_text!r}")

        new_row = {k: v for k, v in row.items() if k != "period"}
        new_row["period_start_date"] = start_iso
        new_row["period_end_date"] = end_iso
        new_rows.append(new_row)

    return new_fieldnames, new_rows, warnings


def convert_date_columns(
    rows: list[dict[str, str]], columns: tuple[str, ...]
) -> list[str]:
    warnings: list[str] = []
    for row in rows:
        for column in columns:
            if column not in row:
                continue
            original = row[column]
            converted = parse_date(original)
            if original.strip() and not is_valid_iso_date(converted):
                warnings.append(f"{column}: could not parse {original!r}")
            row[column] = converted
    return warnings


def check_year_columns(rows: list[dict[str, str]], columns: tuple[str, ...]) -> list[str]:
    warnings: list[str] = []
    for row in rows:
        for column in columns:
            value = row.get(column, "")
            if value and not is_valid_year(value):
                warnings.append(f"{column}: implausible year {value!r}")
    return warnings


def check_categorical_consistency(
    rows: list[dict[str, str]], column: str
) -> list[str]:
    warnings: list[str] = []
    seen_by_lower: dict[str, set[str]] = {}
    for row in rows:
        value = row.get(column, "")
        if not value:
            continue
        seen_by_lower.setdefault(value.lower(), set()).add(value)
    for lower, variants in seen_by_lower.items():
        if len(variants) > 1:
            warnings.append(f"{column}: case/whitespace variants of the same value: {sorted(variants)}")
    return warnings


def process_budget() -> list[str]:
    path = FINAL_DIR / "db-unza26-csc4792-livingstone_city_council_finance_budget.csv"
    fieldnames, rows = read_csv(path)
    warnings = check_year_columns(
        rows, ("approved_budget_year", "revised_budget_year", "estimated_budget_year")
    )
    warnings += check_categorical_consistency(rows, "revenue_category")
    write_csv(path, fieldnames, rows)  # no column changes; re-written for consistency
    return warnings


def process_performance() -> list[str]:
    path = FINAL_DIR / "db-unza26-csc4792-livingstone_city_council_finance_performance.csv"
    fieldnames, rows = read_csv(path)
    fieldnames, rows, warnings = split_period_column(fieldnames, rows)
    warnings += check_categorical_consistency(rows, "revenue_category")
    warnings += check_categorical_consistency(rows, "statement_section")
    write_csv(path, fieldnames, rows)
    return warnings


def process_capital_projects() -> list[str]:
    path = FINAL_DIR / "db-unza26-csc4792-livingstone_city_council_finance_capital_projects.csv"
    fieldnames, rows = read_csv(path)
    warnings = convert_date_columns(rows, ("start_date", "end_date"))
    fieldnames, rows, period_warnings = split_period_column(fieldnames, rows)
    warnings += period_warnings
    warnings += check_categorical_consistency(rows, "funding_source")
    warnings += check_categorical_consistency(rows, "project_status")
    write_csv(path, fieldnames, rows)
    return warnings


def process_debt_arrears() -> list[str]:
    path = FINAL_DIR / "db-unza26-csc4792-livingstone_city_council_finance_debt_arrears.csv"
    fieldnames, rows = read_csv(path)
    warnings = convert_date_columns(
        rows, ("outstanding_start_date", "outstanding_end_date")
    )
    write_csv(path, fieldnames, rows)
    return warnings


def main() -> int:
    steps = {
        "finance_budget": process_budget,
        "finance_performance": process_performance,
        "finance_capital_projects": process_capital_projects,
        "finance_debt_arrears": process_debt_arrears,
    }
    any_warnings = False
    for name, step in steps.items():
        warnings = step()
        if warnings:
            any_warnings = True
            print(f"{name}: {len(warnings)} warning(s)")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print(f"{name}: OK, no anomalies found")
    return 1 if any_warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
