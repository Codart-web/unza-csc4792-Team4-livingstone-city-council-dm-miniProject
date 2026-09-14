# Finance Findings

## Review scope

Member 3 finance sources were acquired from the Livingstone City Council register and reviewed for usefulness. The finance evidence falls into three groups:

1. **Primary extractable sources:** council budgets and the 2025 semi-annual performance report.
2. **Useful supporting sources:** scanned financial statements, audit opinions, consultative budget records, and the debt/arrears mechanism.
3. **Context-only or unusable sources:** national legal documents and broken category-index URLs.

Raw files remain local under `data/raw/`. No raw source is committed to Git.

## Primary sources for finance tables

### SRC-FINA-003 - 2024 Annual Budget

A 39-page, machine-readable Livingstone City Council output-based annual budget. It contains council mandate and programme information, budget headings, revenue and expenditure sections, and financial values that can support a 2024 budget table. Candidate observations should be one row per budget item or financial measure, retaining the programme/head and the reported unit.

### SRC-FINA-004 - 2025 Semi-Annual Budget Performance Report

A six-page, machine-readable performance report covering 1 January to 30 June 2025. It includes revenue sources, budget values, receipts/actual values, and performance information. This is the strongest source for comparing budgeted and actual revenue for the reported period. The period must remain explicit; semi-annual values must not be presented as full-year totals.

### SRC-FINA-011 - 2025 Annual Budget

A 60-page, machine-readable output-based annual budget for Livingstone City Council. It contains revenue and expenditure planning information, programme/head structure, and budget values for 2025. It can support a yearly budget dataset and comparison with the 2024 and 2026 budgets.

### SRC-FINA-016 - 2026 Annual Budget

A 63-page, machine-readable output-based annual budget for Livingstone City Council. It contains budget headings, revenue and expenditure planning information, programme structure, and financial values for 2026. It should be kept separate from 2024 and 2025 values by financial year.

## Supporting sources

- `SRC-FINA-005`, `SRC-FINA-007`: audit-opinion documents. The downloaded files are image-based and need OCR or manual review before extracting audit findings.
- `SRC-FINA-006`, `SRC-FINA-008`, `SRC-FINA-009`, `SRC-FINA-010`, `SRC-FINA-015`, `SRC-FINA-017`: financial-statement documents. They are valid council finance sources, but their text layer is effectively empty, so table extraction requires OCR or manual transcription with page-level validation.
- `SRC-FINA-012`: national/local-authority debt and arrears monitoring mechanism. It is useful for definitions and reporting context, but it is not a Livingstone-specific arrears dataset.
- `SRC-FINA-013`, `SRC-FINA-014`: budget consultative meeting documents. They provide consultation context and may contain proposed budget or revenue priorities, but they should not be treated as approved financial totals without checking the scanned pages.
- `SRC-FINA-001`, `SRC-FINA-002`: national planning/budgeting and public finance management legislation. These explain the legal framework and are not council observations.

## Recommended finance datasets

1. `finance_budget`: one row per reported budget item, programme/head, financial year, and measure from SRC-FINA-003, SRC-FINA-011, and SRC-FINA-016.
2. `finance_performance`: one row per revenue source or performance measure for the stated 2025 semi-annual period from SRC-FINA-004.
3. `finance_statements`: only after OCR/manual extraction and validation of the scanned statement pages.

Recommended fields include `financial_year`, `period`, `programme_or_head`, `measure_type`, `revenue_category`, `revenue_item`, `budget_value`, `actual_value`, `unit`, `source_id`, `source_page`, and `source_url`, but only where the source actually supports them.

Do not infer LGEF, revenue, expenditure, or actual values from a blank template or from a national legal document. Missing values remain missing, and semi-annual values must not be silently annualised.

## Phase 3 — extraction results (2026-09-14)

