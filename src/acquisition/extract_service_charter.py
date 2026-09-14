"""
Phase 3 (Extraction) - Livingstone City Council Service Delivery
Charter (SRC-GOVE-009).

The source is a LEGACY .doc file. python-docx cannot open .doc
directly - it must first be saved/converted to .docx (open in Word
and "Save As" -> Word Document (.docx), or use
`soffice --headless --convert-to docx` if LibreOffice is available).

STRUCTURE: 6 Word tables, each covering several distinct council
services. Word merges cells across columns; python-docx repeats the
merged text in every spanned cell, so this script collapses
consecutive duplicate values per row to recover the real fields.

Each service block appears in this ORDER: service name + duration,
then one row per step (client type, step description, step standard),
then a requirements block, then a blank separator row. Requirements
comes AFTER the steps in the document, so steps are buffered per
block and requirements is backfilled onto all of them once seen.

Output: one row per (service, step) - a step-level dataset, every row
carries the source_id for provenance.
"""
from __future__ import annotations

import csv
from pathlib import Path

import docx

DOCX_PATH = Path("data/raw/other/SRC-GOVE-009_LIVINGSTONE-CITY-COUNCIL-SERVICE-CHARTER.docx")
SOURCE_ID = "SRC-GOVE-009"
OUT_PATH = Path("data/interim/council_service_standards.csv")


def collapse(cells: list[str]) -> list[str]:
    out: list[str] = []
    for c in cells:
        c = c.strip()
        if not out or out[-1] != c:
            out.append(c)
    return out


def parse_table(table, table_num: int) -> list[dict]:
    finished_rows: list[dict] = []
    block_buffer: list[dict] = []
    current_service = None
    current_duration = None

    def flush_block(requirements: str) -> None:
        nonlocal block_buffer
        for r in block_buffer:
            r["requirements"] = requirements
        finished_rows.extend(block_buffer)
        block_buffer = []

    for row in table.rows:
        raw_cells = [c.text for c in row.cells]
        collapsed = collapse(raw_cells)

        if collapsed[:1] == ["Service Type"]:
            continue

        if len(collapsed) == 1 and collapsed[0] == "":
            flush_block("")
            current_service = None
            current_duration = None
            continue

        if collapsed[0].startswith("Requirements:"):
            flush_block(collapsed[0])
            continue

        if collapsed[0].startswith("Clients:"):
            client_type = collapsed[0]
            duration = collapsed[-1] if len(collapsed) >= 2 else current_duration
            if len(collapsed) >= 4:
                step_desc = collapsed[1]
                step_standard = collapsed[2]
            elif len(collapsed) == 3:
                step_desc = collapsed[1]
                step_standard = collapsed[-1]
            else:
                step_desc = ""
                step_standard = ""
            current_duration = duration or current_duration
            block_buffer.append({
                "source_id": SOURCE_ID,
                "table_number": table_num,
                "service_name": current_service or "",
                "client_type": client_type,
                "step_description": step_desc,
                "step_standard_of_service": step_standard,
                "total_duration": current_duration or "",
                "requirements": "",
            })
            continue

        flush_block("")
        current_service = collapsed[0]
        current_duration = collapsed[-1] if len(collapsed) >= 2 else ""

    flush_block("")
    return finished_rows


def main() -> None:
    if not DOCX_PATH.exists():
        print(f"MISSING: {DOCX_PATH}")
        print("Convert the .doc to .docx first (Word: Save As -> .docx),")
        print("saving it at the path above, then re-run this script.")
        return

    d = docx.Document(str(DOCX_PATH))
    all_rows: list[dict] = []
    for i, table in enumerate(d.tables, start=1):
        table_rows = parse_table(table, i)
        with_req = sum(1 for r in table_rows if r["requirements"])
        print(f"Table {i}: {len(table_rows)} step-rows ({with_req} with requirements captured)")
        all_rows.extend(table_rows)

    fieldnames = ["source_id", "table_number", "service_name", "client_type",
                  "step_description", "step_standard_of_service",
                  "total_duration", "requirements"]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        w.writeheader()
        w.writerows(all_rows)

    services = sorted(set(r["service_name"] for r in all_rows if r["service_name"]))
    total_with_req = sum(1 for r in all_rows if r["requirements"])
    print(f"\nTotal step-rows: {len(all_rows)}")
    print(f"Rows with requirements captured: {total_with_req}")
    print(f"Distinct services identified: {len(services)}")
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
