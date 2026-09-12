"""
Verify all 8 sources assigned to Member 4 (Planning/Infrastructure) in
for_member_4.csv. Performed by the Leader on Member 4's behalf (prior
commitments prevented Member 4 from doing this personally) - see
decision log entry recording this.

Confirms PDFs are real, and for the 2 category-index pages + 1 site
page, extracts a preview and the full list of links found on the
page, since Planning is the thinnest domain (8 rows) and these index
pages may list more documents than the two-level crawl surfaced.

Read-only. Uses verify=False per docs/decisions/decision_log.md
(2026-09-10 TLS decision).
"""
from __future__ import annotations

import csv
import time
from pathlib import Path

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {"User-Agent": "CSC4792-Livingstone-Research/1.0"}
TIMEOUT = 30
DELAY_SECONDS = 0.5

REGISTER = Path("docs/source_register/for_member_4.csv")


def preview_html(content: bytes) -> str:
    soup = BeautifulSoup(content, "lxml")
    title = soup.find(["h1", "h2", "title"])
    title_text = title.get_text(strip=True) if title else "(no title found)"
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all(["p", "li"])]
    paragraphs = [p for p in paragraphs if p]
    body_preview = " ".join(paragraphs)[:400]
    links = sorted({a.get_text(strip=True) for a in soup.find_all("a") if a.get_text(strip=True)})
    return f"Title: {title_text}\n    Preview: {body_preview or '(no paragraph text)'}\n    ALL links on page ({len(links)}): {links}"


def main() -> int:
    with REGISTER.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))

    print(f"Verifying {len(rows)} Member 4 (Planning/Infrastructure) sources.\n")

    for i, r in enumerate(rows, 1):
        url = r["url"]
        title = r["source_title"]
        print(f"===== [{i}/{len(rows)}] {r['source_id']} - {title} =====")
        print(f"  URL: {url}")

        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False, allow_redirects=True)
        except Exception as e:
            print(f"  FETCH FAILED: {type(e).__name__}: {e}\n")
            time.sleep(DELAY_SECONDS)
            continue

        ct = resp.headers.get("content-type", "")
        print(f"  HTTP {resp.status_code}, content-type: {ct}, {len(resp.content)} bytes")

        if resp.status_code >= 400:
            print("  *** BROKEN LINK - mark as inaccessible ***\n")
        elif "pdf" in ct.lower() or url.lower().endswith(".pdf"):
            is_real_pdf = resp.content[:4] == b"%PDF"
            print(f"  Real PDF signature present: {is_real_pdf}")
            if not is_real_pdf:
                print("  *** DOES NOT LOOK LIKE A REAL PDF - investigate ***")
        elif "html" in ct.lower():
            print(f"  {preview_html(resp.content)}")
        else:
            print("  (non-HTML, non-PDF content-type - inspect manually)")

        print()
        time.sleep(DELAY_SECONDS)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
