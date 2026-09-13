"""
Download the 5 verified Member 4 (Planning/Infrastructure) sources
into data/raw/pdf/. Performed by the Leader on Member 4's behalf.
"""
from __future__ import annotations

import csv
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {"User-Agent": "CSC4792-Livingstone-Research/1.0"}
TIMEOUT = 180  # the IDP file is 32MB, needs generous headroom
DELAY_SECONDS = 0.5

REGISTER = Path("docs/source_register/for_member_4.csv")
MASTER = Path("docs/source_register/source_register.csv")
OUT_DIR = Path("data/raw/pdf")


def target_path(url: str, source_id: str) -> Path:
    path = urlparse(url).path
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(path).name)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR / f"{source_id}_{safe_name}"


def download(url, source_id):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False, stream=True)
        resp.raise_for_status()
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")
        return None

    out_path = target_path(url, source_id)
    with out_path.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=1 << 16):
            f.write(chunk)

    size = out_path.stat().st_size
    print(f"  Saved {size:,} bytes -> {out_path}")
    return out_path


def main() -> int:
    with REGISTER.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))

    to_get = [r for r in rows if r["status"] == "verified" and r["source_type"] == "PDF"]
    print(f"Downloading {len(to_get)} verified planning PDFs.\n")

    acquired_ids = set()
    for r in to_get:
        print(f"{r['source_id']} - {r['source_title']}")
        path = download(r["url"], r["source_id"])
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

    update_status(REGISTER)
    update_status(MASTER)

    print(f"\n{len(acquired_ids)}/{len(to_get)} downloaded successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
