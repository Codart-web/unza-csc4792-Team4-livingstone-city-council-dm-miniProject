"""
Phase 3 (Extraction) - CDF news-derived project records.

These 3 records were manually reviewed from actual news article text
during Phase 1b (see docs/decisions/decision_log.md, 2026-09-11
reclassification entry, and docs/source_register/source_register.csv
rows SRC-CDF-038 to 040 for the source-of-truth notes). This script
formalizes those already-verified facts into the CDF Projects dataset
schema, with full source provenance retained.

Output: data/interim/cdf_news_derived.csv (pipe-delimited).
"""
from __future__ import annotations

import csv
from pathlib import Path

RECORDS = [
    {
        "project_id": "CDF-2025-MARAMBA-SEWER",
        "source_id": "SRC-CDF-038",
        "cdf_year": "2025",
        "ward": "Maramba (R Section)",
        "constituency": "Livingstone",
        "project_name": "Backbone Sewer Installation",
        "project_category": "Sanitation",
        "description": "Installation of backbone sewer pipes in R Section of Maramba Ward",
        "project_cost": "719972.00",
        "status": "In Progress",
        "completion_percentage": "80",
        "contractor": "",
        "beneficiaries": "",
        "location": "Maramba Ward",
        "source_url": "https://www.livingstonecouncil.gov.zm/?p=4850",
    },
    {
        "project_id": "CDF-2025-LINDA-ROADS",
        "source_id": "SRC-CDF-039",
        "cdf_year": "2025",
        "ward": "Nansanzu",
        "constituency": "Livingstone",
        "project_name": "Road Grading and Gravelling - Linda Township",
        "project_category": "Roads",
        "description": "Grading, damping and spreading of gravel; watering and compaction of 3.3km of road, undertaken by the Council under force account (no external contractor)",
        "project_cost": "377208.75",
        "status": "In Progress",
        "completion_percentage": "70",
        "contractor": "",
        "beneficiaries": "",
        "location": "Linda Township, Nansanzu Ward",
        "source_url": "https://www.livingstonecouncil.gov.zm/?p=5014",
    },
    {
        "project_id": "CDF-2025-KASIYA-WATER",
        "source_id": "SRC-CDF-040",
        "cdf_year": "2025",
        "ward": "Kasiya",
        "constituency": "Livingstone",
        "project_name": "Kasiya Ward Water Boost - 8 Boreholes",
        "project_category": "Water",
        "description": "Drilling of 8 boreholes, benefiting 6 zones: Mahululo, Chaba, Natebe community, Natebe Dam, Kasiya, Daka Munyama",
        "project_cost": "1053507.00",
        "status": "Completed",
        "completion_percentage": "100",
        "contractor": "Buildstrong General Dealers",
        "beneficiaries": "Mahululo, Chaba, Natebe community, Natebe Dam, Kasiya, Daka Munyama",
        "location": "Kasiya Ward",
        "source_url": "https://www.livingstonecouncil.gov.zm/?p=5031",
    },
]

FIELDNAMES = [
    "project_id", "source_id", "cdf_year", "ward", "constituency",
    "project_name", "project_category", "description", "project_cost",
    "status", "completion_percentage", "contractor", "beneficiaries",
    "location", "source_url",
]

OUT_PATH = Path("data/interim/cdf_news_derived.csv")


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter="|")
        w.writeheader()
        w.writerows(RECORDS)
    print(f"Wrote {len(RECORDS)} CDF project records to {OUT_PATH}")
    for r in RECORDS:
        print(f"  {r['project_id']}: {r['project_name']} ({r['ward']}, K{r['project_cost']})")


if __name__ == "__main__":
    main()
