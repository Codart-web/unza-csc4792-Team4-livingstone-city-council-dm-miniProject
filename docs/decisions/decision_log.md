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

