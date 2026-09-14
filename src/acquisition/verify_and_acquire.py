"""
Row-by-row source acquisition script for a CSC4792 Livingstone source register.

WHAT THIS SCRIPT DOES (mechanical steps only)
----------------------------------------------
1. Reads a pipe-delimited source-register CSV (default:
   docs/source_register/for_member_2.csv).
2. For each row whose status is "discovered" (case-insensitive, configurable
   with --status):
     - fetches the URL,
     - saves the raw bytes under data/raw/<pdf|web|csv|other>/,
     - updates that row's status to "acquired" (success) or "inaccessible"
       (failure),
     - appends a note documenting what happened (HTTP status, content-type,
       byte size, saved path, UTC timestamp) -- it never erases an existing
       note, only appends to it.
3. Writes the CSV back out, after saving a timestamped backup of the
   original next to it.

WHAT THIS SCRIPT DELIBERATELY DOES NOT DO
------------------------------------------
- It never marks a row "verified". Per docs/source_register/source_register_guide.md
  and docs/quality/source_quality_checklist.md, "verified" means a human has
  confirmed the fetched content actually matches the title/domain claimed for
  that row -- an HTTP 200 cannot prove that. Skim each downloaded file
  yourself and change "acquired" -> "verified" (or -> "rejected" with a
  reason) once you've looked at it.
- It never invents, estimates, or fills in a data value. If a fetch fails,
  the row is marked "inaccessible" with the error recorded -- nothing is
  guessed.
- It never touches rows that are already "verified" / "rejected" /
  "inaccessible" / "acquired" unless you explicitly pass --status to target
  them.

USAGE
-----
    # from the repo root, inside your project venv
    python -m src.acquisition.verify_and_acquire

    # see what it *would* do, without downloading or writing anything
    python -m src.acquisition.verify_and_acquire --dry-run

    # only try the first 5 matching rows (useful for a quick test)
    python -m src.acquisition.verify_and_acquire --limit 5

    # target a different member's file
    python -m src.acquisition.verify_and_acquire --csv docs/source_register/for_member_3.csv

    # re-fetch rows even if a local file with that source_id already exists
    python -m src.acquisition.verify_and_acquire --force
"""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
import time
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
import urllib3

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = REPO_ROOT / "docs" / "source_register" / "for_member_2.csv"
DEFAULT_DATA_RAW = REPO_ROOT / "data" / "raw"

FIELDNAMES = [
    "source_id",
    "source_title",
    "source_type",
    "year",
    "data_domain",
    "url",
    "retrieval_date",
    "responsible_member",
    "extraction_method",
    "status",
    "notes",
]

USER_AGENT = (
    "Mozilla/5.0 CSC4792-Livingstone-Research/1.0 "
    "(university mini-project; contact: mwalesamson300@gmail.com)"
)
TIMEOUT = 60
DEFAULT_DELAY_SECONDS = 1.5  # be polite to the council server


def slugify(text: str, max_len: int = 60) -> str:
    out = "".join(c if c.isalnum() else "-" for c in text.lower())
    while "--" in out:
        out = out.replace("--", "-")
    out = out.strip("-")
    return out[:max_len] or "untitled"


def pick_subdir(source_type: str, url: str, content_type: str) -> str:
    ext_hint = Path(urlparse(url).path).suffix.lower()
    if ext_hint == ".pdf" or "pdf" in content_type:
        return "pdf"
    if ext_hint in (".csv", ".xlsx", ".xls") or "csv" in content_type or "spreadsheet" in content_type:
        return "csv"
    if "webpage" in source_type.lower() or "html" in content_type or ext_hint in (".html", ".htm", ""):
        return "web"
    return "other"


def pick_extension(url: str, content_type: str, subdir: str) -> str:
    ext_hint = Path(urlparse(url).path).suffix.lower()
    if ext_hint:
        return ext_hint
    if subdir == "web":
        return ".html"
    if "pdf" in content_type:
        return ".pdf"
    if "presentation" in content_type or "powerpoint" in content_type:
        return ".pptx"
    return ".bin"


@dataclass
class FetchResult:
    ok: bool
    status_code: Optional[int]
    content_type: str
    size_bytes: int
    content: bytes
    error: Optional[str]
    used_insecure_ssl: bool = False


def fetch(url: str) -> FetchResult:
    """GET a URL. Retries once without TLS verification on SSLError, since the
    council site is known (per the team's Phase-1 kickoff notes) to serve a
    certificate that browsers/requests flag as untrusted -- that is a known
    quirk of their setup, not evidence the URL is wrong."""
    used_insecure = False
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}, verify=True)
    except requests.exceptions.SSLError:
        used_insecure = True
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)
                resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}, verify=False)
        except requests.RequestException as exc:
            return FetchResult(False, None, "", 0, b"", f"SSL error, then retry without verify also failed: {exc}", True)
    except requests.RequestException as exc:
        return FetchResult(False, None, "", 0, b"", str(exc))

    content_type = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
    if resp.status_code != 200:
        return FetchResult(False, resp.status_code, content_type, len(resp.content), b"", f"HTTP {resp.status_code}", used_insecure)

    return FetchResult(True, resp.status_code, content_type, len(resp.content), resp.content, None, used_insecure)


