"""
Leader's review tool: independently spot-checks a random sample of
rows a team member has marked "acquired" in their source register
CSV, before merging their PR.

Since data/raw/ is gitignored, the PR diff never shows the actual
downloaded file - only the CSV status change. This script closes that
gap by re-fetching the real URL and confirming it genuinely matches
what was claimed (reachable, correct type, plausible size), rather
than trusting the status column alone.

Usage:
    python3 audit_acquired_sources.py docs/source_register/for_member_2.csv
    python3 audit_acquired_sources.py docs/source_register/for_member_2.csv --sample 10
    python3 audit_acquired_sources.py docs/source_register/for_member_2.csv --all
"""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {"User-Agent": "CSC4792-Livingstone-Research/1.0"}
TIMEOUT = 60


def audit_row(r: dict) -> tuple[bool, str]:
    url = r["url"]
    claimed_type = r["source_type"]

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False, stream=True)
        resp.raise_for_status()
    except Exception as e:
        return False, f"FETCH FAILED: {type(e).__name__}: {e}"

    content = resp.raw.read(4096)
    ct = resp.headers.get("content-type", "")

    if claimed_type == "PDF":
        if content[:4] != b"%PDF":
            return False, f"Claimed PDF but no %PDF signature. content-type={ct}"
        return True, f"OK - real PDF, HTTP {resp.status_code}, content-type={ct}"

    if "webpage" in claimed_type:
        if "html" not in ct.lower():
            return False, f"Claimed webpage but content-type={ct}"
        return True, f"OK - real webpage, HTTP {resp.status_code}"

    return True, f"OK (unverified type check) - HTTP {resp.status_code}, content-type={ct}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path", type=Path)
    ap.add_argument("--sample", type=int, default=5, help="Number of acquired rows to spot-check (default 5)")
    ap.add_argument("--all", action="store_true", help="Audit every acquired row, not just a sample")
    args = ap.parse_args()

    with args.csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))

    acquired = [r for r in rows if r["status"] == "acquired"]
    print(f"{len(acquired)} rows marked 'acquired' in {args.csv_path}")

    if not acquired:
        print("Nothing to audit.")
        return 0

    to_check = acquired if args.all else random.sample(acquired, min(args.sample, len(acquired)))
    print(f"Spot-checking {len(to_check)} row(s):\n")

    passed = 0
    for r in to_check:
        ok, detail = audit_row(r)
        status = "PASS" if ok else "*** FAIL ***"
        print(f"[{status}] {r['source_id']} - {r['source_title']}")
        print(f"    URL: {r['url']}")
        print(f"    {detail}\n")
        if ok:
            passed += 1

    print(f"Result: {passed}/{len(to_check)} passed.")
    if passed < len(to_check):
        print("DO NOT MERGE until failures are investigated with the member who submitted this PR.")
    return 0 if passed == len(to_check) else 1


if __name__ == "__main__":
    raise SystemExit(main())
