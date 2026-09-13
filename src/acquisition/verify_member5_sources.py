"""
Verify all 24 sources assigned to Member 5 (Governance) in
for_member_5.csv: confirm each URL is reachable, confirm PDFs are
actually PDFs (not broken links or redirected error pages), and for
HTML pages (category indexes, site pages) extract a short preview so
content can be judged without opening each one manually.

Read-only. Uses verify=False per docs/decisions/decision_log.md
(2026-09-10 TLS decision), scoped to this diagnostic script.
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

REGISTER = Path("docs/source_register/for_member_5.csv")


def preview_html(content: bytes) -> str:
    soup = BeautifulSoup(content, "lxml")
    title = soup.find(["h1", "h2", "title"])
    title_text = title.get_text(strip=True) if title else "(no title found)"
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all(["p", "li"])]
    paragraphs = [p for p in paragraphs if p]
    body_preview = " ".join(paragraphs)[:400]
    links = sorted({a.get_text(strip=True) for a in soup.find_all("a") if a.get_text(strip=True)})[:15]
    return f"Title: {title_text}\n    Preview: {body_preview or '(no paragraph text)'}\n    Sample links on page: {links}"


def main() -> int:
    with REGISTER.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))

    print(f"Verifying {len(rows)} Member 5 (Governance) sources.\n")

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
