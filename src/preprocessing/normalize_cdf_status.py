"""
Phase 5/7 - normalize CDF project status casing to 4 consistent
categories, found necessary when notebook execution revealed 6
distinct strings for the same 4 real states.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

CANONICAL = Path("data/final/db-unza26-csc4792-livingstone_city_council_cdf_projects.csv")


def main() -> None:
    with CANONICAL.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))
        fieldnames = list(rows[0].keys())

    for r in rows:
        r["status"] = r["status"].strip().lower()

    with CANONICAL.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        w.writeheader()
        w.writerows(rows)

    print(Counter(r["status"] for r in rows))


if __name__ == "__main__":
    main()
