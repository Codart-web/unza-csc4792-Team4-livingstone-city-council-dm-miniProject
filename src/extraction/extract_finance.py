"""Extract preliminary finance records from the member-3 (Finance) PDF sources.

Phase 3 (Extraction) scope: pull raw structured values out of the machine-readable
finance PDFs into tables, one row per real-world observation, every row carrying its
source_id back to docs/source_register/for_member_3.csv. No cleaning/standardisation
happens here - values are copied as printed (minus thousands separators).

Four distinct row-shapes exist in the finance sources, so four separate interim
tables are produced instead of forcing everything into one wide CSV (project rule:
"one row must have a clear meaning" / "do not mix fundamentally different
observations into one table"):

  finance_budget_raw.csv            - one row per revenue line item per annual budget
                                       (SRC-FINA-003, SRC-FINA-011, SRC-FINA-016)
  finance_performance_raw.csv       - one row per revenue/payment line item in the
                                       2025 semi-annual budget performance report
                                       (SRC-FINA-004)
  finance_capital_projects_raw.csv  - one row per capital project in that same report
  finance_debt_arrears_raw.csv      - one row per debt/arrears category in that report

Sources with no extractable text layer (scanned financial statements, audit
opinions, bi-annual statements - see docs/team/findings_finance.md) are not
processed here; they need OCR or manual transcription first.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pdfplumber

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER = REPO_ROOT / "docs" / "source_register" / "for_member_3.csv"
INTERIM_DIR = REPO_ROOT / "data" / "interim"
RAW_PDF_DIR = REPO_ROOT / "data" / "raw" / "pdf"

BUDGET_SOURCE_IDS = ("SRC-FINA-003", "SRC-FINA-011", "SRC-FINA-016")
PERFORMANCE_SOURCE_ID = "SRC-FINA-004"

BUDGET_FIELDS = [
    "source_id",
    "source_title",
    "revenue_category",
    "item_code",
    "budget_item",
    "approved_budget",
    "approved_budget_year",
    "revised_budget",
    "revised_budget_year",
    "estimated_budget",
    "estimated_budget_year",
    "source_page",
    "source_url",
]

PERFORMANCE_FIELDS = [
    "source_id",
    "source_title",
    "statement_section",
    "revenue_category",
    "item_code",
    "item_label",
    "row_type",
    "budget_value",
    "actual_value",
    "variance_value",
    "performance_pct",
    "period",
    "source_page",
    "source_url",
]

CAPITAL_PROJECT_FIELDS = [
    "source_id",
    "source_title",
    "project_seq",
    "project_name",
    "start_date",
    "end_date",
    "contract_amount",
    "cumulative_payment",
    "balance",
    "funding_source",
    "project_status",
    "period",
    "source_page",
    "source_url",
]

DEBT_ARREARS_FIELDS = [
    "source_id",
    "source_title",
    "narration",
    "outstanding_start_date",
    "outstanding_start_amount",
    "outstanding_end_date",
    "outstanding_end_amount",
    "source_page",
    "source_url",
]

REPORT_FIELDS = ["source_id", "source_title", "source_type", "status", "extraction_result", "notes"]

# Verified by direct text inspection (see docs/team/findings_finance.md) to be
# national legislation/policy documents with no Livingstone-specific figures.
CONTEXT_ONLY_SOURCE_IDS = ("SRC-FINA-001", "SRC-FINA-002", "SRC-FINA-012")


def read_register() -> dict[str, dict[str, str]]:
    with REGISTER.open(encoding="utf-8", newline="") as handle:
        return {row["source_id"]: row for row in csv.DictReader(handle, delimiter="|")}


def find_pdf_for_source(source_id: str) -> Path:
    matches = list(RAW_PDF_DIR.glob(f"{source_id}_*.pdf"))
    if not matches:
        raise FileNotFoundError(f"No local PDF found for {source_id} in {RAW_PDF_DIR}")
    return matches[0]


def clean_number(value: str | None) -> str:
    value = (value or "").strip().replace(",", "").replace(" ", "").replace("\n", "")
    if value in {"-", "—", "", "N/A", "n/a", "#DIV/0!"}:
        return ""
    return value


def clean_cell(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()


def clean_pct(value: str | None) -> str:
    value = clean_cell(value)
    if not value or value == "#DIV/0!":
        return ""
    return value.replace("%", "").strip()


# ---------------------------------------------------------------------------
# Budget revenue tables (SRC-FINA-003 / 011 / 016)
# ---------------------------------------------------------------------------


def parse_header_years(cells: list[str]) -> tuple[str, str, str] | None:
    years: list[str] = []
    for cell in cells[2:]:
        years.extend(re.findall(r"(20\d{2})", cell))
    if len(years) >= 3:
        return years[0], years[1], years[2]
    return None


def extract_budget_rows(source_id: str, source: dict[str, str]) -> list[dict[str, str]]:
    pdf_path = find_pdf_for_source(source_id)
    rows: list[dict[str, str]] = []
    years: tuple[str, str, str] | None = None
    category = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            for table in page.extract_tables():
                for raw_row in table:
                    cells = [clean_cell(c) for c in raw_row]
                    if not any(cells):
                        continue
                    code, desc = cells[0], cells[1] if len(cells) > 1 else ""

                    if code == "CODE" and "REVENUE" in desc.upper():
                        if years is None:
                            years = parse_header_years(cells)
                        continue

                    trailing_values = [c for c in cells[2:] if c]

                    if not trailing_values:
                        # Category header row, e.g. "01  Local taxes/rates"
                        if desc:
                            category = desc
                        continue

                    if len(trailing_values) != 3:
                        # Unexpected shape (e.g. a stray text row) - skip rather
                        # than guess which value goes where.
                        continue

                    approved, revised, estimate = trailing_values
                    if years is None:
                        continue
                    rows.append(
                        {
                            "source_id": source_id,
                            "source_title": source["source_title"],
                            "revenue_category": category,
                            "item_code": code,
                            "budget_item": desc,
                            "approved_budget": clean_number(approved),
                            "approved_budget_year": years[0],
                            "revised_budget": clean_number(revised),
                            "revised_budget_year": years[1],
                            "estimated_budget": clean_number(estimate),
                            "estimated_budget_year": years[2],
                            "source_page": str(page_num),
                            "source_url": source["url"],
                        }
                    )
    return rows


# ---------------------------------------------------------------------------
# Semi-annual budget performance report (SRC-FINA-004)
# ---------------------------------------------------------------------------

LEAF_CODE_RE = re.compile(r"^(?P<code>\d+\.\d+)\s+(?P<desc>.+)$")
TOTAL_LABELS = {"total", "total payments"}


def extract_period_label(pdf: pdfplumber.PDF) -> str:
    text = pdf.pages[0].extract_text() or ""
    match = re.search(r"Period:\s*([0-9A-Za-z-]+ to [0-9A-Za-z-]+)", text)
    return match.group(1) if match else ""


def parse_performance_table(
    table: list[list[str | None]],
    section: str,
    source_id: str,
    source: dict[str, str],
    period: str,
    page_num: int,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    category = ""

    for raw_row in table:
        cells = [clean_cell(c) for c in raw_row]
        if not any(cells):
            continue
        col0, col1 = cells[0], cells[1] if len(cells) > 1 else ""

        row_type = "item"
        code = ""
        label = ""

        if col0.lower() in TOTAL_LABELS or col0.lower().startswith("total"):
            row_type = "total"
            label = col0
            values = [c for c in cells[1:] if c]
        elif LEAF_CODE_RE.match(col1):
            m = LEAF_CODE_RE.match(col1)
            code, label = m.group("code"), m.group("desc")
            values = [c for c in cells[2:] if c]
        elif col1.lower() == "sub - total":
            row_type = "subtotal"
            label = col1
            values = [c for c in cells[2:] if c]
        elif col0.isdigit() and col1:
            values = [c for c in cells[2:] if c]
            if not values:
                # Category header, e.g. "1  National Support"
                category = col1
                continue
            code, label = col0, col1
        else:
            continue

        if len(values) not in (3, 4):
            continue
        if len(values) == 3:
            budget_v, actual_v, variance_v = values
            pct = ""
        else:
            budget_v, actual_v, variance_v, pct = values

        rows.append(
            {
                "source_id": source_id,
                "source_title": source["source_title"],
                "statement_section": section,
                "revenue_category": category,
                "item_code": code,
                "item_label": label,
                "row_type": row_type,
                "budget_value": clean_number(budget_v),
                "actual_value": clean_number(actual_v),
                "variance_value": clean_number(variance_v),
                "performance_pct": clean_pct(pct),
                "period": period,
                "source_page": str(page_num),
                "source_url": source["url"],
            }
        )
    return rows


def extract_performance_rows(source: dict[str, str]) -> list[dict[str, str]]:
    source_id = PERFORMANCE_SOURCE_ID
    pdf_path = find_pdf_for_source(source_id)
    rows: list[dict[str, str]] = []

    with pdfplumber.open(pdf_path) as pdf:
        period = extract_period_label(pdf)
        page = pdf.pages[0]
        for table in page.extract_tables():
            header = clean_cell(table[0][0] if table and table[0] else "")
            header_row = [clean_cell(c) for c in table[0]] if table else []
            if "Receipts" not in header_row:
                continue
            # The revenue-sources table's header repeats "#|Receipts|...";
            # distinguish it from the payments table by scanning row labels.
            body_text = " ".join(clean_cell(c) for row in table[1:3] for c in row)
            section = "revenue_sources" if "National Support" in body_text else "payments"
            rows.extend(
                parse_performance_table(table, section, source_id, source, period, page_num=1)
            )
    return rows


def extract_capital_project_rows(source: dict[str, str]) -> list[dict[str, str]]:
    source_id = PERFORMANCE_SOURCE_ID
    pdf_path = find_pdf_for_source(source_id)
    rows: list[dict[str, str]] = []

    with pdfplumber.open(pdf_path) as pdf:
        period = extract_period_label(pdf)
        for page_num, page in enumerate(pdf.pages, start=1):
            for table in page.extract_tables():
                header_cells = [clean_cell(c) for c in (table[0] if table else [])]
                if not any("Project Name" in c for c in header_cells):
                    continue
                for raw_row in table[2:]:
                    cells = [clean_cell(c) for c in raw_row]
                    if len(cells) < 8 or not cells[1]:
                        continue
                    if cells[0].lower() == "total":
                        continue
                    rows.append(
                        {
                            "source_id": source_id,
                            "source_title": source["source_title"],
                            "project_seq": cells[0],
                            "project_name": cells[1],
                            "start_date": cells[2],
                            "end_date": cells[3],
                            "contract_amount": clean_number(cells[4]),
                            "cumulative_payment": clean_number(cells[5]),
                            "balance": clean_number(cells[6]),
                            "funding_source": cells[7],
                            "project_status": cells[8] if len(cells) > 8 else "",
                            "period": period,
                            "source_page": str(page_num),
                            "source_url": source["url"],
                        }
                    )
    return rows


def extract_debt_arrears_rows(source: dict[str, str]) -> list[dict[str, str]]:
    source_id = PERFORMANCE_SOURCE_ID
    pdf_path = find_pdf_for_source(source_id)
    rows: list[dict[str, str]] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            for table in page.extract_tables():
                header_cells = [clean_cell(c) for c in (table[0] if table else [])]
                if not header_cells or "Narration" not in header_cells[0]:
                    continue
                start_match = re.search(r"\d{1,2}-[A-Za-z]{3}-\d{4}", header_cells[1])
                end_match = re.search(r"\d{1,2}-[A-Za-z]{3}-\d{4}", header_cells[2])
                start_date = start_match.group(0) if start_match else ""
                end_date = end_match.group(0) if end_match else ""
                for raw_row in table[1:]:
                    cells = [clean_cell(c) for c in raw_row]
                    if len(cells) < 3 or not cells[0]:
                        continue
                    rows.append(
                        {
                            "source_id": source_id,
                            "source_title": source["source_title"],
                            "narration": cells[0],
                            "outstanding_start_date": start_date,
                            "outstanding_start_amount": clean_number(cells[1]),
                            "outstanding_end_date": end_date,
                            "outstanding_end_amount": clean_number(cells[2]),
                            "source_page": str(page_num),
                            "source_url": source["url"],
                        }
                    )
    return rows


def probe_pdf_text(source_id: str) -> tuple[int, int]:
    """Return (page_count, extractable_char_count) for a source's local PDF."""
    pdf_path = find_pdf_for_source(source_id)
    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages
        chars = sum(len(page.extract_text() or "") for page in pages)
        return len(pages), chars


