# Environment Specification

Recorded on **2026-09-10T12:12:41Z** (UTC) on the Group Leader's machine.

## Interpreter

- Python **3.14.4**
- pip **26.2.1**
- OS: Ubuntu 26.04 (`resolute`) under WSL

## Reproduction steps

Any team member or examiner can reproduce this environment with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install --only-binary=:all: -r requirements.lock.txt
```

Two files describe dependencies:

- `requirements.txt` — human-readable intent (loose `>=` pins).
- `requirements.lock.txt` — exact, byte-reproducible versions,
  including every transitive dependency. This is the file to use
  when reproducing the environment.

## Lock file fingerprint

```
sha256(requirements.lock.txt) = c36056b3e6877c7e1a7fccbba69d8279a766a8e1591c35b433e09b5e5b6d04ee
```

If the lock file is edited by hand, this fingerprint will change and
the change must be recorded in `docs/decisions/decision_log.md`.

## Verified install

- Installed via `pip install --only-binary=:all: -r requirements.txt`
  → exit code 0
- All 15 declared packages resolved to pre-built wheels for CPython
  3.14; no source builds.
- 14/14 import sanity probes succeeded (see `tests/test_environment.py`).

## Notable versions

- pandas **3.0.5** (major-version jump from 2.x; code should be
  written against pandas 3 behaviour)
- numpy **2.5.3**
- scikit-learn **1.9.0**
- lxml **6.1.3**
- pdfminer.six **20260107** (hard-pinned by pdfplumber 0.11.10)
- matplotlib **3.11.1**
