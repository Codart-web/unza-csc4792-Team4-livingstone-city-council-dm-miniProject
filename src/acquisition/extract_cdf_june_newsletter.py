"""
Phase 3 (Extraction) - additional CDF records from the June 2026
newsletter (SRC-GOVE-017), found by Member 5's full multi-page read.
"""
from __future__ import annotations
import csv
from pathlib import Path

INTERIM = Path("data/interim/cdf_news_derived.csv")
SOURCE_URL = "http://www.livingstonecouncil.gov.zm/wp-content/uploads/2026/09/LCC-June-news-2026.pdf"
SOURCE_ID = "SRC-GOVE-017"

NEW_RECORDS = [
    {
        "project_id": "CDF-2025-KABILA-WATERTANK",
        "source_id": SOURCE_ID, "cdf_year": "2025", "ward": "Kabila",
        "constituency": "Livingstone", "project_name": "Water Tank Installation",
        "project_category": "Water",
        "description": "Installation of a water tank in Kabila Ward; site-visited by CDF Committee as a completed 2025 community project.",
        "project_cost": "", "status": "Completed", "completion_percentage": "100",
        "contractor": "", "beneficiaries": "", "location": "Kabila Ward",
        "source_url": SOURCE_URL,
    },
    {
        "project_id": "CDF-2025-ZAMBEZI-DRAINAGE",
        "source_id": SOURCE_ID, "cdf_year": "2025", "ward": "Zambezi",
        "constituency": "Livingstone", "project_name": "Zambezi Drainage Phase V",
        "project_category": "Drainage",
        "description": "Zambezi Drainage project in Zambezi Ward; site-visited by CDF Committee as a completed 2025 community project; also listed among 13 CDF projects commissioned June 2026.",
        "project_cost": "", "status": "Completed", "completion_percentage": "100",
        "contractor": "", "beneficiaries": "", "location": "Zambezi Ward",
        "source_url": SOURCE_URL,
    },
    {
        "project_id": "CDF-2025-RIVERSIDE-CROSSING",
        "source_id": SOURCE_ID, "cdf_year": "2025", "ward": "",
        "constituency": "Livingstone", "project_name": "Crossing point at Riverside Market and Burton",
        "project_category": "Infrastructure",
        "description": "Listed among 13 CDF projects commissioned June 2026. INSUFFICIENT DETAIL IN SOURCE: ward, cost, category, and contractor not stated anywhere in either newsletter. Documented gap, not a guess.",
        "project_cost": "", "status": "Completed", "completion_percentage": "",
        "contractor": "", "beneficiaries": "", "location": "Riverside Market / Burton area",
        "source_url": SOURCE_URL,
    },
]

with INTERIM.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f, delimiter="|"))
    fieldnames = list(rows[0].keys())

# Note-only updates, no invented percentages - flag possible completion
for r in rows:
    if r["project_id"] == "CDF-2025-KALALUKA-STAFFHOUSE":
        r["description"] += " UPDATE (June 2026 newsletter, photo caption, past tense): structure appears now constructed; exact revised completion percentage not stated in source, original 80% retained pending confirmation."
    if r["project_id"] == "CDF-2025-MARAMBA-SEWER":
        r["description"] += " UPDATE (June 2026 newsletter): listed among 13 CDF projects 'commissioned', implying completion; exact revised percentage not stated in source, original 80% retained pending confirmation."

rows.extend(NEW_RECORDS)

with INTERIM.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
    w.writeheader()
    w.writerows(rows)

print(f"Total CDF records now: {len(rows)}")
for r in NEW_RECORDS:
    print(f"  NEW: {r['project_id']} - {r['project_name']}")
