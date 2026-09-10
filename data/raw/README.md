# Raw Acquired Source Material — LOCAL ONLY

This directory holds unmodified, as-acquired source material from
public Livingstone City Council digital sources: web pages, PDFs,
CSVs, and other files.

## Policy

Contents of `data/raw/` are **excluded from Git** (see `.gitignore`).
Only this README and the `.gitkeep` placeholders inside each sub-
directory are tracked.

Rationale:
- size,
- third-party copyright,
- reproducibility is preserved via `docs/source_register/source_register.csv`
  and `src/acquisition/download_source.py`.

## Sub-directories

- `web/`  — HTML pages, saved web pages
- `pdf/`  — council PDFs, reports, budgets, minutes
- `csv/`  — CSV/XLSX files served by the council
- `other/` — anything else (images, docx, etc.)

## Rule

Never clean or modify files in this directory.
Cleaning happens in `src/cleaning/`, producing outputs in
`data/interim/` and finally `data/final/`.
