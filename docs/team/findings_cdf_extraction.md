# CDF Phase 3 Extraction Findings

## Extraction command

```text
python -m src.extraction.extract_cdf
```

The script writes local preliminary outputs to `data/interim/cdf_projects_raw.csv` and `data/interim/cdf_extraction_report.csv`. These are extraction-stage outputs, not cleaned or final datasets.

## Successful extraction

`SRC-CDF-012` was parsed with `pdfplumber`. The source contains 22 approved 2024 community-project rows. The extracted fields are:

- `source_id`
- `cdf_year`
- `project_number`
- `project_description`
- `ward`
- `project_type`
- `project_cost`
- `status`
- `contractor`
- `source_page`
- `source_url`

The PDF does not provide project costs or contractors in the visible table, so those fields remain blank. The OCR text contains minor artefacts such as `lkm` and `l00001itre`; these are preserved at extraction stage and require documented cleaning later.

The three verified news-post records `SRC-CDF-038`, `SRC-CDF-039`, and `SRC-CDF-040` are extracted from their verified register notes because their raw HTML copies are not present locally. Their source IDs, URLs, costs, wards, progress/completion, and contractor where available are preserved. They are clearly identified as `webpage (news post)` sources rather than PDF records.

## OCR: dependencies added, extraction not yet implemented

`SRC-CDF-013` (approved 2025 skills-development bursaries) and `SRC-CDF-022`
(approved 2025 CDF loans) are scanned/image PDFs. `pytesseract` and
`pdf2image` are listed in `requirements.txt` for this purpose, but
`src/extraction/extract_cdf.py` has no OCR code path: both sources are
reported by the script itself as `blocked: scanned PDF`, and neither
`data/interim/cdf_projects_raw.csv` nor `data/interim/cdf_extraction_report.csv`
contains any record for them. Running `python -m src.extraction.extract_cdf`
produces exactly 25 rows (22 SRC-CDF-012 project rows + 3 news-post rows) -
confirmed by re-running the script directly.

A raw Tesseract text dump for each PDF was produced ad hoc while testing OCR
feasibility and is sitting locally (uncommitted, and excluded from Git by the
`data/interim/*` rule) at `data/interim/ocr/SRC-CDF-013_*.txt` and
`data/interim/ocr/SRC-CDF-022_*.txt`. The OCR text quality is poor in places
(e.g. garbled characters, misread digits) and, for the bursaries file
specifically, contains full student names and other personal identifiers that
would need explicit exclusion before any structured record is produced -
neither the dump-to-record parsing nor that exclusion logic has been written.
This paragraph previously (incorrectly) stated that OCR extraction was
complete and that personal identifiers had already been excluded; that was
not true and is corrected here. Turning these two sources into real rows
remains open work, to be picked up as a follow-up task rather than rushed
without review given the personal-data handling involved.
