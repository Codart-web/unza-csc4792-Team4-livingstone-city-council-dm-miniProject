# Integration notes — Finance and CDF (Member 3 + Member 2 scope)

Scope: only the integration work that can be done without the other domains'
data or team agreement on the final cross-domain structure - relating the
Finance and CDF datasets to each other and to themselves. The final,
cross-domain dataset structure (all five members' data) still needs the
Leader and Data Owners to agree it, per the project's own Phase 6 rule.

## Common fields across all 5 final datasets

Every row in every one of `finance_budget`, `finance_performance`,
`finance_capital_projects`, `finance_debt_arrears`, and `cdf_projects`
carries `source_id` and `source_url`, so any row can always be traced back
to `docs/source_register/for_member_2.csv` / `for_member_3.csv` and from
there to the original PDF/webpage. This is the join key for any future
cross-dataset work.

## Relationships within Finance's 4 datasets

- `finance_performance`, `finance_capital_projects`, and
  `finance_debt_arrears` all come from the single source `SRC-FINA-004`
  (2025 semi-annual report) and share the same reporting period
  (`period_start_date`/`period_end_date` = 2025-01-01/2025-06-30 after
  Phase 5). They are three different observation types from one document,
  not duplicates of each other.
- `finance_budget` comes from three different documents (the 2024/2025/2026
  Annual Budgets, `SRC-FINA-003`/`011`/`016`) and is conceptually related to
  `finance_performance`'s `budget_value` column: both represent the
  council's budgeted revenue target, just restated in a different document.

## Cross-check: 2025 "Local Taxes" budget figure (finance_budget vs finance_performance)

`finance_performance` restates a `budget_value` for each revenue line - in
principle this should agree with the matching category's total in the
matching year's `finance_budget` (extracted independently, from a different
PDF, by a different function in `extract_finance.py`). Checked one:

- `finance_budget` (SRC-FINA-011, 2025 Annual Budget), category
  "Local taxes/rates", `approved_budget_year`=2025: SubItem Totals
  44,377,379 (Residential+Commercial+Hospitality) + 166,080 (Personal levy)
  = **44,543,459**
- `finance_performance` (SRC-FINA-004, 2025 semi-annual report), item
  "Local Taxes", `budget_value` = **44,543,478.18**

Difference: 19.18 out of ~44.5 million (0.00004%) - consistent with a minor
rounding/decimal-cents difference between when each document was prepared,
not a real disagreement. This is independent corroboration between two
different source PDFs, extracted by two different code paths, and is strong
evidence the Phase 3 extraction is correct for both sources. No correction
needed; recorded here as validation evidence for Phase 7.

**Limitation:** this was checked for one category as a spot-check, not
exhaustively for every category/year - a full reconciliation is Phase 7
Validation work, not Phase 6 Integration.

## Cross-check: CDF projects vs Finance capital projects

`finance_capital_projects` (from SRC-FINA-004) contains one row relevant to
CDF: "CDF Community projects", `contract_amount`=21,962,692.00,
`funding_source`=CDF, `project_status`=WIP, for the Jan-Jun 2025 period.

This is **not** a duplicate of any row in `cdf_projects`:
- The 22 SRC-CDF-012 rows are individually-named **2024**-approved projects
  with no cost figures in their source PDF - different year, different
  granularity (one lump-sum finance line vs many named projects).
- The 3 news-derived **2025** rows (SRC-CDF-038/039/040) have individual
  costs summing to 2,150,687.75 - about 10% of the 21.96M lump sum, which is
  consistent with "3 highlighted projects out of a larger funded programme,"
  not a contradiction.

**Open item, not resolved here:** we do not have an "Approved 2025 CDF
Community Projects" source (the 2024 equivalent is SRC-CDF-012) to reconcile
against the 21.96M figure item-by-item. Recorded as a limitation rather than
assumed - if such a source is acquired later, this should be revisited.

## Ward-name and category discrepancies (see decision_log.md for the CDF-side ones)

- CDF: "Maramba" (SRC-CDF-012) vs "Maramba (R Section)" (SRC-CDF-038) - left
  unmerged, flagged for the team's ward-name harmonisation pass.
- Finance has no ward-level data, so no Finance/CDF ward cross-check is
  possible with current sources.
