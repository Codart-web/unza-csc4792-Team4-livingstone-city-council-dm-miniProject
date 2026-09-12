"""
Quick structural peek into representative PDFs from the Planning and
Governance domains, to actually write docs/team/findings_*.md based
on real content instead of assumption. Prints first-page text and
whether pdfplumber detects any tables.

This is Step 4 of the Phase 1b instructions - "describe what's
actually inside 2-3 of your PDFs" - done here for the domains the
Leader completed on behalf of Members 4 and 5, and for the Leader's
own kept sources.
"""
from __future__ import annotations

from pathlib import Path

import pdfplumber

TARGETS = [
    ("PLANNING", "data/raw/pdf/SRC-PLAN-001_LStone-IDP-2021-2031-7.8.23.pdf"),
    ("PLANNING", "data/raw/pdf/SRC-PLAN-005_Livingstone-City-Climate-Change-and-Resilience-Strategy.pdf"),
    ("PLANNING", "data/raw/pdf/SRC-PLAN-003_The-Urban-and-Regional-Planning-Act-2015.pdf"),
    ("GOVERNANCE", "data/raw/pdf/SRC-GOVE-013_MINUTES-OF-LIVINGSTONE-BUSINESS-CONSULTATIVE-MEETING-21ST-OCTOBER-2025.pdf"),
    ("GOVERNANCE", "data/raw/pdf/SRC-GOVE-012_Livingstone-City-Council-Livingstone-City-Citizen-Engagement-.pdf"),
    ("GOVERNANCE", "data/raw/pdf/SRC-GOVE-017_LCC-June-news-2026.pdf"),
]


def peek(path_str: str) -> None:
    path = Path(path_str)
    if not path.exists():
        print(f"  MISSING: {path}")
        return
    try:
        with pdfplumber.open(path) as pdf:
            print(f"  Total pages: {len(pdf.pages)}")
            page1 = pdf.pages[0]
            text = (page1.extract_text() or "").strip()
            tables = page1.extract_tables()
            print(f"  Page 1 text length: {len(text)} chars")
            print(f"  Page 1 tables detected: {len(tables)}")
            preview = text[:500] if text else "(NO EXTRACTABLE TEXT - likely a scanned/image page)"
            print(f"  Page 1 preview: {preview}")
    except Exception as e:
        print(f"  FAILED to open/parse: {type(e).__name__}: {e}")


def main() -> None:
    for domain, path_str in TARGETS:
        print(f"\n===== [{domain}] {path_str} =====")
        peek(path_str)


if __name__ == "__main__":
    main()
