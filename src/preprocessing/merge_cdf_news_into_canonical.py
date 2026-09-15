"""
Phase 6 (Integration) - merge the 9 unique CDF records found via
Member 5's newsletter reads (cdf_news_derived.csv) into the canonical
CDF dataset, mapping fields into its schema.

The 3 records already present in both files (SRC-CDF-038/039/040,
independently extracted by Member 2's regex-on-notes approach) are
excluded here to avoid duplication - Member 2's version is kept as
canonical for those, since it's part of the audited extraction
pipeline. Only the 9 records unique to cdf_news_derived.csv are added.
"""
from __future__ import annotations

import csv
from pathlib import Path

CANONICAL = Path("data/final/db-unza26-csc4792-livingstone_city_council_cdf_projects.csv")
NEWS_DERIVED = Path("data/final/cdf_news_derived.csv")

ALREADY_PRESENT = {"SRC-CDF-038", "SRC-CDF-039", "SRC-CDF-040"}

CANONICAL_FIELDS = ["source_id", "cdf_year", "project_number", "project_description",
                    "ward", "project_type", "project_cost", "status",
                    "completion_pct", "contractor", "source_page", "source_url"]


def map_row(r: dict) -> dict:
    extras = []
    if r.get("constituency"):
        extras.append(f"Constituency: {r['constituency']}")
    if r.get("beneficiaries"):
        extras.append(f"Beneficiaries: {r['beneficiaries']}")
    if r.get("location"):
        extras.append(f"Location: {r['location']}")
    description = r.get("description", "").strip()
    name = r.get("project_name", "").strip()
    full_description = name
    if description:
        full_description += f" - {description}"
    if extras:
        full_description += " [" + "; ".join(extras) + "]"

    return {
        "source_id": r["source_id"],
        "cdf_year": r.get("cdf_year", ""),
        "project_number": "",
        "project_description": full_description,
        "ward": r.get("ward", ""),
        "project_type": r.get("project_category", ""),
        "project_cost": r.get("project_cost", ""),
        "status": r.get("status", ""),
        "completion_pct": r.get("completion_percentage", ""),
        "contractor": r.get("contractor", ""),
        "source_page": "",
        "source_url": r.get("source_url", ""),
    }


def main() -> None:
    with CANONICAL.open("r", encoding="utf-8", newline="") as f:
        canonical_rows = list(csv.DictReader(f, delimiter="|"))
        fieldnames = list(canonical_rows[0].keys())

    with NEWS_DERIVED.open("r", encoding="utf-8", newline="") as f:
        news_rows = list(csv.DictReader(f, delimiter="|"))

    to_add = [r for r in news_rows if r["source_id"] not in ALREADY_PRESENT]
    print(f"Canonical file: {len(canonical_rows)} existing rows")
    print(f"News-derived file: {len(news_rows)} rows, {len(to_add)} not already present, {len(news_rows) - len(to_add)} skipped as duplicates")

    mapped = [map_row(r) for r in to_add]
    all_rows = canonical_rows + mapped

    with CANONICAL.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        w.writeheader()
        w.writerows(all_rows)

    print(f"\nFinal canonical CDF dataset: {len(all_rows)} rows")
    for r in mapped:
        print(f"  ADDED: {r['source_id']} - {r['project_description'][:60]}")


if __name__ == "__main__":
    main()
