"""Phase 4 cleaning for the CDF and Finance interim tables.

Scope for tonight, as agreed with the team leader - nothing more:

- strip leading/trailing whitespace from every header and every cell
- convert number-looking text in known numeric columns into plain numbers
  (strip thousands-separator commas: "1,234" -> "1234")
- remove exact duplicate rows (every field identical)
- a blank/missing value is NEVER turned into 0 or any other placeholder -
  it stays blank

This does not rename columns, reformat dates, standardise categories, or
touch any field not listed in NUMERIC_FIELDS below. Those are later
Phase 4/5 work, not tonight's narrow fix.

Reads data/interim/*_raw.csv (Phase 3 output, gitignored/local-only) and
writes data/final/db-unza26-csc4792-*.csv (tracked in Git).
"""

from __future__ import annotations

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INTERIM_DIR = REPO_ROOT / "data" / "interim"
FINAL_DIR = REPO_ROOT / "data" / "final"

# interim filename -> (final dataset description, numeric column names)
# Only columns listed as numeric are converted; everything else (including
# code-like fields such as item_code="001" or ward names) is left as text
# so leading zeros and identifiers are never silently altered.
DATASETS: dict[str, tuple[str, tuple[str, ...]]] = {
    "cdf_projects_raw.csv": (
        "livingstone_city_council_cdf_projects",
        ("project_cost",),
    ),
    "council_service_standards.csv": (
        "livingstone_city_council_service_standards",
        (),
    ),
    "finance_budget_raw.csv": (
        "livingstone_city_council_finance_budget",
        ("approved_budget", "revised_budget", "estimated_budget"),
    ),
    "finance_performance_raw.csv": (
        "livingstone_city_council_finance_performance",
        ("budget_value", "actual_value", "variance_value", "performance_pct"),
    ),
    "finance_capital_projects_raw.csv": (
        "livingstone_city_council_finance_capital_projects",
        ("contract_amount", "cumulative_payment", "balance"),
    ),
    "finance_debt_arrears_raw.csv": (
        "livingstone_city_council_finance_debt_arrears",
        ("outstanding_start_amount", "outstanding_end_amount"),
    ),
}


def clean_numeric(value: str) -> str:
    """Strip thousands-separator commas from a numeric-looking value.

    A truly blank value stays blank - it is never turned into 0. A value
    that isn't confidently numeric after stripping commas is returned
    unchanged rather than guessed at.
    """
    value = value.strip()
    if value == "":
        return ""
    candidate = value.replace(",", "")
    try:
        float(candidate)
    except ValueError:
        return value
    return candidate


def clean_rows(rows: list[dict[str, str]], numeric_fields: tuple[str, ...]) -> list[dict[str, str]]:
    cleaned: list[dict[str, str]] = []
    seen: set[tuple[tuple[str, str], ...]] = set()

    for row in rows:
        cleaned_row: dict[str, str] = {}
        for key, value in row.items():
            key = key.strip()
            value = (value or "").strip()
            if key in numeric_fields:
                value = clean_numeric(value)
            cleaned_row[key] = value

        dedup_key = tuple(sorted(cleaned_row.items()))
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        cleaned.append(cleaned_row)

    return cleaned


def clean_file(interim_name: str, description: str, numeric_fields: tuple[str, ...]) -> tuple[int, int] | None:
    src = INTERIM_DIR / interim_name
    if not src.exists():
        return None

    with src.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        fieldnames = [name.strip() for name in reader.fieldnames or []]
        rows = list(reader)

    before = len(rows)
    cleaned = clean_rows(rows, numeric_fields)
    after = len(cleaned)

    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    dest = FINAL_DIR / f"db-unza26-csc4792-{description}.csv"
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        writer.writerows(cleaned)

    return before, after


def main() -> int:
    for interim_name, (description, numeric_fields) in DATASETS.items():
        result = clean_file(interim_name, description, numeric_fields)
        if result is None:
            print(f"skip {interim_name}: not found locally (not this member's domain, or Phase 3 not run yet)")
            continue
        before, after = result
        dropped = before - after
        print(
            f"{interim_name} -> db-unza26-csc4792-{description}.csv: "
            f"{before} rows -> {after} rows ({dropped} exact duplicate(s) removed)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
