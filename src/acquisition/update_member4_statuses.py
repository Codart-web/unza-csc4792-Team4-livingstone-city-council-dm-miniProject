"""
Apply the manual verification verdict to for_member_4.csv (performed
by the Leader on Member 4's behalf).
"""
from __future__ import annotations

import csv
from pathlib import Path

REGISTER = Path("docs/source_register/for_member_4.csv")
MASTER = Path("docs/source_register/source_register.csv")

INACCESSIBLE_IDS = {"SRC-PLAN-007", "SRC-PLAN-008"}
INACCESSIBLE_NOTE = "Verified 2026-09-12 (Leader, on Member 4's behalf): real HTTP 404, page does not resolve. Consistent with same failure pattern seen across CDF/Finance/Governance category-index pages - site-wide issue, not domain-specific."

ZDSP_ID = "SRC-PLAN-006"
ZDSP_NOTE = "Verified 2026-09-12 (Leader, on Member 4's behalf): loads correctly, but is an external-links directory page (Ministry links, partner orgs). Internal links all already captured elsewhere in the register (Citizens Engagement Strategy, Debt-Arrears doc, National Decentralisation Policy). No new sources found. Kept as verified reference, not extracted as a data row."


def update_file(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))
        fieldnames = list(rows[0].keys())

    changed = False
    for r in rows:
        sid = r["source_id"]
        if sid in INACCESSIBLE_IDS:
            r["status"] = "inaccessible"
            r["notes"] = INACCESSIBLE_NOTE
            changed = True
        elif sid == ZDSP_ID:
            r["status"] = "verified"
            r["notes"] = ZDSP_NOTE
            changed = True
        elif r["data_domain"] == "planning" and r["status"] == "discovered":
            r["status"] = "verified"
            changed = True

    if changed:
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
            w.writeheader()
            w.writerows(rows)
    return changed


def main() -> int:
    for path in (REGISTER, MASTER):
        result = update_file(path)
        print(f"{path}: {'updated' if result else 'no change / not found'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
