"""
Phase 3 (Extraction) - additional CDF records found in the March 2026
"Voice of Livingstone" newsletter (SRC-GOVE-016), discovered during
Member 5's full multi-page read of the newsletter.
"""
from __future__ import annotations

import csv
from pathlib import Path

INTERIM = Path("data/interim/cdf_news_derived.csv")
SOURCE_URL = "http://www.livingstonecouncil.gov.zm/wp-content/uploads/2026/04/LCC-March-news-2026.pdf"
SOURCE_ID = "SRC-GOVE-016"

NEW_RECORDS = [
    {
        "project_id": "CDF-2024-STRAPHAEL-ABLUTION",
        "source_id": SOURCE_ID, "cdf_year": "2024", "ward": "",
        "constituency": "Livingstone",
        "project_name": "Rehabilitation of ablution block, St. Raphael Secondary School",
        "project_category": "Education/Sanitation",
        "description": "Rehabilitation of an ablution block, commissioned alongside other 2024/2025 CDF projects",
        "project_cost": "549848.00", "status": "Completed", "completion_percentage": "100",
        "contractor": "", "beneficiaries": "", "location": "St. Raphael Secondary School",
        "source_url": SOURCE_URL,
    },
    {
        "project_id": "CDF-2024-LIBUYU-STREETLIGHTS",
        "source_id": SOURCE_ID, "cdf_year": "2024", "ward": "Libuyu",
        "constituency": "Livingstone",
        "project_name": "Solar streetlights installation, Mukuni Road",
        "project_category": "Infrastructure/Lighting",
        "description": "Installation of solar streetlights along Mukuni Road, Libuyu Ward",
        "project_cost": "555318.00", "status": "Completed", "completion_percentage": "100",
        "contractor": "", "beneficiaries": "", "location": "Mukuni Road, Libuyu Ward",
        "source_url": SOURCE_URL,
    },
    {
        "project_id": "CDF-2024-MOSIOATUNYA-STREETLIGHTS",
        "source_id": SOURCE_ID, "cdf_year": "2024", "ward": "Mosi-oa-Tunya",
        "constituency": "Livingstone",
        "project_name": "Solar streetlights installation, Mosi-oa-Tunya Ward",
        "project_category": "Infrastructure/Lighting",
        "description": "Installation of solar streetlights in Mosi-oa-Tunya Ward",
        "project_cost": "1194480.00", "status": "Completed", "completion_percentage": "100",
        "contractor": "", "beneficiaries": "", "location": "Mosi-oa-Tunya Ward",
        "source_url": SOURCE_URL,
    },
    {
        "project_id": "CDF-2025-SKIP-LOADER-TRUCK",
        "source_id": SOURCE_ID, "cdf_year": "2025", "ward": "",
        "constituency": "Livingstone",
        "project_name": "Procurement of Skip Loader Truck",
        "project_category": "Equipment/Waste Management",
        "description": "Procurement of a skip loader truck for garbage collection. COST DISCREPANCY IN SOURCE: article states 'approximately K2.2 million' in one paragraph and 'K2 million' in another, referring to the same truck. Not resolved - both figures documented per Rule 2 (never invent/guess a single value).",
        "project_cost": "2200000.00 OR 2000000.00 (see description - source discrepancy)",
        "status": "Completed", "completion_percentage": "100",
        "contractor": "", "beneficiaries": "", "location": "Livingstone (city-wide)",
        "source_url": SOURCE_URL,
    },
    {
        "project_id": "CDF-2025-KALALUKA-STAFFHOUSE",
        "source_id": SOURCE_ID, "cdf_year": "2025", "ward": "",
        "constituency": "Livingstone",
        "project_name": "Kalaluka Health Post staff house",
        "project_category": "Health",
        "description": "Construction of semi-detached staff house, water reticulation system, and incinerator at Kalaluka Health Post",
        "project_cost": "1800000.00", "status": "In Progress", "completion_percentage": "80",
        "contractor": "", "beneficiaries": "", "location": "Kalaluka Health Post",
        "source_url": SOURCE_URL,
    },
    {
        "project_id": "CDF-2025-SIMONGA-MARKET-SHELTER",
        "source_id": SOURCE_ID, "cdf_year": "2025", "ward": "",
        "constituency": "Livingstone",
        "project_name": "Simonga Market Shelter",
        "project_category": "Markets/Commerce",
        "description": "Construction of market shelter, concrete lockable stands, and electrification at Simonga Market",
        "project_cost": "1273482.00", "status": "Nearly Complete", "completion_percentage": "99.99",
        "contractor": "F. Kamwi Ventures Ltd", "beneficiaries": "", "location": "Simonga Market",
        "source_url": SOURCE_URL,
    },
]

ENRICH_PROJECT_ID = "CDF-2025-MARAMBA-SEWER"
ENRICH_UPDATES = {
    "contractor": "Southern Water and Sanitation Company",
    "beneficiaries": "133 houses to be connected",
}


def main() -> None:
    with INTERIM.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))
        fieldnames = list(rows[0].keys())

    enriched = False
    for r in rows:
        if r["project_id"] == ENRICH_PROJECT_ID:
            r.update(ENRICH_UPDATES)
            enriched = True

    if not enriched:
        print(f"WARNING: {ENRICH_PROJECT_ID} not found - enrichment skipped.")
    else:
        print(f"Enriched {ENRICH_PROJECT_ID} with contractor and beneficiaries.")

    rows.extend(NEW_RECORDS)

    with INTERIM.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        w.writeheader()
        w.writerows(rows)

    print(f"\nTotal CDF records now: {len(rows)}")
    for r in NEW_RECORDS:
        print(f"  NEW: {r['project_id']} - {r['project_name']} (K{r['project_cost']})")


if __name__ == "__main__":
    main()
