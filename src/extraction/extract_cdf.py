"""Extract preliminary CDF project records with source-level provenance."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pdfplumber

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER = REPO_ROOT / "docs" / "source_register" / "for_member_2.csv"
RAW_PDF = REPO_ROOT / "data" / "raw" / "pdf" / "SRC-CDF-012_approved-2024-cdf-community-projects.pdf"
PROJECT_OUTPUT = REPO_ROOT / "data" / "interim" / "cdf_projects_raw.csv"
REPORT_OUTPUT = REPO_ROOT / "data" / "interim" / "cdf_extraction_report.csv"

PROJECT_FIELDS = [
    "source_id", "cdf_year", "project_number", "project_description", "ward",
    "project_type", "project_cost", "status", "contractor", "source_page", "source_url",
]
REPORT_FIELDS = ["source_id", "source_title", "source_type", "status", "extraction_result", "notes"]


def read_register() -> dict[str, dict[str, str]]:
    with REGISTER.open(encoding="utf-8", newline="") as handle:
        return {row["source_id"]: row for row in csv.DictReader(handle, delimiter="|")}


def extract_project_rows() -> list[dict[str, str]]:
    with pdfplumber.open(RAW_PDF) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    text = text.replace("\r", "")
    start = re.compile(r"^\s*(?P<number>[0-9IlrtJ]{1,3})\s+(?P<body>.*)$")
    ward_names = ["Akapelwa", "Dambwa Central", "Dr. Mubitana", "Freedom", "Kabila", "Kariba", "Kasiya", "Libuyu", "Lizuma", "Maramba", "Mosi-oa-tunya", "Mulungushi", "Mwalibonena", "Namatama", "Nakatindi", "Nansanzu", "Simatobolo", "Shungu", "Simonga", "Zambezi", "LCC", "Ministry of Health"]
    project_types = ["Solar Powered boreholes", "Solar streetlights", "Water reticulation", "Supply and delivery", "Drainage construction", "Road works", "Road Works", "Roads works", "Construction", "Renovation"]
    blocks: list[tuple[str, list[str]]] = []
    current_number = ""
    current_lines: list[str] = []
    for line in text.splitlines():
        match = start.match(line)
        if match and not re.match(r"(?:Construction|Road|Drilling|Installation|Rehabilitation|Supply)", match.group("body"), re.IGNORECASE):
            match = None
        if match:
            if current_lines:
                blocks.append((current_number, current_lines))
            current_number = match.group("number")
            current_lines = [match.group("body")]
        elif current_lines:
            current_lines.append(line)
    if current_lines:
        blocks.append((current_number, current_lines))
    rows = []
    for row_number, (_raw_number, raw_lines) in enumerate(blocks, start=1):
        number = str(row_number)
        first_line = " ".join(raw_lines[0].split())
        project_type = next((value for value in project_types if first_line.endswith(value)), "")
        if not project_type:
            continue
        first_line = first_line[: -len(project_type)].strip(" .")
        ward = next((value for value in ward_names if first_line.endswith(value)), "")
        if not ward:
            continue
        description = " ".join([first_line[: -len(ward)].strip(" ."), *raw_lines[1:]]).strip(" .")
        description = " ".join(description.split())
        rows.append({
            "source_id": "SRC-CDF-012",
            "cdf_year": "2024",
            "project_number": number,
            "project_description": description,
            "ward": ward,
            "project_type": project_type,
            "project_cost": "",
            "status": "approved",
            "contractor": "",
            "source_page": "1-2",
            "source_url": read_register()["SRC-CDF-012"]["url"],
        })
    if len(rows) != 22:
        raise ValueError(f"Expected 22 project rows from SRC-CDF-012, extracted {len(rows)}")
    return rows


def extract_news_rows(register: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for source_id in ("SRC-CDF-038", "SRC-CDF-039", "SRC-CDF-040"):
        row = register[source_id]
        note = row["notes"]
        cost = re.search(r"Cost K([0-9,]+(?:\.[0-9]+)?)", note)
        completion = re.search(r"([0-9]+)% complete", note)
        ward = re.search(r"Ward: ([^.]+)", note)
        contractor = re.search(r"Contractor: ([^.]+)", note)
        rows.append({
            "source_id": source_id,
            "cdf_year": "2025",
            "project_number": "",
            "project_description": row["source_title"].replace(" (news report)", ""),
            "ward": ward.group(1).strip() if ward else "",
            "project_type": "",
            "project_cost": cost.group(1).replace(",", "") if cost else "",
            "status": "completed" if "Completed" in note else "in progress",
            "contractor": contractor.group(1).strip() if contractor else "",
            "source_page": "",
            "source_url": row["url"],
        })
        if completion:
            rows[-1]["status"] = f"{completion.group(1)}% complete"
    return rows


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="|")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    register = read_register()
    project_rows = extract_project_rows()
    news_rows = extract_news_rows(register)
    write_csv(PROJECT_OUTPUT, PROJECT_FIELDS, project_rows + news_rows)

    report = []
    for source_id in ("SRC-CDF-012", "SRC-CDF-038", "SRC-CDF-039", "SRC-CDF-040"):
        source = register[source_id]
        report.append({"source_id": source_id, "source_title": source["source_title"], "source_type": source["source_type"], "status": source["status"], "extraction_result": "records extracted", "notes": "Project rows written with source provenance."})
    for source_id in ("SRC-CDF-013", "SRC-CDF-022"):
        source = register[source_id]
        report.append({"source_id": source_id, "source_title": source["source_title"], "source_type": source["source_type"], "status": source["status"], "extraction_result": "blocked: scanned PDF", "notes": "No OCR dependency is installed; do not hand-type records. Extract after OCR/manual workflow is approved."})
    write_csv(REPORT_OUTPUT, REPORT_FIELDS, report)
    print(f"projects extracted: {len(project_rows)}")
    print(f"news records extracted: {len(news_rows)}")
    print(f"output: {PROJECT_OUTPUT.relative_to(REPO_ROOT)}")
    print(f"report: {REPORT_OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
