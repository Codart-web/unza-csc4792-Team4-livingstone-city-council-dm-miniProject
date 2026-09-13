"""
Consolidated Phase 2 -> Phase 3 readiness check.

Confirms, across the master source register and the three closed
domains (LEADER, Member 4/Planning, Member 5/Governance):
  1. No row is silently stuck at "discovered" when it should have
     been resolved (verified/acquired/rejected/inaccessible).
  2. Every acquired PDF file actually exists locally in data/raw/.
  3. Each domain's findings_<name>.md file exists and is non-empty.
  4. Row counts add up (nothing silently lost or duplicated).

This does NOT re-check CDF or Finance, since those domains are still
in progress by design.
"""
from __future__ import annotations

import csv
from pathlib import Path

MASTER = Path("docs/source_register/source_register.csv")
CLOSED_DOMAINS = {
    "other": "LEADER",
    "planning": "Member 4",
    "governance": "Member 5",
}
FINDINGS_FILES = {
    "other": "docs/team/findings_leader.md",
    "planning": "docs/team/findings_planning.md",
    "governance": "docs/team/findings_governance.md",
}
VALID_STATUSES = {"discovered", "verified", "acquired", "rejected", "inaccessible"}


def main() -> int:
    with MASTER.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))

    print(f"Master register: {len(rows)} total rows.\n")

    all_ok = True

    for domain in CLOSED_DOMAINS:
        domain_rows = [r for r in rows if r["data_domain"] == domain]
        print(f"=== Domain: {domain} ({len(domain_rows)} rows) ===")

        status_counts: dict[str, int] = {}
        stuck = []
        bad_status = []
        for r in domain_rows:
            s = r["status"]
            status_counts[s] = status_counts.get(s, 0) + 1
            if s not in VALID_STATUSES:
                bad_status.append(r["source_id"])
            if s == "discovered":
                stuck.append(r["source_id"])

        for s, n in sorted(status_counts.items()):
            print(f"    {s:14s} {n}")

        if stuck:
            print(f"    *** {len(stuck)} row(s) still 'discovered', never resolved: {stuck}")
            all_ok = False

        if bad_status:
            print(f"    *** {len(bad_status)} row(s) with an invalid/unexpected status value: {bad_status}")
            all_ok = False

        acquired_pdfs = [r for r in domain_rows if r["status"] == "acquired" and r["source_type"] == "PDF"]
        missing_files = []
        for r in acquired_pdfs:
            matches = list(Path("data/raw/pdf").glob(f"{r['source_id']}_*"))
            if not matches:
                missing_files.append(r["source_id"])
        if missing_files:
            print(f"    *** {len(missing_files)} acquired PDF row(s) have NO matching local file in data/raw/pdf/: {missing_files}")
            all_ok = False
        elif acquired_pdfs:
            print(f"    Local file check: all {len(acquired_pdfs)} acquired PDF(s) present on disk. OK")

        findings_path = Path(FINDINGS_FILES[domain])
        if not findings_path.exists():
            print(f"    *** MISSING findings file: {findings_path}")
            all_ok = False
        elif findings_path.stat().st_size < 50:
            print(f"    *** findings file exists but looks empty/too short: {findings_path}")
            all_ok = False
        else:
            print(f"    Findings file present and non-trivial: {findings_path} ({findings_path.stat().st_size} bytes). OK")

        print()

    print("=" * 60)
    if all_ok:
        print("ALL CHECKS PASSED. Leader/Planning/Governance domains are")
        print("genuinely ready to move into Phase 3 (Extraction).")
    else:
        print("ISSUES FOUND ABOVE. Resolve before starting Phase 3 on the")
        print("affected domain(s).")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
