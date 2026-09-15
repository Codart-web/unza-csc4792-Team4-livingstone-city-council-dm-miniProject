"""
Substantially expands the notebook to actually DEMONSTRATE extraction
and cleaning code running live, per the grading rubric: 40 marks on
"quality, efficiency, correctness of extraction/scraping scripts" and
"data cleaning and preprocessing steps" - both need to be shown
executing in the notebook, not just described in prose.
"""
import json
from pathlib import Path

def md(text): return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}
def code(text): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(keepends=True)}

nb_path = Path("notebooks/Livingstone_City_Council_Data_Mining_Notebook.ipynb")
nb = json.loads(nb_path.read_text())
cells = nb["cells"]

insert_at = 3

new_cells = []

new_cells.append(md("""## 3. Data Extraction — Live Demonstration

The cell below runs the actual extraction script
(`src/extraction/extract_cdf.py`) against a real acquired source PDF,
not a simplified re-implementation. This demonstrates the real
extraction logic: page-by-page text extraction with `pdfplumber`,
block-based parsing of numbered project entries, and validation
against an expected row count (the script raises an error if the
count doesn't match, rather than silently returning partial data)."""))

new_cells.append(code("""import subprocess, sys

result = subprocess.run(
    [sys.executable, "-m", "src.extraction.extract_cdf"],
    cwd=REPO_ROOT, capture_output=True, text=True
)
print("STDOUT:\\n", result.stdout)
if result.returncode != 0:
    print("STDERR:\\n", result.stderr)
print("Exit code:", result.returncode)"""))

new_cells.append(code("""# Show the extraction report - what succeeded, what was blocked, and why
import pandas as pd
extraction_report = pd.read_csv(REPO_ROOT / "data/interim/cdf_extraction_report.csv", sep="|")
extraction_report"""))

new_cells.append(md("""**Reading the extraction logic itself** (not just its output) — the
core parsing function, for review of extraction quality:"""))

new_cells.append(code("""extraction_source = (REPO_ROOT / "src/extraction/extract_cdf.py").read_text()
start = extraction_source.find("def extract_project_rows")
end = extraction_source.find("def extract_news_rows")
print(extraction_source[start:end])"""))

new_cells.append(md("""## 4. Data Cleaning and Preprocessing — Live Demonstration

Rather than only describing the cleaning steps in prose, this section
runs the actual cleaning script and shows a real before/after
comparison on one file, so the transformation is directly visible."""))

new_cells.append(code("""# BEFORE: raw interim data straight from extraction, uncleaned
raw_sample = pd.read_csv(REPO_ROOT / "data/interim/finance_budget_raw.csv", sep="|", nrows=5)
print("BEFORE cleaning (raw extraction output):")
raw_sample[["item_code", "budget_item", "approved_budget"]]"""))

new_cells.append(code("""# Run the actual cleaning script
result = subprocess.run(
    [sys.executable, "-m", "src.cleaning.clean_datasets"],
    cwd=REPO_ROOT, capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr)"""))

new_cells.append(code("""# AFTER: same rows, post-cleaning
clean_sample = pd.read_csv(
    REPO_ROOT / "data/final/db-unza26-csc4792-livingstone_city_council_finance_budget.csv",
    sep="|", nrows=5
)
print("AFTER cleaning:")
clean_sample[["item_code", "budget_item", "approved_budget"]]"""))

new_cells.append(md("""**The cleaning logic itself**, for review of correctness — note the
explicit rule that a value which isn't confidently numeric after
stripping thousands-separators is returned UNCHANGED, never guessed
at or coerced to zero:"""))

new_cells.append(code("""cleaning_source = (REPO_ROOT / "src/cleaning/clean_datasets.py").read_text()
start = cleaning_source.find("def clean_numeric")
end = cleaning_source.find("def clean_rows")
print(cleaning_source[start:end])"""))

new_cells.append(md("""## 5. Preprocessing — Standardisation Live Demonstration

Phase 5 preprocessing resolves category-spelling inconsistencies
(e.g. "Road Works" vs "Roads works") and splits free-text date ranges
into structured start/end dates. Run live below:"""))

new_cells.append(code("""result = subprocess.run(
    [sys.executable, "-m", "src.preprocessing.preprocess_cdf"],
    cwd=REPO_ROOT, capture_output=True, text=True
)
print(result.stdout)
result2 = subprocess.run(
    [sys.executable, "-m", "src.preprocessing.preprocess_finance"],
    cwd=REPO_ROOT, capture_output=True, text=True
)
print(result2.stdout)"""))

new_cells.append(md("""## 6. Version Control Evidence

This project's full history is tracked in Git, with per-domain
feature branches, a documented decision log, and a review process
that included independently re-verifying claimed data acquisitions
against live sources before merge. The commands below query the
actual repository history (not a description of it)."""))

new_cells.append(code("""result = subprocess.run(["git", "log", "--oneline"], cwd=REPO_ROOT, capture_output=True, text=True)
commits = result.stdout.strip().splitlines()
print(f"Total commits on main: {len(commits)}")
print("\\nMost recent 10:")
for c in commits[:10]:
    print(" ", c)"""))

new_cells.append(code("""result = subprocess.run(["git", "branch", "-a"], cwd=REPO_ROOT, capture_output=True, text=True)
print(result.stdout)"""))

cells[insert_at:insert_at] = new_cells

import re
for i in range(insert_at + len(new_cells), len(cells)):
    c = cells[i]
    if c["cell_type"] == "markdown":
        src = "".join(c["source"])
        m = re.match(r"## (\d+)\.", src)
        if m:
            old_num = int(m.group(1))
            new_num = old_num + 4
            new_src = re.sub(r"^## \d+\.", f"## {new_num}.", src, count=1)
            c["source"] = new_src.splitlines(keepends=True)

nb_path.write_text(json.dumps(nb, indent=1))
print(f"Patched. Total cells now: {len(cells)}")
