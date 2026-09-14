# Findings — Governance / Quality (Member 5 domain)

Based on actual pdfplumber/python-docx inspection of acquired files.

## SRC-GOVE-013 — Minutes of Business Consultative Meeting, 21 Oct 2025 (8 pages)
- CONFIRMED: zero extractable text on page 1. Scanned image PDF.
- LIMITATION: cannot be extracted without OCR, not currently in
  requirements.lock.txt. Documented as a Limitation in the paper
  rather than attempting OCR under time pressure.

## SRC-GOVE-012 — Citizen Engagement Plan (13 pages)
- CONFIRMED: page 1 extracts only "CamScanner" - phone-camera scan of
  a physical document. Same OCR limitation as above.

## SRC-GOVE-017 — LCC June News 2026 ("Voice of Livingstone" bulletin)
## SRC-GOVE-016 — LCC March News 2026 ("Voice of Livingstone" bulletin)
- Real extractable text, multiple CDF project mentions with real
  figures. Fully read page-by-page; 9 genuine CDF project records
  extracted from these two newsletters and routed into the CDF
  dataset (see data/interim/cdf_news_derived.csv, source_ids
  SRC-GOVE-016/017), not kept as a separate governance dataset.

## SRC-GOVE-009 — Service Delivery Charter (CORRECTED FINDING)
- Originally assessed as likely reference-only, by analogy with the
  other Governance sources. That assumption was WRONG and was never
  actually checked against this file's real content - see
  docs/decisions/decision_log.md, 2026-09-14 entry.
- Actual content: 6 structured Word tables (originally legacy .doc,
  converted to .docx for extraction) covering 99 distinct council
  services - permits, licences, certificates - each with client type,
  procedural steps, per-step time standards, total service duration,
  and application requirements.
- Extraction script: src/acquisition/extract_service_charter.py
- Output: data/interim/council_service_standards.csv - 372 step-level
  records, one row per (service, step) pair, full source_id
  provenance on every row.
- DECISION: this is its own standalone final dataset
  (db-unza26-csc4792-council-service-standards.csv), not merged into
  any other domain's data. See decision log for rationale.

## Governance Acts (Data Protection, Local Government, Solid Waste, etc.)
- Narrative legal text, no tables detected, reference-only. Cite in
  paper background/context, not extracted as dataset rows.

## Overall assessment for schema design (REVISED)
Governance domain now produces TWO real outputs:
1. Contribution to the CDF dataset (9 news-derived project records
   found in the two newsletters).
2. Its own standalone dataset: Council Service Standards (372 rows,
   99 services), from the Service Charter.
The Minutes and Citizen Engagement Plan remain documented limitations
(scanned, unextractable without OCR). The Acts remain reference-only.

LESSON: the original "thin/reference-only" assessment for this domain
was based on pattern-matching against similar-looking sources, not
on actually opening every file. Every source should be individually
checked before being written off, even when it resembles others that
turned out to be unextractable.
