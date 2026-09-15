"""
Phase 4 (Cleaning) - light-touch cleaning pass across the real
datasets, given time constraints. Whitespace, numeric type coercion,
duplicate detection, and null-vs-zero discipline (never convert a
blank to 0).

Reads from data/interim/, writes cleaned versions to data/final/.
"""
from __future__ import annotations

import csv
from pathlib import Path

INTERIM = Path("data/interim")
FINAL = Path("data/final")
FINAL.mkdir(parents=True, exist_ok=True)


def clean_value(v: str) -> str:
    return (v or "").strip()


def clean_numeric(v: str) -> str:
    v = clean_value(v)
    if not v:
        return ""
    return v.replace(",", "")


NUMERIC_FIELDS = {
    "project_cost", "approved_budget", "revised_budget", "estimated_budget",
    "budget_value", "actual_value", "variance_value", "performance_pct",
    "completion_percentage", "outstanding_start", "outstanding_end",
}


def clean_csv(path: Path, out_path: Path) -> dict:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))
        fieldnames = list(rows[0].keys()) if rows else []

    seen = set()
    duplicates = 0
    cleaned_rows = []
    for r in rows:
        cleaned = {}
        for k, v in r.items():
            cleaned[k] = clean_numeric(v) if k in NUMERIC_FIELDS else clean_value(v)
        key = tuple(cleaned.items())
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        cleaned_rows.append(cleaned)

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        w.writeheader()
        w.writerows(cleaned_rows)

    return {"input_rows": len(rows), "output_rows": len(cleaned_rows), "duplicates_removed": duplicates}


def main() -> None:
    targets = list(INTERIM.glob("*.csv"))
    print(f"Found {len(targets)} interim CSVs to clean.\n")
    for path in targets:
        out_path = FINAL / path.name.replace("_raw", "_clean")
        stats = clean_csv(path, out_path)
        print(f"{path.name} -> {out_path.name}: {stats}")


if __name__ == "__main__":
    main()
