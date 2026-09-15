"""
Adds the Integration and Validation pipeline steps (merge news
records, backfill enrichment, normalize status) as explicit notebook
cells, run in the correct order right after preprocessing. This makes
the notebook a complete, self-consistent, reproducible pipeline
regardless of how many times it's re-executed.
"""
import json
from pathlib import Path

def md(text): return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}
def code(text): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(keepends=True)}

nb_path = Path("notebooks/Livingstone_City_Council_Data_Mining_Notebook.ipynb")
nb = json.loads(nb_path.read_text())
cells = nb["cells"]

insert_idx = None
for i, c in enumerate(cells):
    if c["cell_type"] == "markdown" and "Version Control Evidence" in "".join(c["source"]):
        insert_idx = i
        break
assert insert_idx is not None, "Could not find Version Control Evidence cell"

new_cells = [
    md("""## 5b. Integration — Merging Additional Sources and Correcting Casing

Running extraction/cleaning/preprocessing from scratch (as demonstrated
above) reproduces the audited pipeline's base output, but two further
steps happened during this project's Phase 6/7 and must be re-applied
here so this notebook always ends in the actual submitted state:

1. 9 additional CDF records found via full newsletter reads (not
   captured by the automatic PDF-based extraction above) are merged in.
2. 2 of those records' contractor/beneficiary details, added after
   deeper reading of the source, are backfilled.
3. Project status casing is normalised to 4 consistent categories
   (a real inconsistency only surfaced by actually running this
   notebook end-to-end - see `docs/decisions/decision_log.md`)."""),
    code("""result = subprocess.run(
    [sys.executable, "src/preprocessing/merge_cdf_news_into_canonical.py"],
    cwd=REPO_ROOT, capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr)"""),
    code("""result = subprocess.run(
    [sys.executable, "src/preprocessing/backfill_cdf_enrichment.py"],
    cwd=REPO_ROOT, capture_output=True, text=True
)
print(result.stdout)"""),
    code("""result = subprocess.run(
    [sys.executable, "src/preprocessing/normalize_cdf_status.py"],
    cwd=REPO_ROOT, capture_output=True, text=True
)
print(result.stdout)"""),
    code("""# Reload and confirm final state
cdf = pd.read_csv(DATA_DIR / "db-unza26-csc4792-livingstone_city_council_cdf_projects.csv", sep="|")
print("Final CDF shape:", cdf.shape)
print(cdf["status"].value_counts())"""),
]

cells[insert_idx:insert_idx] = new_cells
nb_path.write_text(json.dumps(nb, indent=1))
print(f"Patched. Total cells now: {len(cells)}")
