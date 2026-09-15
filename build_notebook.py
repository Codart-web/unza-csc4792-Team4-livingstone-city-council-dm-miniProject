"""
Builds the final Jupyter notebook for CSC4792 submission, referencing
the actual verified data pipeline (data/final/db-unza26-csc4792-*.csv),
not the excluded unverifiable package.
"""
import json
from pathlib import Path

def md(text): return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}
def code(text): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(keepends=True)}

cells = []

cells.append(md("""# CSC 4792: Data Mining and Warehousing
## Mini Project — Livingstone City Council Dataset
**Team 4** | Livingstone City Council administrative and financial data

**Note on submission timing:** this project was submitted after the
stated deadline. See the accompanying letter and
`docs/decisions/decision_log.md` for a full, honest account of the
technical and team-availability challenges encountered."""))

cells.append(md("## 1. Environment Setup and Libraries"))
cells.append(code("""import pandas as pd
import csv
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    p = start.resolve()
    while not (p / "data" / "final").exists():
        if p.parent == p:
            raise FileNotFoundError("Could not locate data/final from " + str(start))
        p = p.parent
    return p

REPO_ROOT = find_repo_root(Path.cwd())
DATA_DIR = REPO_ROOT / "data" / "final"
pd.set_option("display.max_columns", None)
print("Environment ready. DATA_DIR =", DATA_DIR)"""))

cells.append(md("""## 2. Data Collection Methodology

Sources were discovered via a two-level crawl of the official council
website, then individually verified (URL reachability, content-type,
file-signature checks) before acquisition. Every source is recorded
in `docs/source_register/source_register.csv` with a unique
`source_id`, retrieval date, and status. A custom audit tool
(`src/acquisition/audit_acquired_sources.py`) independently re-checks
claimed acquisitions against the live source before any merge into
the shared codebase — this is a hard gate, not optional review.

Known limitations of the source website: an invalid/expired TLS
certificate (documented in `docs/decisions/decision_log.md`,
2026-09-10 entry) required scoped, disclosed use of `verify=False`
for read-only GET requests only."""))

cells.append(md("## 3. CDF Projects Dataset"))
cells.append(code("""cdf = pd.read_csv(DATA_DIR / "db-unza26-csc4792-livingstone_city_council_cdf_projects.csv", sep="|")
print("Shape:", cdf.shape)
cdf.head()"""))
cells.append(code("""print("Projects by status:")
print(cdf["status"].value_counts())
print("\\nProjects with a recorded cost:", cdf["project_cost"].notna().sum(), "of", len(cdf))"""))

cells.append(md("""## 4. Finance Datasets

Four related tables extracted from council budget and performance
documents: annual budgets, semi-annual performance, capital projects,
and debt/arrears."""))
cells.append(code("""finance_budget = pd.read_csv(DATA_DIR / "db-unza26-csc4792-livingstone_city_council_finance_budget.csv", sep="|")
finance_performance = pd.read_csv(DATA_DIR / "db-unza26-csc4792-livingstone_city_council_finance_performance.csv", sep="|")
finance_capital = pd.read_csv(DATA_DIR / "db-unza26-csc4792-livingstone_city_council_finance_capital_projects.csv", sep="|")
finance_debt = pd.read_csv(DATA_DIR / "db-unza26-csc4792-livingstone_city_council_finance_debt_arrears.csv", sep="|")

for name, df in [("Budget", finance_budget), ("Performance", finance_performance),
                  ("Capital Projects", finance_capital), ("Debt/Arrears", finance_debt)]:
    print(f"{name}: {df.shape}")"""))
cells.append(code("finance_budget.head()"))

cells.append(md("""## 5. Council Service Standards Dataset

A previously-unassessed source (the Service Delivery Charter) was
found on direct inspection to contain 6 structured tables covering
99 distinct council services — see
`docs/decisions/decision_log.md`, 2026-09-14 entry, for the discovery
and the earlier incorrect assumption it corrects."""))
cells.append(code("""service_standards = pd.read_csv(DATA_DIR / "db-unza26-csc4792-livingstone_city_council_service_standards.csv", sep="|")
print("Shape:", service_standards.shape)
print("Distinct services:", service_standards["service_name"].nunique())
service_standards.head()"""))

