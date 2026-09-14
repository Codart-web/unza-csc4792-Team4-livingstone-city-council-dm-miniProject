"""
Phase 3 reconnaissance: full page-by-page dump of the Climate Change
and Resilience Strategy (SRC-PLAN-005). Writes directly to a UTF-8
file, bypassing the console entirely, to avoid Windows code-page
mojibake corruption.
"""
from __future__ import annotations

import pdfplumber
from pathlib import Path

PATH = Path("data/raw/pdf/SRC-PLAN-005_Livingstone-City-Climate-Change-and-Resilience-Strategy.pdf")
OUT = Path("climate_dump.txt")


def main() -> None:
    with open(OUT, "w", encoding="utf-8") as out, pdfplumber.open(PATH) as pdf:
        out.write(f"Total pages: {len(pdf.pages)}\n\n")
        for i, page in enumerate(pdf.pages, 1):
            text = (page.extract_text() or "").strip()
            tables = page.extract_tables()
            out.write(f"===== Page {i} - {len(tables)} table(s) detected =====\n")
            out.write((text[:2000] if text else "(no extractable text)") + "\n")
            if tables:
                out.write(f"\n--- Tables on page {i} ---\n")
                for t_idx, table in enumerate(tables):
                    out.write(f"  Table {t_idx+1}:\n")
                    for row in table[:8]:
                        out.write("    | " + " | ".join((c or "")[:40] for c in row) + "\n")
            out.write("\n")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
