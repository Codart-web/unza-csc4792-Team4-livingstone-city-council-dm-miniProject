"""
Rebuild data/interim/cdf_news_derived.csv from scratch, cleanly, since
running extract_cdf_june_newsletter.py a second time (or twice in one
session) appended duplicate rows and doubled up an update note on the
Maramba sewer record.

This deletes the file and re-runs the three extraction scripts in
their correct dependency order:
  1. extract_cdf_news_facts.py       (creates the base 3 records)
  2. extract_cdf_march_newsletter.py (adds 6, enriches Maramba)
  3. extract_cdf_june_newsletter.py  (adds 3, enriches Maramba+Kalaluka)

Each script is idempotent-UNSAFE on its own (append-only), so this
script guarantees a clean single run of each, in order, from a blank
starting file.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

INTERIM = Path("data/interim/cdf_news_derived.csv")

SCRIPTS_IN_ORDER = [
    "src/acquisition/extract_cdf_news_facts.py",
    "src/acquisition/extract_cdf_march_newsletter.py",
    "src/acquisition/extract_cdf_june_newsletter.py",
]


def main() -> int:
    if INTERIM.exists():
        INTERIM.unlink()
        print(f"Deleted existing {INTERIM} to start clean.")

    for script in SCRIPTS_IN_ORDER:
        path = Path(script)
        if not path.exists():
            print(f"MISSING SCRIPT: {script} - cannot continue.")
            return 1
        print(f"\n===== Running {script} =====")
        result = subprocess.run([sys.executable, script], check=False)
        if result.returncode != 0:
            print(f"FAILED: {script} exited with {result.returncode}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
