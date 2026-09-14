"""Acquire registered Livingstone finance sources without extracting values."""

from __future__ import annotations

import argparse
import csv
import shutil
import time
import warnings
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
import urllib3

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = REPO_ROOT / "docs" / "source_register" / "for_member_3.csv"
DEFAULT_DATA_RAW = REPO_ROOT / "data" / "raw"
USER_AGENT = "CSC4792-Livingstone-Research/1.0 (university mini-project)"
TIMEOUT = 60
FIELDS = ["source_id", "source_title", "source_type", "year", "data_domain", "url", "retrieval_date", "responsible_member", "extraction_method", "status", "notes"]


def slugify(text: str) -> str:
    value = "".join(char if char.isalnum() else "-" for char in text.lower())
    while "--" in value:
        value = value.replace("--", "-")
    return value.strip("-")[:60] or "untitled"


def content_folder(source_type: str, url: str, content_type: str) -> str:
    extension = Path(urlparse(url).path).suffix.lower()
    if extension == ".pdf" or "pdf" in content_type:
        return "pdf"
    if extension in {".csv", ".xls", ".xlsx"} or "spreadsheet" in content_type:
        return "csv"
    if "webpage" in source_type.lower() or "html" in content_type or not extension:
        return "web"
    return "other"


def fetch(url: str) -> tuple[bool, int | None, str, bytes, str | None]:
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT, verify=True)
    except requests.exceptions.SSLError:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)
            try:
                response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT, verify=False)
            except requests.RequestException as exc:
                return False, None, "", b"", str(exc)
    except requests.RequestException as exc:
        return False, None, "", b"", str(exc)
    content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
    if response.status_code != 200:
        return False, response.status_code, content_type, b"", f"HTTP {response.status_code}"
    return True, response.status_code, content_type, response.content, None


def append_note(existing: str, addition: str) -> str:
    existing = (existing or "").strip()
    return f"{existing}; {addition}" if existing else addition


def acquire(rows: list[dict], args: argparse.Namespace) -> dict[str, int]:
    counts = {"attempted": 0, "acquired": 0, "inaccessible": 0, "skipped": 0}
    for row in rows:
        if (row.get("status") or "").strip().lower() != args.status.lower():
            counts["skipped"] += 1
            continue
        if args.limit is not None and counts["attempted"] >= args.limit:
            break
        counts["attempted"] += 1
        source_id = row["source_id"].strip()
        url = row["url"].strip()
        if not url:
            row["status"] = "inaccessible"
            row["notes"] = append_note(row.get("notes", ""), "Inaccessible: no URL.")
            counts["inaccessible"] += 1
            continue
        existing = next((path for folder in ("pdf", "web", "csv", "other") for path in (args.data_dir / folder).glob(f"{source_id}_*")), None)
        if existing is not None and not args.force:
            row["notes"] = append_note(row.get("notes", ""), "Acquired locally; review content before verification.")
            counts["skipped"] += 1
            continue
        if args.dry_run:
            print(f"[dry-run] {source_id}: {url}")
            continue
        ok, status_code, content_type, content, error = fetch(url)
        if not ok:
            row["status"] = "inaccessible"
            row["notes"] = append_note(row.get("notes", ""), f"Inaccessible: {error}.")
            counts["inaccessible"] += 1
        else:
            folder = content_folder(row.get("source_type", ""), url, content_type)
            extension = Path(urlparse(url).path).suffix.lower() or (".html" if folder == "web" else ".bin")
            output = args.data_dir / folder / f"{source_id}_{slugify(row.get('source_title', ''))}{extension}"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
            row["status"] = "acquired"
            row["notes"] = append_note(row.get("notes", ""), f"Acquired: HTTP {status_code}, {content_type or 'unknown type'}, {len(content)} bytes; review usefulness manually.")
            counts["acquired"] += 1
        time.sleep(args.delay)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_RAW)
    parser.add_argument("--status", default="discovered")
    parser.add_argument("--delay", type=float, default=1.5)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.csv.is_absolute():
        args.csv = REPO_ROOT / args.csv
    if not args.data_dir.is_absolute():
        args.data_dir = REPO_ROOT / args.data_dir
    if not args.csv.exists():
        parser.error(f"CSV not found: {args.csv}")
    with args.csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        rows = list(reader)
        fieldnames = reader.fieldnames or FIELDS
    counts = acquire(rows, args)
    print(counts)
    if not args.dry_run and (counts["acquired"] or counts["inaccessible"]):
        backup = args.csv.with_suffix(f".bak-{datetime.now().strftime('%Y%m%dT%H%M%S')}.csv")
        shutil.copy2(args.csv, backup)
        with args.csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="|")
            writer.writeheader()
            writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
