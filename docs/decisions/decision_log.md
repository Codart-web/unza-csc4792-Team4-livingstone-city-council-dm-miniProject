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

## DECISION: 2026-09-14 — Standardised "Road Works"/"Roads works" to "Road works"

**Context**
Phase 5 preprocessing of the CDF projects dataset flagged that `project_type`
has three spellings for what reads as the same activity: "Road works" (8
rows), "Road Works" (1 row, SRC-CDF-012 project 3, Dr. Mubitana ward), and
"Roads works" (1 row, SRC-CDF-012 project 13, Mwalibonena ward). All three
are present in the source PDF itself, not introduced by extraction.

**Decision**
Read both affected rows' `project_description` values directly: project 3 is
"Road grading and gravelling of 5.5km of various roads" and project 13 is
"Road Grading and Gravelling of l.2km of roads in MA Zone" - both plainly the
same activity as the 8 rows already labelled "Road works". Both variants are
merged into the majority spelling "Road works" by
`src/preprocessing/preprocess_cdf.py`.

**Rationale**
This is a documented, source-verified merge of a spelling/capitalisation
inconsistency in the original document, not an inference about unknown data
- the underlying activity was independently confirmed from each row's own
description before merging, satisfying the "no unsupported assumptions"
rule.

## DECISION: 2026-09-14 — Left "Maramba" vs "Maramba (R Section)" ward names unmerged

**Context**
The CDF projects dataset has `ward="Maramba"` (SRC-CDF-012, from the 2024
approved-projects PDF) and `ward="Maramba (R Section)"` (SRC-CDF-038, a 2025
news-derived record). These may be the same ward with an added sub-area
qualifier, or genuinely different areas - this cannot be determined from the
two sources alone.

**Decision**
Both values are left exactly as extracted. No merge, no truncation of
"(R Section)". Flagged in `docs/team/findings_cdf_extraction.md` for Phase 6
Integration to resolve (e.g. against an authoritative ward list, if one
becomes available).

**Rationale**
Unlike the "Road works" case above, there is no independent evidence in
either source confirming these refer to the identical area - merging them
would be a guess, not a verified correction. Per the Phase 6 Integration
Rule: investigate, do not arbitrarily choose, and document unresolved
discrepancies rather than silently picking one.

## DECISION: 2026-09-14 — Removed Finance final CSVs mistakenly committed to feature/cdf

**Context**
Commit `dd010e9` ("Done with Phase 4 - Data Cleaning"), authored as
`MissTeeChipo <teechipo@gmail.com>`, added the four Finance final datasets
to this branch. `data/interim/` and `data/final/` are local filesystem
state, not branch-scoped, so leftover Finance output from earlier work in
the same working directory was picked up and committed here under the
Finance identity while `feature/cdf` was checked out.

**Decision**
The four Finance CSVs are removed from `feature/cdf` in the following
commit. They remain correctly committed on `feature/finance`.

**Rationale**
Keeping Member 3's output correctly attributed to Member 3's branch/account
matters for this assignment's per-member accountability, and the CDF branch
should only contain CDF-domain deliverables. No data was lost - the
authoritative copy exists on the correct branch.
