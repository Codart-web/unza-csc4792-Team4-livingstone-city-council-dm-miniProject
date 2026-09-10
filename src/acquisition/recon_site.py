"""
Read-only reconnaissance of the Livingstone City Council website.

Fetches the homepage only. Extracts same-domain links. Categorises
them by likely data domain using keyword heuristics. Writes a pipe-
delimited CSV for human review. Does NOT download any sub-page
content. Does NOT follow sub-links.
"""

from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup

BASE_URL = "https://www.livingstonecouncil.gov.zm"
USER_AGENT = (
    "CSC4792-Livingstone-Research/1.0 "
    "(https://github.com/Codart-web/unza-csc4792-Team4-livingstone-city-council-dm-miniProject)"
)
TIMEOUT = 30
# The council site serves a misconfigured TLS chain. See
# docs/decisions/decision_log.md (2026-09-10). Verification is
# disabled for read-only reconnaissance only.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CATEGORY_KEYWORDS = {
    "cdf": ["cdf", "constituency", "bursary", "bursaries", "grant", "loan", "empowerment"],
    "finance": ["budget", "revenue", "finance", "financial", "lgef",
                "equalisation", "equalization", "audit", "expenditure", "tender"],
    "planning": ["idp", "integrated-development", "infrastructure", "road",
                 "water", "sanitation", "health", "school", "drainage", "project"],
    "governance": ["minutes", "council-meeting", "wdc", "ward", "consultation",
                   "newsletter", "publication", "news", "report", "resolution"],
}


def categorise(url: str, text: str) -> str:
    haystack = (url + " " + text).lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in haystack:
                return cat
    return "other"


def main() -> int:
    print(f"Fetching {BASE_URL} ...")
    try:
        r = requests.get(
        BASE_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
        verify=False,  # see decision_log.md 2026-09-10
    )
    except Exception as e:
        print(f"FETCH FAILED: {type(e).__name__}: {e}")
        return 2
    print(f"HTTP {r.status_code}, {len(r.content)} bytes")
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    base_host = urlparse(BASE_URL).netloc

    rows = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = urljoin(BASE_URL, href)
        parsed = urlparse(full)
        if parsed.netloc and parsed.netloc != base_host:
            continue
        key = (parsed.scheme, parsed.netloc, parsed.path, parsed.query)
        if key in seen:
            continue
        seen.add(key)
        text = " ".join(a.get_text(" ", strip=True).split())[:120]
        rows.append({
            "url": full,
            "anchor_text": text,
            "likely_domain": categorise(full, text),
            "path": parsed.path,
        })

    out_dir = Path("docs/source_register")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"recon_{date.today().isoformat()}.csv"

    with out_file.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["url", "anchor_text", "likely_domain", "path"],
            delimiter="|",
        )
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["likely_domain"], r["url"])))

    print(f"\nWrote {len(rows)} same-domain links to {out_file}")
    print("\nBreakdown by likely domain:")
    counts = {}
    for row in rows:
        counts[row["likely_domain"]] = counts.get(row["likely_domain"], 0) + 1
    for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:12s} {n}")

    print("\nSample links per domain (up to 6 each):")
    for cat in sorted(set(r["likely_domain"] for r in rows)):
        print(f"\n[{cat}]")
        shown = 0
        for row in rows:
            if row["likely_domain"] == cat and shown < 6:
                print(f"  {row['url']}")
                shown += 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
