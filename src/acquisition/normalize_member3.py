"""
Normalize Member 3's finance register: strip quotes, fix
responsible_member to "Member 3" for consistency with the rest of the
register. No merge conflict to resolve here - this is a clean commit,
just needs format normalization same as every other member's file.
"""
from __future__ import annotations

import csv
from pathlib import Path

SOURCE = Path("/tmp/member3_remote.csv")
FOR_MEMBER_3 = Path("docs/source_register/for_member_3.csv")
MASTER = Path("docs/source_register/source_register.csv")

FIELDNAMES = ["source_id", "source_title", "source_type", "year", "data_domain",
              "url", "retrieval_date", "responsible_member", "extraction_method",
              "status", "notes"]


def main() -> None:
    with SOURCE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="|", quotechar='"')
        rows = list(reader)

    for r in rows:
        r["responsible_member"] = "Member 3"
        r["status"] = r["status"].strip().lower()

    with FOR_MEMBER_3.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter="|")
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} normalized rows to {FOR_MEMBER_3}")

    by_id = {r["source_id"]: r for r in rows}
    with MASTER.open("r", encoding="utf-8", newline="") as f:
        master_rows = list(csv.DictReader(f, delimiter="|"))
        master_fieldnames = list(master_rows[0].keys())

    updated = 0
    for r in master_rows:
        if r["source_id"] in by_id:
            fixed = by_id[r["source_id"]]
            r["responsible_member"] = fixed["responsible_member"]
            r["status"] = fixed["status"]
            r["notes"] = fixed["notes"]
            updated += 1

    with MASTER.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=master_fieldnames, delimiter="|")
        w.writeheader()
        w.writerows(master_rows)
    print(f"Updated {updated} matching rows in {MASTER}")

    print("\nStatus breakdown:")
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    for s, n in sorted(counts.items()):
        print(f"  {s:14s} {n}")


if __name__ == "__main__":
    main()
