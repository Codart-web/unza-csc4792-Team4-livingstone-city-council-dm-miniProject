"""
Apply the manual verification verdict to for_member_5.csv:
- 6 category-index pages that returned real HTTP 404s -> inaccessible
- News Updates page (loaded fine, corroborates existing news finds) -> verified
- 16 PDFs + 1 .doc that returned real, valid file signatures -> verified
  (pending actual download to data/raw/)

Also flags the 3 unusually large PDFs (>4MB) as likely scanned/image
PDFs needing OCR, and the 1 .doc file as needing python-docx, not
pdfplumber, so this doesn't get discovered too late during extraction.
"""
from __future__ import annotations

import csv
from pathlib import Path

REGISTER = Path("docs/source_register/for_member_5.csv")
MASTER = Path("docs/source_register/source_register.csv")

INACCESSIBLE_IDS = {
    "SRC-GOVE-023",
    "SRC-GOVE-024",
    "SRC-GOVE-021",
    "SRC-GOVE-019",
    "SRC-GOVE-020",
    "SRC-GOVE-022",
}
INACCESSIBLE_NOTE = "Verified 2026-09-11: real HTTP 404, page does not resolve. Likely a stale anchor/route from the site's page builder. Kept in register as documented gap, not deleted."

NEWS_INDEX_ID = "SRC-GOVE-018"
NEWS_INDEX_NOTE = "Verified 2026-09-11: loads correctly, is the site's news index. Confirms completeness of news posts already found and processed under LEADER (SRC-OTHE/SRC-CDF-038-040). No new content to extract from this page itself."

LARGE_PDF_IDS = {"SRC-GOVE-015", "SRC-GOVE-011", "SRC-GOVE-016"}
LARGE_PDF_NOTE_SUFFIX = " FLAG: unusually large file size for its apparent content - likely a scanned/image PDF. Verify with pdfplumber/pypdf whether text extraction actually works before assuming it does; may need OCR (pytesseract) instead."

DOC_ID = "SRC-GOVE-009"
DOC_NOTE = "Verified 2026-09-11: real .doc file (old Word format), NOT a PDF. Requires python-docx for extraction, not pdfplumber/pypdf. Confirm python-docx is in requirements before extraction phase."


def update_file(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="|"))
        fieldnames = list(rows[0].keys())

    changed = False
    for r in rows:
        sid = r["source_id"]
        if sid in INACCESSIBLE_IDS:
            r["status"] = "inaccessible"
            r["notes"] = INACCESSIBLE_NOTE
            changed = True
        elif sid == NEWS_INDEX_ID:
            r["status"] = "verified"
            r["notes"] = NEWS_INDEX_NOTE
            changed = True
        elif sid == DOC_ID:
            r["status"] = "verified"
            r["notes"] = DOC_NOTE
            changed = True
        elif sid in LARGE_PDF_IDS:
            r["status"] = "verified"
            r["notes"] = (r["notes"] or "") + LARGE_PDF_NOTE_SUFFIX
            changed = True
        elif r["data_domain"] == "governance" and r["status"] == "discovered":
            r["status"] = "verified"
            changed = True

    if changed:
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
            w.writeheader()
            w.writerows(rows)
    return changed


def main() -> int:
    for path in (REGISTER, MASTER):
        result = update_file(path)
        print(f"{path}: {'updated' if result else 'no change / not found'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
