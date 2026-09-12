"""
Download local evidence copies of the 6 Leader-owned sources that were
kept (not rejected) after verification: 3 contextual governance
narratives + 3 reclassified CDF news reports. Saves raw HTML into
data/raw/web/ and flips status from "verified" to "acquired".

Read-only fetch, no modification of source content. Uses verify=False
per docs/decisions/decision_log.md (2026-09-10 TLS decision).
"""
from __future__ import annotations

import csv
import re
import time
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {"User-Agent": "CSC4792-Livingstone-Research/1.0"}
TIMEOUT = 30
DELAY_SECONDS = 0.5

MASTER = Path("docs/source_register/source_register.csv")
LEADER_FILE = Path("docs/source_register/for_leader.csv")
OUT_DIR = Path("data/raw/web")

KEEP_IDS = {"SRC-CDF-038", "SRC-CDF-039", "SRC-CDF-040"}
CONTEXTUAL_URLS = {
    "https://www.livingstonecouncil.gov.zm/?p=4841",
    "https://www.livingstonecouncil.gov.zm/?p=4843",
    "https://www.livingstonecouncil.gov.zm/?p=5004",
}


def slugify(url: str, source_id: str) -> str:
    m = re.search(r"[?&]p=(\d+)", url)
    post_id = m.group(1) if m else "unknown"
    return f"{source_id}_news_post_{post_id}.html"


def acquire(url: str, source_id: str):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        resp.raise_for_status()
    except Exception as e:
        print(f"  FAILED to acquire {url}: {type(e).__name__}: {e}")
        return None

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / slugify(url, source_id)
    out_path.write_bytes(resp.content)
    print(f"  Saved {len(resp.content)} bytes -> {out_path}")
    return out_path


def main() -> int:
    with MASTER.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))

    to_acquire = []
    for r in rows:
        if r["source_id"] in KEEP_IDS or r["url"] in CONTEXTUAL_URLS:
            to_acquire.append(r)

    print(f"Acquiring {len(to_acquire)} kept sources.\n")

    acquired_ids = set()
    for r in to_acquire:
        print(f"{r['source_id']} - {r['source_title']}")
        path = acquire(r["url"], r["source_id"])
        if path is not None:
            acquired_ids.add(r["source_id"])
        time.sleep(DELAY_SECONDS)
        print()

    def update_status(path: Path) -> None:
        if not path.exists():
            return
        with path.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f, delimiter="|"))
            fieldnames = list(rows[0].keys())
        changed = False
        for r in rows:
            if r["source_id"] in acquired_ids and r["status"] == "verified":
                r["status"] = "acquired"
                changed = True
        if changed:
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
                w.writeheader()
                w.writerows(rows)
            print(f"Updated statuses in {path}")

    update_status(MASTER)
    update_status(LEADER_FILE)
    update_status(Path("docs/source_register/for_member_2.csv"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
