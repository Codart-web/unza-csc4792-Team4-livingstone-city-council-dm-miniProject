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
