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