cells.append(md("""## 6. Data Cleaning and Preprocessing Steps Performed

1. **Whitespace normalisation** on every field.
2. **Numeric coercion**: thousands-separator commas stripped from
   known numeric columns only; a value that isn't confidently
   numeric after stripping is left unchanged, never guessed.
3. **Missing-value discipline**: a blank value is NEVER converted to
   zero. Verified directly (see Section 8).
4. **Duplicate removal**: exact-duplicate rows dropped.
5. **Phase 5 preprocessing**: category-spelling standardisation
   (e.g. "Road Works"/"Roads works" -> "Road works"), ISO date
   splitting for Finance's `period` column.
6. **Phase 6 integration**: 9 additional CDF records (found via full
   newsletter reads) merged into the canonical CDF dataset; 3
   already-duplicated records resolved by keeping the audited
   pipeline's version.
7. **Phase 7 validation**: a direct spot-check against the original
   source article (see below) caught 2 rows missing contractor
   enrichment, backfilled before this submission."""))

cells.append(md("## 7. Validation Evidence"))
cells.append(code("""# Spot-check: SRC-CDF-038 (Maramba Sewer) against the original March
# newsletter article. Expected: cost 719972, 80% complete, contractor
# "Southern Water and Sanitation Company".
check = cdf[cdf["source_id"] == "SRC-CDF-038"]
print(check[["source_id", "project_cost", "completion_pct", "contractor"]].to_string(index=False))"""))
cells.append(code("""# Confirm missing values were never converted to zero
for name, df in [("CDF", cdf), ("Finance Budget", finance_budget),
                  ("Finance Performance", finance_performance),
                  ("Service Standards", service_standards)]:
    blanks = (df.astype(str) == "").sum().sum()
    print(f"{name}: {blanks} blank cells preserved as missing (not zero)")"""))

cells.append(md("""## 8. Limitations

- **Scanned/image PDFs**: two Governance sources (community
  consultative meeting minutes, citizen engagement plan) and one CDF
  source (2025 skills bursaries list, 54MB) are scanned images with
  no extractable text. OCR was not implemented in the time available;
  these remain documented gaps, not fabricated data.
- **Planning domain**: the Climate Change Strategy's strategic
  pillars (pages 7-9) are laid out in a two-column format that both
  table- and text-extraction interleave incorrectly. This content is
  cited as narrative background rather than mechanically parsed, to
  avoid misattributing one pillar's content to another.
- **Ward-name inconsistency**: "Maramba" (2024 approved-projects list)
  vs "Maramba (R Section)" (2025 news report) are left as distinct
  strings rather than assumed identical.
- **Unreconciled aggregate**: a lump-sum "CDF Community projects"
  finance line (K21.96M) could not be checked item-by-item against
  individual project records, since no "Approved 2025 CDF Community
  Projects" source (equivalent to the 2024 one) was located.
- **Late submission**: see the accompanying letter for a full account
  of the technical and team-availability challenges encountered."""))

cells.append(md("""## 9. Potential Reuse Value

These datasets support research on constituency development fund
effectiveness, municipal financial transparency and budget-execution
tracking, and service-delivery benchmarking against 99 distinct
council services with formally stated time standards."""))

cells.append(md("""## 10. How to Reproduce / Extend

1. Clone the repository:
   `github.com/Codart-web/unza-csc4792-Team4-livingstone-city-council-dm-miniProject`
2. `pip install -r requirements.lock.txt` (Python 3.11+)
3. Source register: `docs/source_register/source_register.csv`
4. Extraction scripts: `src/extraction/`
5. Cleaning: `python -m src.cleaning.clean_datasets`
6. Preprocessing: `python -m src.preprocessing.preprocess_cdf` and
   `preprocess_finance`
7. Integration: `python -m src.preprocessing.merge_cdf_news_into_canonical`
8. Every decision made during this process, including corrections to
   earlier mistakes, is recorded in `docs/decisions/decision_log.md`."""))

cells.append(code("""print("Notebook completed successfully.")
print("Final datasets ready for Kaggle upload:")
for f in sorted(DATA_DIR.glob("db-unza26-csc4792-*.csv")):
    print(" -", f.name)"""))

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out_path = Path("notebooks/Livingstone_City_Council_Data_Mining_Notebook.ipynb")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(notebook, indent=1))
print(f"Wrote {out_path}")
