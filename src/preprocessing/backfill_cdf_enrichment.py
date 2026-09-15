"""
Phase 7 (Validation) fix - spot-check against the original source
revealed that SRC-CDF-038 and SRC-CDF-040's contractor/beneficiary
enrichment (added by the Leader after reading the March newsletter)
never made it into the canonical CDF dataset, because Member 2's
independent extraction only captured the original short news post,
not this later enrichment.

Backfills contractor (direct field) and beneficiaries (folded into
project_description, since canonical schema has no beneficiaries
column) for exactly these rows, from data/interim/cdf_news_derived.csv,
without touching any other row.
"""
from __future__ import annotations

import csv
from pathlib import Path

CANONICAL = Path("data/final/db-unza26-csc4792-livingstone_city_council_cdf_projects.csv")
NEWS_DERIVED = Path("data/interim/cdf_news_derived.csv")

TARGET_IDS = {"SRC-CDF-038", "SRC-CDF-039", "SRC-CDF-040"}


def main() -> None:
    with NEWS_DERIVED.open("r", encoding="utf-8", newline="") as f:
        news_by_id = {r["source_id"]: r for r in csv.DictReader(f, delimiter="|")}

    with CANONICAL.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))
        fieldnames = list(rows[0].keys())

    updated = 0
    for r in rows:
        if r["source_id"] not in TARGET_IDS:
            continue
        source = news_by_id.get(r["source_id"])
        if not source:
            continue

        changed = False
        if source.get("contractor") and not r.get("contractor"):
            r["contractor"] = source["contractor"]
            changed = True
        if source.get("beneficiaries") and "Beneficiaries:" not in r["project_description"]:
            r["project_description"] = r["project_description"] + f" [Beneficiaries: {source['beneficiaries']}]"
            changed = True
        if changed:
            updated += 1
            print(f"Backfilled {r['source_id']}: contractor={r['contractor']!r}")

    with CANONICAL.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        w.writeheader()
        w.writerows(rows)

    print(f"\n{updated} row(s) backfilled.")


if __name__ == "__main__":
    main()
