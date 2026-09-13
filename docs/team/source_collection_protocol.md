# Source Collection Protocol

## Objective

Build an evidence base for the Livingstone City Council dataset.

## Procedure

For every source:

1. Identify the official source.
2. Record the URL.
3. Record the source title.
4. Record publication/year information where available.
5. Assign a source ID.
6. Identify the relevant data domain.
7. Record the responsible member.
8. Record the extraction method.
9. Acquire the source where appropriate.
10. Preserve provenance.
11. Do not enter extracted values into final datasets until reviewed.

## Evidence Rule

Never invent a value because a field appears useful.

If information is unavailable:

- leave it missing;
- document the limitation; or
- exclude the field.

## Conflict Rule

If two official sources disagree:

- do not silently choose one;
- record both sources;
- investigate the discrepancy;
- document the resolution in the decision log.

## PR Merge Gate — Acquisition Audit (added 2026-09-12)

Before merging any PR that changes a source_register CSV's status to
"acquired", the reviewer MUST run:

    python3 src/acquisition/audit_acquired_sources.py <path-to-their-csv> --all

All rows must PASS. If any FAIL, do not merge - return the PR to the
submitter with the specific failing source_id(s) and ask them to
re-verify or correct the status.

Rationale: data/raw/ is gitignored by design, so a PR's diff never
shows the actual acquired file - only the CSV status change. This
audit closes that gap by independently re-checking the live source,
rather than trusting the status column on faith.