`src/extraction/extract_finance.py` opens the machine-readable finance PDFs with
`pdfplumber`, uses its table extraction (not raw-text regex) for every table, and
writes four separate interim CSVs to `data/interim/`. Four tables rather than one,
because the underlying observations are not the same shape (project Rule 4: "one
row must have a clear meaning" / do not merge unrelated observations):

| File | Rows | Source(s) | One row = |
|---|---|---|---|
| `finance_budget_raw.csv` | 274 | SRC-FINA-003, 011, 016 | one revenue line item (or category SubItem Total) in one annual budget, carrying approved/revised/estimated values **and the specific year each column applies to** |
| `finance_performance_raw.csv` | 30 | SRC-FINA-004 | one revenue or payment line item (or subtotal/total) for the stated Jan-Jun 2025 period, with budget, actual, variance and performance % exactly as the source labels them |
| `finance_capital_projects_raw.csv` | 12 | SRC-FINA-004 | one capital project, with contract amount, cumulative payment, balance, funding source and status |
| `finance_debt_arrears_raw.csv` | 16 | SRC-FINA-004 | one debt/arrears category, with outstanding amounts at the start and end of the reporting period |

`data/interim/finance_extraction_report.csv` records the per-source outcome for
all 20 registered finance sources (extracted / not extracted / rejected, and why).

### Verified against source

- Sample budget rows (e.g. SRC-FINA-003 "Residential": 10,294,498 / 11,323,948 /
  12,456,343) were checked against the PDF text and match exactly.
- The 2025 performance report's own column labels ("Budget a", "Actual b",
  "Variance c=a-b", "Performance b/a") were read directly from the table header,
  not assumed - an early draft of this script guessed the opposite order (actual
  first, budget second), which the arithmetic disproves: e.g. for "Local
  Government Equalisation Fund", 17,512,929.96 (Budget) − 5,949,157.00 (Actual) =
  11,563,772.96 (Variance), and 5,949,157.00 / 17,512,929.96 ≈ 34% (Performance),
  matching the printed values. Always confirm the column order against a header
  and at least one row's own arithmetic before trusting it.
- Category subtotals were spot-checked by re-summing the item rows above them;
  they agree except for one source anomaly (see below).

### Known data-quality issue kept, not fixed

SRC-FINA-016 (2026 budget)'s "Commercial" revenue line has a revised-2027 figure
(221,567,902) that appears to carry a stray extra digit compared to its own
approved-2026 and estimate-2028 columns (both 21,567,902), and the category's
"SubItem Total" row is inflated by the same amount in the same column - i.e. the
error originates in the council's own document, not in extraction. It is copied
as printed. See `docs/decisions/decision_log.md` (2026-09-14 entry) and the notes
column of `finance_extraction_report.csv`.

### What was not extracted, and why

- **Programme/sub-programme/economic-classification budget tables** (2024 budget
  pages 7-13 and equivalents in the 2025/2026 budgets): these use "(0)" and "-"
  placeholder cells in a merged-cell layout that is materially less reliable to
  parse mechanically than the revenue table. Deferred rather than risking
  fabricated column alignment.
- **Budget Programme Output Performance** table (SRC-FINA-004, ~105 KPI rows
  spanning pages 1-3): non-monetary output/target/actual indicators (e.g.
  "Number of boreholes drilled"). This is closer to a Planning/Governance KPI
  dataset than a Finance revenue/budget one; flagged for Member 4/5 rather than
  duplicated here, per Rule 5 (do not over-expand).
- **8 scanned PDFs** (SRC-FINA-005/006/007/008/009/010/013/014/015/017): zero
  extractable text via pdfplumber on every page. SRC-FINA-007 specifically is a
  malformed PDF - a single embedded JPEG with no page tree, so it cannot even be
  paginated for OCR without repair first.
- **SRC-FINA-001, 002, 012**: verified by direct text inspection to be national
  legislation/policy documents with no Livingstone-specific figures - correctly
  excluded as context-only, confirming the earlier Phase 2 assessment.
