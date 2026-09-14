"""
Full multi-page text dump of both LCC newsletters, writing directly
to a UTF-8 file to avoid Windows console encoding crashes on special
characters sometimes found in scanned/exported PDF text.
"""
import pdfplumber
from pathlib import Path

FILES = [
    "data/raw/pdf/SRC-GOVE-016_LCC-March-news-2026.pdf",
    "data/raw/pdf/SRC-GOVE-017_LCC-June-news-2026.pdf",
]

with open("newsletter_dump.txt", "w", encoding="utf-8") as out:
    for path_str in FILES:
        path = Path(path_str)
        out.write(f"\n{'='*70}\n{path.name}\n{'='*70}\n")
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                text = (page.extract_text() or "").strip()
                out.write(f"\n--- Page {i} ---\n")
                out.write(text if text else "(no extractable text on this page)")
                out.write("\n")

print("Done - written to newsletter_dump.txt")
