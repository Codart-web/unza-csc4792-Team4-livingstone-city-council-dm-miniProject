"""
Download the 18 verified Member 5 (Governance) sources into data/raw/,
since Member 5's native Windows machine cannot reach the council site
directly (diagnosed 2026-09-11: TCP connect blocked at network level,
confirmed not Python/Windows-config specific - curl.exe fails
identically, another unrelated Zambian gov site also fails the same
way from that network).

Run on WSL as a network proxy only. Flips status "verified" ->
"acquired" for every row that downloads successfully. Does NOT commit
data/raw/ contents (gitignored per project policy) - only the CSV
status changes are meant to be committed.
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
TIMEOUT = 60
DELAY_SECONDS = 0.5

REGISTER = Path("docs/source_register/for_member_5.csv")
MASTER = Path("docs/source_register/source_register.csv")

EXT_DIR = {
    ".pdf": Path("data/raw/pdf"),
    ".doc": Path("data/raw/other"),
    ".docx": Path("data/raw/other"),
}


def target_path(url: str, source_id: str) -> Path:
    path = urlparse(url).path
    ext = Path(path).suffix.lower() or ".bin"
    out_dir = EXT_DIR.get(ext, Path("data/raw/other"))
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(path).name)
    return out_dir / f"{source_id}_{safe_name}"


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

    to_get = [r for r in rows if r["status"] == "verified"]
    print(f"Downloading {len(to_get)} verified governance sources.\n")

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
