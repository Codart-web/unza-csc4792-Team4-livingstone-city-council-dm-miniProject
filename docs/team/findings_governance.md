# Findings — Governance / Quality (Member 5 domain)

Based on actual pdfplumber inspection of representative acquired
files, not assumption.

## SRC-GOVE-013 — Minutes of Business Consultative Meeting, 21 Oct 2025 (8 pages)
- CONFIRMED: zero extractable text on page 1. This is a scanned image
  PDF, not real text. pdfplumber/pypdf extract nothing.
- LIMITATION: cannot be extracted without OCR (e.g. pytesseract), and
  OCR is not currently in requirements.lock.txt. Given time
  constraints, recommend documenting this as a stated Limitation in
  the Data Description Paper rather than attempting OCR setup now.

## SRC-GOVE-012 — Citizen Engagement Plan (13 pages)
- CONFIRMED: page 1 extracts only the literal text "CamScanner" - this
  document is a phone-camera scan (via the CamScanner app) of a
  physical document, not a native digital PDF.
- Same limitation as above: not extractable without OCR, and even
  with OCR, phone-scanned documents are often poor quality. Document
  as a Limitation.
- NOTE: the large file size (7.4MB for 13 pages) is now explained -
  this is high-resolution scanned images, not compressed text.

## SRC-GOVE-017 — LCC June News 2026 ("Voice of Livingstone" bulletin, 10 pages)
- Real extractable text, table detected on page 1.
- Page 1 already mentions: "13 CDF PROJECTS COMMISSIONED IN
  LIVINGSTONE - approximately K7.5 million worth of Constituency
  Development Fund (CDF) projects", quoting Town Clerk Ms Sombo
  Kawilila and District Commissioner Ms Eunice Nawa.
- FINDING FOR MEMBER 2 (CDF): this newsletter (and likely its
  March 2026 counterpart, SRC-GOVE-016) contains additional CDF
  project detail beyond what was found in the 9 individual news
  posts already processed. Same enrichment pattern as before.
  Recommend a full multi-page read of both newsletters during
  Phase 3 extraction if time allows - this is a real, evidenced lead,
  not speculation.

## Governance Acts (Data Protection, Local Government, Solid Waste, etc.)
- Not individually re-peeked here, but same expected structure as
  the Planning Acts: narrative legal text, reference-only, not
  tabular. Treat consistently.

## Overall assessment for schema design
Governance domain's genuinely tabular/extractable material is thin:
2 of the largest, most promising-looking files (the minutes, the
citizen engagement plan) turn out to be scanned images and cannot be
extracted under current tooling. The Acts are reference-only. The
strongest actual candidate for governance-domain rows may end up
being CDF-relevant facts pulled from the newsletters, which should
be routed to the CDF dataset (as already done for the 3 reclassified
news posts) rather than forced into a separate "governance" CSV.
