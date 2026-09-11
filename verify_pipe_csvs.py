"""
Verify every source_register CSV in the repo is valid pipe-delimited
data, regardless of what GitHub's comma-sniffing preview claims.

Checks, per file:
  1. Every row has the same number of fields as the header, when
     split on '|' (the actual, correct delimiter for this project).
  2. Reports which rows contain a literal comma in any field -- this
     is exactly what confuses GitHub's browser preview, but is
     harmless to real pipe-delimited parsing.
  3. Confirms the file loads cleanly with pandas using sep="|".

Run from the repo root:
    python3 verify_pipe_csvs.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
REGISTER_DIR = REPO_ROOT / "docs" / "source_register"

FILES_TO_CHECK = [
    "source_register.csv",
    "for_member_2.csv",
    "for_member_3.csv",
    "for_member_4.csv",
    "for_member_5.csv",
    "for_leader.csv",
    "recon_2026-09-10.csv",
    "recon_depth2_2026-09-10.csv",
]


def check_file(path: Path) -> bool:
    if not path.exists():
        print(f"  MISSING: {path.name}")
        return False

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="|")
        rows = list(reader)

    if not rows:
        print(f"  EMPTY: {path.name}")
        return False

    header = rows[0]
    ncols = len(header)
    bad_rows = []
    comma_rows = []

    for i, row in enumerate(rows[1:], start=2):  # line 2 = first data row
        if len(row) != ncols:
            bad_rows.append((i, len(row), row))
        if any("," in field for field in row):
            comma_rows.append(i)

    ok = not bad_rows
    status = "OK" if ok else "STRUCTURE PROBLEM"
    print(f"  {path.name}: {len(rows)-1} data rows, {ncols} columns -> {status}")

    if bad_rows:
        print("    Rows with wrong field count when split on '|':")
        for line_no, n, row in bad_rows:
            print(f"      line {line_no}: expected {ncols} fields, got {n} -> {row}")

    if comma_rows:
        print(f"    Rows containing a literal comma in some field "
              f"(harmless for '|' parsing, but this is what makes GitHub's "
              f"comma-based preview misreport column counts): lines {comma_rows}")

    return ok


def check_with_pandas(path: Path) -> None:
    try:
        import pandas as pd
    except ImportError:
        print("    (pandas not installed - skipping pandas load check)")
        return
    try:
        df = pd.read_csv(path, sep="|")
        print(f"    pandas.read_csv(sep='|') -> OK, shape={df.shape}")
    except Exception as e:
        print(f"    pandas.read_csv(sep='|') -> FAILED: {e}")


def main() -> int:
    print(f"Checking pipe-delimited CSVs in {REGISTER_DIR}\n")
    all_ok = True
    for name in FILES_TO_CHECK:
        path = REGISTER_DIR / name
        ok = check_file(path)
        if path.exists():
            check_with_pandas(path)
        print()
        all_ok = all_ok and ok

    if all_ok:
        print("ALL FILES STRUCTURALLY VALID as pipe-delimited CSV.")
        print("Any 'wrong column count' banner shown by GitHub's web preview")
        print("is caused by GitHub assuming comma-delimiting and getting")
        print("confused by literal commas inside a few source titles. It is")
        print("cosmetic only and does not affect actual parsing.")
        return 0
    else:
        print("STRUCTURAL PROBLEMS FOUND -- see details above. Fix before")
        print("relying on these files downstream.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
