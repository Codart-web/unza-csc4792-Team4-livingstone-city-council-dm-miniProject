"""
Fix a regression: 15 site-navigation rows were correctly marked
'rejected' earlier, but that edit only touched for_leader.csv
directly. A later regeneration of all per-member files FROM the
master (source_register.csv) overwrote them back to 'discovered',
since the master itself was never updated.

This time, fix the MASTER, then regenerate every per-member file from
it - the correct direction of data flow.
"""
from __future__ import annotations

import csv
from pathlib import Path
from collections import defaultdict

REG_DIR = Path("docs/source_register")
MASTER = REG_DIR / "source_register.csv"

NAV_NOTE = "Generic site-navigation/informational page - not a data source for this project"

with MASTER.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f, delimiter="|"))
    fieldnames = list(rows[0].keys())

fixed = 0
for r in rows:
    if r["data_domain"] == "other" and r["status"] == "discovered" and "?p=" not in r["url"]:
        r["status"] = "rejected"
        r["notes"] = NAV_NOTE
        fixed += 1

with MASTER.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
    w.writeheader()
    w.writerows(rows)

print(f"Fixed {fixed} rows in master (should be 15).")

by_member = defaultdict(list)
for r in rows:
    by_member[r["responsible_member"]].append(r)

for member, member_rows in by_member.items():
    slug = member.lower().replace(" ", "_")
    out = REG_DIR / f"for_{slug}.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        w.writeheader()
        w.writerows(member_rows)
    print(f"  Regenerated {out}: {len(member_rows)} rows")
