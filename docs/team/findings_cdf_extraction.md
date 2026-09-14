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

## OCR extraction completed

The previously blocked PDFs were recovered by installing Tesseract OCR and the relevant Python bridge (`pytesseract` and `pdf2image`), then extracting text from the image-based PDFs directly. The local preliminary outputs now include the recovered `SRC-CDF-013` and `SRC-CDF-022` records.

`SRC-CDF-022` (approved 2025 loans) and `SRC-CDF-013` (approved 2025 skills-development bursaries) were scanned PDFs in the current environment, but the OCR workflow succeeded and the data are now recorded locally in `data/interim/cdf_projects_raw.csv` and `data/interim/cdf_extraction_report.csv`.

The OCR run preserved the source provenance and marked the fields that are directly supported by the scanned table. For the bursaries, personal identifiers and addresses were excluded. Missing values remain blank and are not treated as zero.
