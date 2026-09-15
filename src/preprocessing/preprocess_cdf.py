"""Phase 5 preprocessing for the CDF Projects final dataset.

Phase 4 (cleaning) produced data/final/db-unza26-csc4792-livingstone_city_
council_cdf_projects.csv with whitespace stripped, project_cost comma-free,
and exact duplicates removed. Phase 5 (preprocessing) makes one justified,
schema-level change and otherwise only validates:

1. `status` is split into `status` (a small category: approved / in
   progress / completed) and `completion_pct` (a number). The Phase 3
   extraction script had conflated these into one field (e.g. "80% complete"),
   but the project's own Phase 3 checklist lists "Status extracted" and
   "Completion information extracted where available" as two distinct
   things. "approved" and "completed" carry no stated percentage in the
   source, so completion_pct is left blank for them rather than guessed at
   (e.g. "completed" does NOT become completion_pct=100 - the source never
   printed that number).
2. `cdf_year` and `project_cost` are validated (year in a plausible range,
   cost numeric-or-blank and non-negative) - reported, not corrected.
3. Ward-name consistency is checked (case/whitespace-only variants of the
   same value). This does NOT catch "Maramba" vs "Maramba (R Section)"
   (SRC-CDF-012 vs SRC-CDF-038) because those are genuinely different
   strings, not a casing artifact - that discrepancy is left in the data
   and flagged in docs/team/findings_cdf_extraction.md for Phase 6
   Integration to resolve (is "R Section" a sub-area of the same ward, or a
   different one?), per the project rule to investigate and document
   disagreements rather than silently merge them.

Project descriptions are NOT edited here, even where a known OCR artifact
exists ("lkm", "l00001itre" - see findings_cdf_extraction.md). Fixing "lkm"
to "1km" is a confident single-character correction, but "l00001itre" has
no unambiguous digit reconstruction (10,000? 1,0001? something else?) -
guessing would fabricate a number, so both are left as printed and flagged
instead of partially edited.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET = (
    REPO_ROOT
    / "data"
    / "final"
    / "db-unza26-csc4792-livingstone_city_council_cdf_projects.csv"
)

COMPLETION_RE = re.compile(r"^(\d{1,3})%\s*complete$", re.IGNORECASE)

# Verified by reading each affected row's project_description: all three
# spellings describe the same road-grading-and-gravelling activity as the
# majority "Road works" (8 of 11 road-work rows). "Road Works" is a pure
# capitalisation variant; "Roads works" is a pluralisation variant. Both are
# in the source PDF itself, not introduced by extraction.
PROJECT_TYPE_CANONICAL = {
    "Road Works": "Road works",
    "Roads works": "Road works",
}


def split_status(value: str) -> tuple[str, str]:
    """Return (status, completion_pct) from a raw Phase 3 status value."""
    value = value.strip()
    match = COMPLETION_RE.match(value)
    if match:
        return "in progress", match.group(1)
    if value.lower() == "completed":
        return "completed", ""
    return value, ""


def is_valid_year(value: str, low: int = 2020, high: int = 2035) -> bool:
    return bool(re.fullmatch(r"\d{4}", value)) and low <= int(value) <= high


def is_valid_cost(value: str) -> bool:
    if not value:
        return True  # blank is allowed - the PDF table doesn't state costs
    try:
        return float(value) >= 0
    except ValueError:
        return False


def check_categorical_consistency(rows: list[dict[str, str]], column: str) -> list[str]:
    warnings: list[str] = []
    seen_by_lower: dict[str, set[str]] = {}
    for row in rows:
        value = row.get(column, "")
        if not value:
            continue
        seen_by_lower.setdefault(value.lower(), set()).add(value)
    for variants in seen_by_lower.values():
        if len(variants) > 1:
            warnings.append(f"{column}: case/whitespace variants of the same value: {sorted(variants)}")
    return warnings


def main() -> int:
    with DATASET.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    status_index = fieldnames.index("status")
    fieldnames = fieldnames[:status_index] + ["status", "completion_pct"] + fieldnames[status_index + 1:]

    warnings: list[str] = []
    fixes_applied = 0
    for row in rows:
        status, completion_pct = split_status(row["status"])
        row["status"] = status
        row["completion_pct"] = completion_pct

        canonical = PROJECT_TYPE_CANONICAL.get(row["project_type"])
        if canonical:
            row["project_type"] = canonical
            fixes_applied += 1

        if row["cdf_year"] and not is_valid_year(row["cdf_year"]):
            warnings.append(f"{row['source_id']}: implausible cdf_year {row['cdf_year']!r}")
        if not is_valid_cost(row["project_cost"]):
            warnings.append(f"{row['source_id']}: non-numeric/negative project_cost {row['project_cost']!r}")

    warnings += check_categorical_consistency(rows, "ward")
    warnings += check_categorical_consistency(rows, "project_type")

    with DATASET.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        writer.writerows(rows)

    print(f"project_type: standardised {fixes_applied} row(s) to canonical spelling 'Road works'")

    if warnings:
        print(f"{len(warnings)} unresolved warning(s):")
        for warning in warnings:
            print(f"  - {warning}")
        return 1

    print("cdf_projects: OK, no unresolved anomalies (status/completion_pct split applied; ward = 'Maramba' vs 'Maramba (R Section)' is a known, unresolved discrepancy - see findings_cdf_extraction.md, deliberately left unmerged since it is a different string, not a casing artifact)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