def append_note(existing: str, addition: str) -> str:
    existing = (existing or "").strip()
    return f"{existing}; {addition}" if existing else addition


def process_rows(rows: list[dict], args) -> tuple[list[dict], dict]:
    counts = {"attempted": 0, "acquired": 0, "inaccessible": 0, "skipped_status": 0, "skipped_existing": 0}
    target_status = args.status.strip().lower()

    for i, row in enumerate(rows):
        if (row.get("status") or "").strip().lower() != target_status:
            counts["skipped_status"] += 1
            continue

        if args.limit is not None and counts["attempted"] >= args.limit:
            break
        counts["attempted"] += 1

        source_id = row["source_id"].strip()
        url = row["url"].strip()
        source_type = row.get("source_type", "")
        print(f"[{source_id}] {url}")

        if not url:
            row["status"] = "inaccessible"
            row["notes"] = append_note(row.get("notes", ""), "[auto] no URL present, cannot fetch")
            counts["inaccessible"] += 1
            continue

        # Idempotency: skip if we already have a local file for this source_id.
        existing_match = None
        if not args.force:
            for sub in ("pdf", "web", "csv", "other"):
                d = args.data_dir / sub
                if d.exists():
                    hits = list(d.glob(f"{source_id}_*"))
                    if hits:
                        existing_match = hits[0]
                        break
        if existing_match is not None:
            print(f"  -> already have {existing_match.relative_to(REPO_ROOT)}, skipping (use --force to redownload)")
            counts["skipped_existing"] += 1
            continue

        if args.dry_run:
            print("  -> [dry-run] would fetch and save")
            continue

        result = fetch(url)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

        if not result.ok:
            row["status"] = "inaccessible"
            row["notes"] = append_note(row.get("notes", ""), f"[auto {stamp}] fetch failed: {result.error}")
            print(f"  -> FAILED: {result.error}")
            counts["inaccessible"] += 1
            time.sleep(args.delay)
            continue

        subdir = pick_subdir(source_type, url, result.content_type)
        ext = pick_extension(url, result.content_type, subdir)
        filename = f"{source_id}_{slugify(row.get('source_title', ''))}{ext}"
        out_dir = args.data_dir / subdir
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / filename
        out_path.write_bytes(result.content)

        rel_path = out_path.relative_to(REPO_ROOT).as_posix()
        ssl_flag = " (TLS verify skipped: council cert not trusted)" if result.used_insecure_ssl else ""
        note = (
            f"[auto {stamp}] downloaded HTTP {result.status_code}, "
            f"{result.content_type or 'unknown content-type'}, "
            f"{result.size_bytes} bytes -> {rel_path}{ssl_flag}. "
            f"NOT yet human-verified -- confirm content matches title before "
            f"changing status to 'verified'."
        )
        row["status"] = "acquired"
        row["notes"] = append_note(row.get("notes", ""), note)
        print(f"  -> saved {rel_path} ({result.size_bytes} bytes)")
        counts["acquired"] += 1

        time.sleep(args.delay)

    return rows, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to the source-register CSV to process")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_RAW, help="Root of data/raw/")
    parser.add_argument("--status", default="discovered", help="Only process rows with this status (default: discovered)")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY_SECONDS, help="Seconds to sleep between requests")
    parser.add_argument("--limit", type=int, default=None, help="Stop after this many rows have been fetched (success or failure)")
    parser.add_argument("--force", action="store_true", help="Re-download even if a local file for that source_id already exists")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen; fetch/save/write nothing")
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"CSV not found: {args.csv}", file=sys.stderr)
        return 1

    with args.csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")
        rows = list(reader)
        fieldnames = reader.fieldnames or FIELDNAMES

    rows, counts = process_rows(rows, args)

    print("\n--- summary ---")
    for k, v in counts.items():
        print(f"{k}: {v}")

    if not args.dry_run and (counts["acquired"] or counts["inaccessible"]):
        backup = args.csv.with_suffix(f".bak-{datetime.now().strftime('%Y%m%dT%H%M%S')}.csv")
        shutil.copy2(args.csv, backup)
        print(f"backup of original CSV: {backup.name}")

        with args.csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
            writer.writeheader()
            writer.writerows(rows)
        print(f"updated: {args.csv}")
    elif args.dry_run:
        print("(dry-run: CSV not modified)")
    else:
        print("(nothing changed: CSV not modified)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
