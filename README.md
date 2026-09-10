# Livingstone City Council Data Mining and Warehousing

## CSC 4792 — Data Mining and Warehousing

### University of Zambia

This project develops a comprehensive, curated and reusable dataset containing important information associated with Livingstone City Council, Zambia.

## Council

**Livingstone City Council**

Official website: https://www.livingstonecouncil.gov.zm

## Objective

To identify, acquire, extract, clean, curate, preprocess and validate relevant data from the public digital footprint of Livingstone City Council.

## Data Domains

1. CDF projects
2. Revenue and budgets
3. Financial/LGEF information
4. Development and infrastructure

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
