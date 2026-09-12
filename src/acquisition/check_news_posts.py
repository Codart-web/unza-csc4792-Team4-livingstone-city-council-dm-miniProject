"""
Fetch the 9 unlabeled news-post URLs assigned to the Leader in
for_leader.csv and print their visible text, so they can be reviewed
in one pass instead of opening each in a browser.

Read-only. Uses verify=False per docs/decisions/decision_log.md
(2026-09-10 TLS decision), scoped only to this diagnostic script.
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

REGISTER = Path("docs/source_register/for_leader.csv")


def main() -> int:
    with REGISTER.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))

    news_urls = [r["url"] for r in rows if "?p=" in r["url"]]
    print(f"Found {len(news_urls)} news-post URLs to check.\n")

    for i, url in enumerate(news_urls, 1):
        print(f"===== [{i}/{len(news_urls)}] {url} =====")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        except Exception as e:
            print(f"  FETCH FAILED: {type(e).__name__}: {e}\n")
            time.sleep(DELAY_SECONDS)
            continue

        print(f"  HTTP {resp.status_code}, {len(resp.content)} bytes")

        soup = BeautifulSoup(resp.text, "lxml")

        title = soup.find(["h1", "h2"], class_=lambda c: c and "title" in c.lower()) \
            or soup.find("title")
        print(f"  Title: {title.get_text(strip=True) if title else '(none found)'}")

        content = soup.find(class_=lambda c: c and ("entry-content" in c or "post-content" in c))
        if not content:
            content = soup

        paragraphs = [p.get_text(" ", strip=True) for p in content.find_all("p")]
        paragraphs = [p for p in paragraphs if p]
        preview = " ".join(paragraphs)[:500]
        print(f"  Preview: {preview if preview else '(no paragraph text found)'}")
        print()

        time.sleep(DELAY_SECONDS)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
