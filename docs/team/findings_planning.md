# Findings — Planning / Infrastructure (Member 4 domain)

Verified/acquired by the Leader on Member 4's behalf. Based on actual
pdfplumber inspection of representative files, not assumption.

## SRC-PLAN-001 — Integrated Development Plan 2021-2031 (220 pages)
- Real extractable text (NOT scanned). Table detected on page 1.
- Large, rich document. Title page confirms scope: tourism,
  environment, cultural heritage, socio-economic opportunities,
  infrastructure, through 2031.
- Candidate variables (pending deeper page-by-page review): sector,
  development priority/programme name, target year, indicator, status.
- 220 pages means full-document extraction is a real effort - worth
  scoping to specific chapters/sections rather than all pages, once
  the document's internal structure (table of contents) is reviewed.

## SRC-PLAN-005 — Climate Change and Resilience Strategy (2026-2031, 9 pages)
- Real extractable text, table detected on page 1. Short, manageable
  document.
- Candidate variables: climate priority area, strategy/action, target
  year, responsible unit.

## SRC-PLAN-003 — Urban and Regional Planning Act, 2015 (58 pages)
- Real extractable text, ZERO tables detected on page 1 (consistent
  with legal/legislative text structure - sections and clauses, not
  rows and columns).
- CONCLUSION: this and the other Acts in this domain (Environmental
  Management Act, Zambia National Public Health Institute Act) are
  reference/context material for the paper's background section, not
  row-level dataset sources. No tabular extraction expected.

## SRC-PLAN-007, SRC-PLAN-008 (category-index pages)
- Confirmed inaccessible (real HTTP 404). No content to describe.

## Overall assessment for schema design
Planning domain likely yields ONE dataset (from the IDP and/or Climate
Strategy, both structured/tabular), not multiple. The 2 Acts are
citation-only. Given 220 pages in the IDP, recommend targeting a
specific known section (e.g. a projects/priorities table) rather than
attempting full-document extraction under time pressure.
