"""
Sync the master source_register.csv FROM all per-member/leader files.

During Phase 2 acquisition, per-member files (for_member_2.csv,
for_member_3.csv, etc.) are updated directly by each member's
acquisition script - but those scripts never touch the master. This
creates drift: the master silently falls behind reality.

Run this after ANY per-member acquisition/verification script, before
committing, to keep the master authoritative again.
"""
from __future__ import annotations

import csv
from pathlib import Path

REG_DIR = Path("docs/source_register")
MASTER = REG_DIR / "source_register.csv"

MEMBER_FILES = [
    "for_member_2.csv", "for_member_3.csv", "for_member_4.csv",
    "for_member_5.csv", "for_leader.csv",
]


def main() -> None:
    with MASTER.open("r", encoding="utf-8", newline="") as f:
        master_rows = list(csv.DictReader(f, delimiter="|"))
        fieldnames = list(master_rows[0].keys())

    by_id = {r["source_id"]: r for r in master_rows}
    total_updated = 0

    for fname in MEMBER_FILES:
        path = REG_DIR / fname
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8", newline="") as f:
            member_rows = list(csv.DictReader(f, delimiter="|"))

        file_updated = 0
        for r in member_rows:
            sid = r["source_id"]
            if sid in by_id:
                master_r = by_id[sid]
                if master_r["status"] != r["status"] or master_r["notes"] != r["notes"]:
                    master_r["status"] = r["status"]
                    master_r["notes"] = r["notes"]
                    file_updated += 1
        if file_updated:
            print(f"{fname}: synced {file_updated} changed row(s) into master")
        total_updated += file_updated

    with MASTER.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        w.writeheader()
        w.writerows(master_rows)

    print(f"\nTotal rows synced into master: {total_updated}")

    print("\nMaster status breakdown:")
    counts = {}
    for r in master_rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    for s, n in sorted(counts.items()):
        print(f"  {s:14s} {n}")


if __name__ == "__main__":
    main()
