# Livingstone City Council Data Mining and Warehousing

## CSC 4792 — Data Mining and Warehousing

### University of Zambia

This project develops a comprehensive, curated and reusable dataset containing important information associated with Livingstone City Council, Zambia.

## Council

**Livingstone City Council**

Official website: https://www.livingstonecouncil.gov.zm

## Objective

To identify, acquire, extract, clean, curate, preprocess and validate relevant data from the public digital footprint of Livingstone City Council.

## Final Dataset (Kaggle)

https://www.kaggle.com/datasets/sachynachy/livingstone-city-council-data

6 CSV files, 738 total records, every record traceable to a specific
source document and URL (see docs/source_register/source_register.csv).

## Data Domains

1. CDF projects (34 records)
2. Municipal finance: budget, performance, capital projects, debt/arrears (332 records)
3. Council Service Standards: 99 services, procedural steps and time standards (372 records)

Development/infrastructure and detailed governance data were assessed
but not included as row-level datasets in the final submission — see
docs/decisions/decision_log.md for the specific reasoning per source
(e.g. narrative content that risked misattribution if force-parsed,
scanned PDFs requiring OCR not implemented in the available time).

(Scope confirmed after source verification — see docs/decisions/decision_log.md)

## Data Pipeline

Source Discovery -> Source Acquisition -> Extraction -> Cleaning -> Preprocessing -> Integration -> Validation -> Final Dataset -> Documentation -> Publication

## Required Dataset Format

CSV files, `|` (pipe) as the field separator.

## Required Filename Convention

db-unza26-csc4792-[DESCRIPTION].csv

Example: db-unza26-csc4792-livingstone_city_council_cdf_projects.csv

## Repository Structure

data/ (raw, interim, final)
src/ (acquisition, extraction, cleaning, preprocessing, integration, validation, utils)
notebooks/
docs/
paper/
tests/

## Local environment setup

To reproduce the exact environment used to develop this project:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install --only-binary=:all: -r requirements.lock.txt

- requirements.txt       : human-readable dependency intent.
- requirements.lock.txt  : exact, byte-reproducible versions.

See docs/methodology/environment.md for the recorded interpreter,
lock-file fingerprint, and verification evidence.

## Team Workflow

Repository uses a feature-branch workflow. Nothing is committed directly to main.

- main -- stable, approved, always green
- feature/cdf -- CDF projects, beneficiaries, bursaries, grants, loans
- feature/finance -- budgets, revenue, LGEF, financial statements
- feature/planning -- IDP, infrastructure, schools, health, water, roads
- feature/governance -- minutes, WDC, consultations, newsletters, publications
- feature/integration -- cross-domain schema alignment and final datasets

### Member assignments

- Member 1 (Leader / Data Architect) -> feature/integration
- Member 2 (CDF / Project Data Lead) -> feature/cdf
- Member 3 (Finance / Revenue Data Lead) -> feature/finance
- Member 4 (Planning / Infrastructure Data Lead) -> feature/planning
- Member 5 (Governance / Quality Lead) -> feature/governance

### Workflow

1. git fetch origin; git checkout feature/<yours>
2. Work only on your branch. Never commit to main.
3. Commit with a meaningful prefix: feat:, fix:, docs:, test:, chore:, data:
4. git push origin feature/<yours>
5. Open a Pull Request into main.
6. The Group Leader reviews and merges.
