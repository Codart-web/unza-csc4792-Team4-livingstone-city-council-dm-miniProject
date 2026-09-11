"""
Apply the manual review verdict on the 9 unlabeled news-post URLs:
- 3 irrelevant -> rejected, stay under LEADER
- 3 narrative/contextual -> verified but flagged as non-row source, stay under LEADER
- 3 genuine structured CDF project records -> reassigned to cdf domain,
  Member 2, given new source IDs, with the key facts captured in notes.

Then regenerates every per-member/leader CSV from the corrected master
so nothing drifts out of sync.
"""
from __future__ import annotations

import csv
from pathlib import Path
from collections import defaultdict

REG_DIR = Path("docs/source_register")
MASTER = REG_DIR / "source_register.csv"

REJECT = {
    "https://www.livingstonecouncil.gov.zm/?p=4839": "Flood relief food distribution - disaster relief aid, no financial/project structure, out of scope for CDF/finance/planning/governance datasets",
    "https://www.livingstonecouncil.gov.zm/?p=4904": "DVET/DVEC voter education training - electoral/civic training, unrelated to project data domains",
    "https://www.livingstonecouncil.gov.zm/?p=5024": "Republican President at ANTUSA Festival - sports/education union event, unrelated to project data domains",
}

CONTEXTUAL = {
    "https://www.livingstonecouncil.gov.zm/?p=4841": "Kashitu Local Area Plan (GIZ CitiZen+D) - planning narrative, no cost/structured data. Contextual only - cite in paper background, not extracted as a dataset row.",
    "https://www.livingstonecouncil.gov.zm/?p=4843": "Cash for Work programme sensitisation - corroborates CFW-advert.pdf (SRC-CDF-014) already registered. No new figures. Contextual only.",
    "https://www.livingstonecouncil.gov.zm/?p=5004": "Kashitu LAP - Mayor's visit narrative, no cost/structured data. Contextual only, same LAP initiative as p=4841.",
}

RECLASSIFY_TO_CDF = [
    {
        "url": "https://www.livingstonecouncil.gov.zm/?p=4850",
        "source_title": "Backbone Sewer Installation, Maramba Ward (news report)",
        "notes": "2025 CDF project. Cost K719,972. 80% complete at time of report. 3-month contract duration. Ward: Maramba (R Section).",
    },
    {
        "url": "https://www.livingstonecouncil.gov.zm/?p=5014",
        "source_title": "Road Works, Linda Township / Nansanzu Ward (news report)",
        "notes": "2025 CDF project. Cost K377,208.75. 70% complete at time of report. 3.3km grading/gravelling. Expected completion 8 April 2026.",
    },
    {
        "url": "https://www.livingstonecouncil.gov.zm/?p=5031",
        "source_title": "Kasiya Ward CDF Water Boost - 8 Boreholes (news report)",
        "notes": "2025 CDF allocation. Cost K1,053,507. 8 boreholes, 6 zones benefiting (Mahululo, Chaba, Natebe community, Natebe Dam, Kasiya, Daka Munyama). Contractor: Buildstrong General Dealers. Completed.",
    },
]

with MASTER.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f, delimiter="|"))
    fieldnames = list(rows[0].keys())

cdf_nums = [int(r["source_id"].split("-")[-1]) for r in rows if r["source_id"].startswith("SRC-CDF-")]
next_cdf_num = max(cdf_nums) + 1

new_rows = []
reclass_lookup = {r["url"]: r for r in RECLASSIFY_TO_CDF}

for r in rows:
    url = r["url"]
    if url in REJECT:
        r["status"] = "rejected"
        r["notes"] = REJECT[url]
        new_rows.append(r)
    elif url in CONTEXTUAL:
        r["status"] = "verified"
        r["notes"] = CONTEXTUAL[url]
        new_rows.append(r)
    elif url in reclass_lookup:
        info = reclass_lookup[url]
        r["source_id"] = f"SRC-CDF-{next_cdf_num:03d}"
        next_cdf_num += 1
        r["source_title"] = info["source_title"]
        r["data_domain"] = "cdf"
        r["responsible_member"] = "Member 2"
        r["status"] = "verified"
        r["extraction_method"] = "web scraping (structured facts extracted from news article text)"
        r["notes"] = info["notes"]
        new_rows.append(r)
    else:
        new_rows.append(r)

with MASTER.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
    w.writeheader()
    w.writerows(new_rows)

print(f"Master register updated: {len(new_rows)} rows total.")

by_member = defaultdict(list)
for r in new_rows:
    by_member[r["responsible_member"]].append(r)

for member, member_rows in by_member.items():
    slug = member.lower().replace(" ", "_")
    out = REG_DIR / f"for_{slug}.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        w.writeheader()
        w.writerows(member_rows)
    print(f"  {out}: {len(member_rows)} rows")
