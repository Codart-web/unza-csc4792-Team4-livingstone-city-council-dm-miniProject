# Decision Log

Log every case where sources disagree, per Phase 5 Integration Rule.
Do not silently pick a value — record why.

## Template
- **Date:**
- **Issue:**
- **Sources compared:**
- **Resolution:**
- **Reasoning:**

## DECISION: 2026-09-10 — Use unverified TLS for reading the Livingstone council site

**Context**
The official source URL `https://www.livingstonecouncil.gov.zm` serves a TLS
certificate that cannot be verified from any correctly configured client:

- Certificate CN is `www.mlgrd.gov.zm`, not the council hostname (hostname mismatch).
- Certificate `notAfter` is `2026-09-06`, i.e. already expired.
- The serving chain omits the Sectigo intermediate certificate.

Confirmed via `openssl s_client` on 2026-09-10. Local `ca-certificates` package
is current (`20260601~26.04.1`). The problem is on the server side and cannot
be fixed by us.

**Decision**
Read-only HTTP GETs against `*.livingstonecouncil.gov.zm` will be performed with
`requests.get(..., verify=False)`. This is scoped to:
- `src/acquisition/recon_site.py` (recon)
- any future `src/acquisition/*` read scripts

Nothing else in the project disables TLS verification.

**Rationale**
- All traffic is GET on public pages. No credentials, no writes, no private data.
- The certificate problems are visual/verifiable by any reader, so no trust is broken.
- Blocking the entire mini-project on a defect we cannot repair is disproportionate.

**Disclosure**
- This decision is disclosed in the notebook (Environment / Reproducibility section).
- This decision is disclosed in the Data Description Paper (Limitations section).
- Any URL that is captured in our dataset or paper is stored as HTTP(S) literal,
  and the SSL warning is documented as a known issue.


## DECISION: 2026-09-11 — Phase 1 (Source Discovery) closed with documented gaps

**Context**
148 same-domain URLs discovered via two-level reconnaissance of
livingstonecouncil.gov.zm. 113 registered as candidate sources across
cdf (37), finance (20), planning (8), governance (24), other (24).

No standalone source was found for: revenue breakdown (market fees,
local taxes, levies), LGEF specifically, water/sanitation/roads
infrastructure, or WDC material.

**Decision**
Phase 1 is closed on the basis that these four areas are most likely
embedded as line items within sources already registered (financial
statements, budget documents, the IDP) rather than published as
separate documents. This will be confirmed or refuted during Phase 3
(Extraction) when each document is actually opened.

**Rationale**
Continued open-ended searching has a low probability of finding
additional standalone sources and is not a good use of remaining time
against the 12 September deadline. If Phase 3 confirms these are
genuinely absent, this becomes a stated Limitation in the Data
Description Paper rather than an invented data point.

## DECISION: 2026-09-11 — Reclassified 3 news posts as CDF project records

**Context**
9 unlabeled WordPress news posts were assigned to LEADER for manual
review (no domain could be inferred from URL/anchor text alone).
Content was fetched and read directly.

**Decision**
3 of 9 posts contained genuine structured CDF project data (ward,
cost, funding year, completion percentage, and in one case a named
contractor) and were reassigned from domain=other/LEADER to
domain=cdf/Member 2, given new source IDs (SRC-CDF-038 to 040).
3 posts were kept as contextual/background sources only (planning
narrative, no structured data). 3 posts were rejected as unrelated
to any project data domain (disaster relief, voter education,
unrelated public event).

**Rationale**
This directly implements the project plan's Section 3E expectation
that council news reports can enrich CDF/project records where they
contain structured facts. Reclassification was based on actual
content review, not assumption.

## DECISION: 2026-09-12 — Leader performed Member 4's Phase 1b verification/acquisition

**Context**
Member 4 (Planning/Infrastructure) had prior commitments preventing
personal completion of Phase 1b source verification/acquisition
before the compressed deadline. The Leader performed this work
directly on Member 4's branch (feature/planning) to avoid blocking
downstream phases.

**What was done**
All 8 registered planning sources were verified: 2 category-index
pages returned real HTTP 404s (consistent with the same failure
pattern already observed across CDF/Finance/Governance category
pages - a site-wide issue), the ZDSP page loads but is an external
links directory with no new sources, and 5 PDFs were confirmed real
and downloaded to data/raw/pdf/, including the 32MB Integrated
Development Plan 2021-2031.

**Rationale**
This is consistent with the same Leader-override pattern already
used for the Leader's own source family and, separately, for
downloading Member 5's governance sources via WSL due to a network
constraint. Recorded here for transparency in the project
methodology and for accurate individual-contribution accounting.

## DECISION: 2026-09-14 — Kept an apparent source typo in the 2026 budget as-is

**Context**
While extracting the 2026 Annual Budget revenue table (SRC-FINA-016)
into `finance_budget_raw.csv`, the "Commercial" local-tax line under
category "01 Local taxes/rates" reads (as printed in the PDF):
approved budget 2026 = 21,567,902; revised budget 2027 = 221,567,902;
budget estimate 2028 = 21,567,902. The revised-2027 figure has an
extra leading "2" compared to both neighbouring years and does not
sum correctly into the category's own "SubItem Total" row for that
column (51,761,556 approved vs. 251,761,556 revised vs. 51,761,556
estimate - the revised subtotal is likewise inflated by the same
extra digit, so the source document is internally consistent with
its own typo, not just a one-off OCR/rendering artifact on our side).

**Decision**
The value is extracted and stored exactly as printed
(`revised_budget=251761556`, `revised_budget_year=2027`). No
correction is applied.