def build_extraction_report(
    register: dict[str, dict[str, str]],
    budget_rows: list[dict[str, str]],
    performance_rows: list[dict[str, str]],
    capital_rows: list[dict[str, str]],
    debt_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Per-source extraction outcome for every registered finance source.

    Status is derived from what the extraction functions actually produced
    (for the 4 machine-readable sources) or from probing the PDF's own text
    layer at run time (for everything else) - not from a hand-written note -
    so this file stays true if the script is re-run against different inputs.
    """
    budget_counts = {
        source_id: sum(1 for row in budget_rows if row["source_id"] == source_id)
        for source_id in BUDGET_SOURCE_IDS
    }
    report: list[dict[str, str]] = []

    for source_id in sorted(register):
        source = register[source_id]
        status = source["status"]

        if source_id in budget_counts:
            report.append(
                {
                    "source_id": source_id,
                    "source_title": source["source_title"],
                    "source_type": source["source_type"],
                    "status": status,
                    "extraction_result": "records extracted",
                    "notes": (
                        f"{budget_counts[source_id]} revenue line-item rows written to "
                        "finance_budget_raw.csv, with source provenance."
                    ),
                }
            )
            continue

        if source_id == PERFORMANCE_SOURCE_ID:
            report.append(
                {
                    "source_id": source_id,
                    "source_title": source["source_title"],
                    "source_type": source["source_type"],
                    "status": status,
                    "extraction_result": "records extracted",
                    "notes": (
                        f"{len(performance_rows)} revenue/payment line items, "
                        f"{len(capital_rows)} capital projects, and {len(debt_rows)} "
                        "debt/arrears rows written across finance_performance_raw.csv, "
                        "finance_capital_projects_raw.csv, and "
                        "finance_debt_arrears_raw.csv, with source provenance."
                    ),
                }
            )
            continue

        if status == "rejected":
            report.append(
                {
                    "source_id": source_id,
                    "source_title": source["source_title"],
                    "source_type": source["source_type"],
                    "status": status,
                    "extraction_result": "not applicable",
                    "notes": source["notes"],
                }
            )
            continue

        if source_id in CONTEXT_ONLY_SOURCE_IDS:
            report.append(
                {
                    "source_id": source_id,
                    "source_title": source["source_title"],
                    "source_type": source["source_type"],
                    "status": status,
                    "extraction_result": "not extracted",
                    "notes": (
                        "Verified by direct text inspection to be a national "
                        "legislation/policy document with no Livingstone-specific "
                        "figures; context only."
                    ),
                }
            )
            continue

        try:
            page_count, char_count = probe_pdf_text(source_id)
        except FileNotFoundError:
            notes = "Local PDF not found; cannot probe for extractable text."
        else:
            if page_count == 0:
                notes = (
                    "Malformed/non-standard PDF: pdfplumber reports 0 pages (e.g. a "
                    "single embedded image object with no page tree). Cannot be "
                    "paginated for OCR without repair."
                )
            elif char_count == 0:
                notes = (
                    f"Scanned document ({page_count} pages), zero extractable "
                    "characters via pdfplumber on every page. Needs OCR or manual "
                    "transcription."
                )
            else:
                notes = (
                    f"{page_count} pages, {char_count} extractable characters found "
                    "but not yet matched to a known table layout; needs manual "
                    "review before extraction."
                )

        report.append(
            {
                "source_id": source_id,
                "source_title": source["source_title"],
                "source_type": source["source_type"],
                "status": status,
                "extraction_result": "not extracted",
                "notes": notes,
            }
        )

    return report


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="|")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    register = read_register()

    budget_rows: list[dict[str, str]] = []
    for source_id in BUDGET_SOURCE_IDS:
        budget_rows.extend(extract_budget_rows(source_id, register[source_id]))

    performance_source = register[PERFORMANCE_SOURCE_ID]
    performance_rows = extract_performance_rows(performance_source)
    capital_rows = extract_capital_project_rows(performance_source)
    debt_rows = extract_debt_arrears_rows(performance_source)

    write_csv(INTERIM_DIR / "finance_budget_raw.csv", BUDGET_FIELDS, budget_rows)
    write_csv(INTERIM_DIR / "finance_performance_raw.csv", PERFORMANCE_FIELDS, performance_rows)
    write_csv(
        INTERIM_DIR / "finance_capital_projects_raw.csv",
        CAPITAL_PROJECT_FIELDS,
        capital_rows,
    )
    write_csv(INTERIM_DIR / "finance_debt_arrears_raw.csv", DEBT_ARREARS_FIELDS, debt_rows)

    report_rows = build_extraction_report(
        register, budget_rows, performance_rows, capital_rows, debt_rows
    )
    write_csv(INTERIM_DIR / "finance_extraction_report.csv", REPORT_FIELDS, report_rows)

    print(f"finance_budget_raw.csv: {len(budget_rows)} rows")
    print(f"finance_performance_raw.csv: {len(performance_rows)} rows")
    print(f"finance_capital_projects_raw.csv: {len(capital_rows)} rows")
    print(f"finance_debt_arrears_raw.csv: {len(debt_rows)} rows")
    print(f"finance_extraction_report.csv: {len(report_rows)} sources covered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
