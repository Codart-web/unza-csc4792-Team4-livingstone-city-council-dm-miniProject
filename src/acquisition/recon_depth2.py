"""
Second-pass reconnaissance: fetch every HTML page linked from the
homepage and extract its sub-links. Same-domain only. Deduplicates
across all fetches. Skips non-HTML targets (PDFs, PPTX, etc).

Read-only. Polite rate limit. verify=False per decision_log.md
2026-09-10.
"""

from __future__ import annotations

import csv
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://www.livingstonecouncil.gov.zm"
HEADERS = {"User-Agent": "CSC4792-Livingstone-Research/1.0"}
TIMEOUT = 30
DELAY_SECONDS = 0.5
SKIP_EXT = {".pdf", ".pptx", ".docx", ".xlsx", ".zip",
            ".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp4"}


def is_probably_html(url: str) -> bool:
    path = urlparse(url).path.lower()
    for ext in SKIP_EXT:
        if path.endswith(ext):
            return False
    return True


def extract_links(html: str, base_host: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = urljoin(BASE, href)
        parsed = urlparse(full)
        if parsed.netloc and parsed.netloc != base_host:
            continue
        text = " ".join(a.get_text(" ", strip=True).split())[:120]
        out.append({"url": full, "anchor_text": text, "path": parsed.path})
    return out


def main() -> int:
    recon_file = Path("docs/source_register") / f"recon_{date.today().isoformat()}.csv"
    if not recon_file.exists():
        print(f"missing {recon_file}; run recon_site.py first")
        return 2

    base_host = urlparse(BASE).netloc

    seeds: list[str] = []
    with recon_file.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="|")
        for row in r:
            url = row["url"]
            if is_probably_html(url):
                seeds.append(url)

    print(f"Seeds to fetch: {len(seeds)}")
    print()

    seen: dict[str, dict] = {}

    for i, seed in enumerate(seeds, 1):
        try:
            resp = requests.get(seed, headers=HEADERS, timeout=TIMEOUT, verify=False)
        except Exception as e:
            print(f"[{i:>2}/{len(seeds)}] FAILED {type(e).__name__}: {seed}")
            time.sleep(DELAY_SECONDS)
            continue

        ct = resp.headers.get("content-type", "")
        if "html" not in ct:
            print(f"[{i:>2}/{len(seeds)}] skip {ct[:40]:<40} {seed}")
            time.sleep(DELAY_SECONDS)
            continue

        print(f"[{i:>2}/{len(seeds)}] {resp.status_code} {len(resp.content):>7} B {seed}")

        for link in extract_links(resp.text, base_host):
            key = link["url"]
            if key not in seen:
                seen[key] = link

        time.sleep(DELAY_SECONDS)

    out_file = Path("docs/source_register") / f"recon_depth2_{date.today().isoformat()}.csv"
    with out_file.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["url", "anchor_text", "path"],
            delimiter="|",
        )
        w.writeheader()
        w.writerows(sorted(seen.values(), key=lambda r: r["url"]))

    print()
    print(f"Wrote {len(seen)} unique links to {out_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