**Rationale**
Rule 2 (never invent data) and Rule 3 (keep raw evidence) both apply:
we do not know whether 21,567,902 or 221,567,902 is the council's
intended figure, and guessing would silently fabricate a number.
This is flagged here and in
`data/interim/finance_extraction_report.csv` so it can be excluded
or footnoted during cleaning/validation (Phase 4/6) rather than
quietly propagating into the final dataset.

## DECISION: 2026-09-14 — Service Charter yields its own standalone dataset

**Context**
The Service Charter (SRC-GOVE-009, a legacy .doc file) was earlier
assessed in docs/team/findings_governance.md as likely reference-only,
based on the pattern seen in other Governance sources (Acts,
newsletters). That assessment was never verified against this
specific file's actual content.

On manual inspection, the file contains 6 structured Word tables
covering 99 distinct council services (permits, licences,
certificates), each broken into client type, procedural steps, per-
step time standards, total service duration, and application
requirements - a genuine, rich, tabular dataset of 372 step-level
records.

**Decision**
This will be produced as its OWN standalone final dataset,
independent of CDF/Finance/Planning/Governance's other material:
db-unza26-csc4792-council-service-standards.csv

It will NOT be merged or folded into any other domain's dataset at
Integration (Phase 6).

**Rationale**
The content is self-contained (does not reference or depend on other
domains' data), structurally distinct (service/step/standard schema,
not project/cost/ward like CDF), and substantial enough (372 rows,
99 services) to stand alone rather than being treated as a minor
enrichment.

**Lesson for methodology section of the paper**
The earlier "thin/reference-only" assessment for this file was an
untested assumption based on similar-looking sources, not a checked
fact. This is worth stating as a limitation of early-stage manual
triage: document-type pattern-matching is not a substitute for
actually opening every source.

## DECISION: 2026-09-14 — Raised minimum Python version to 3.11; pinned numpy ceiling

**Context**
requirements.lock.txt pinned numpy==2.5.3, which requires Python
>=3.12. This was generated on the Leader's machine (Python 3.14) with
an unbounded constraint in requirements.txt (numpy>=1.26). Member 4,
on Python 3.11, could not install it at all - pip aborts the entire
batch install when one pinned version can't be resolved, silently
preventing 8 unrelated packages listed after numpy from installing
too. This caused repeated, confusing "8 failed" test results across
multiple sessions before the root cause was isolated.

Checked PyPI directly: no numpy version supports both Python 3.10
(the previously documented minimum) and Python 3.14 (Leader's actual
version) simultaneously - numpy dropped 3.10 support at 2.3.0, and
no version below 2.3 has Python 3.14 wheels.

**Decision**
- requirements.txt: numpy constraint changed to numpy>=1.26,<2.5
  (keeps the lock file from drifting to a 3.12+-only release again)
- requirements.lock.txt: regenerated, numpy pinned to 2.4.6 (supports
  3.11 through 3.14)
- docs/team/onboarding.md: minimum Python version raised from 3.10 to
  3.11 to match what the dependency set can actually support

**Rationale**
Honesty over aspiration: keeping "3.10 or newer" documented while the
actual lock file silently required 3.12+ was a false promise. No team
member was confirmed to be actually running exactly 3.10, so raising
the floor to 3.11 costs nothing real while fixing a genuine, verified
incompatibility.

## DECISION: 2026-09-14 — Climate Strategy pillars are narrative, not tabular

**Context**
SRC-PLAN-005 pages 7-9 contain the strategy's 5 strategic pillars,
each with a "Strategic Focus" and a bulleted "Priority Interventions"
list. pdfplumber detects these as tables, but the underlying PDF uses
a two-column magazine-style layout - both table extraction and plain
text extraction interleave the two side-by-side columns, mixing one
pillar's content with its neighbour's mid-sentence.

**Decision**
This content will NOT be mechanically parsed into a CSV. It will be
cited as narrative content in the paper's background/context section
(the 5 pillar names and their strategic focus, read directly from the
source).

**Rationale**
A parser attempting to un-interleave two-column text carries a real,
material risk of misattributing one pillar's intervention to another
- silent fabrication of structure the source doesn't cleanly present.
Given the deadline, this risk is not worth taking for content that is
legitimately narrative in nature, not row-level project data like
CDF/Finance. This is a considered decision after direct inspection of
the real content, not a skipped step.

## DECISION: 2026-09-15 — Excluded independently-scraped dataset from final submission

**Context**
A separate CDF dataset (10 rows) was independently committed to main
past the deadline, citing bare-domain sources (Facebook page, news
site homepage, council homepage) rather than specific verifiable
page-level URLs, and carrying a scraped_date (2026-09-07) that
predates this project's actual start (2026-09-10) - unexplained.

**Decision**
This file is retained in git history (livingstone_city_council_dataset_team_completed_dataset/)
as evidence of effort, but is NOT used as the final CDF dataset for
Kaggle/paper submission. The canonical CDF dataset is
data/final/cdf_projects_clean.csv + data/final/cdf_news_derived.csv,
built through the project's established source-register, acquisition-
audit, and extraction pipeline, where every record traces to a
specific source_id and verifiable URL.

**Rationale**
Using unverifiable, non-traceable sources for the final submission
would directly contradict this project's own documented provenance
standard (source_register.csv, audit_acquired_sources.py, this
decision log). Some facts in the excluded file may be genuinely true
and valuable, but were not verified through our process in the
available time, so are not included rather than risk an unverifiable claim.
