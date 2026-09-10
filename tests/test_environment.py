"""
Environment verification tests.

Purpose
-------
Prove that the repository's declared environment is importable and
self-consistent. These tests must pass on any machine that has
installed from requirements.lock.txt inside a fresh .venv.

They intentionally:
- do not touch the network,
- do not touch data/ directories,
- do not depend on the time of day.
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_TXT = REPO_ROOT / "requirements.txt"
REQUIREMENTS_LOCK = REPO_ROOT / "requirements.lock.txt"

# The 15 packages declared in requirements.txt.
# Some PyPI names differ from their import names; we map explicitly.
DECLARED_PACKAGES = [
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("requests", "requests"),
    ("beautifulsoup4", "bs4"),
    ("lxml", "lxml"),
    ("openpyxl", "openpyxl"),
    ("pdfplumber", "pdfplumber"),
    ("pypdf", "pypdf"),
    ("jupyter", "jupyter"),
    ("notebook", "notebook"),
    ("matplotlib", "matplotlib"),
    ("scikit-learn", "sklearn"),
    ("pytest", "pytest"),
    ("python-dotenv", "dotenv"),
    ("tqdm", "tqdm"),
]


def test_python_version_is_supported() -> None:
    # We validate on 3.14; refuse anything older than 3.10 to catch
    # accidental use of a stale system interpreter.
    assert sys.version_info >= (3, 10), (
        f"Python 3.10+ required; found {sys.version.split()[0]}"
    )


@pytest.mark.parametrize("pypi_name, import_name", DECLARED_PACKAGES)
def test_declared_package_imports(pypi_name: str, import_name: str) -> None:
    try:
        importlib.import_module(import_name)
    except Exception as exc:  # pragma: no cover - only on real failure
        pytest.fail(f"Failed to import {import_name} ({pypi_name}): {exc!r}")


def test_requirements_txt_exists() -> None:
    assert REQUIREMENTS_TXT.is_file(), "requirements.txt missing"


def test_lock_file_exists_and_is_nonempty() -> None:
    assert REQUIREMENTS_LOCK.is_file(), "requirements.lock.txt missing"
    text = REQUIREMENTS_LOCK.read_text(encoding="utf-8").strip()
    assert text, "requirements.lock.txt is empty"
    # A lock file should have at least as many lines as declared packages.
    lines = [ln for ln in text.splitlines() if ln.strip()]
    assert len(lines) >= len(DECLARED_PACKAGES), (
        f"Lock file has only {len(lines)} entries; expected at least "
        f"{len(DECLARED_PACKAGES)}."
    )


def _normalise(name: str) -> str:
    # PyPI canonical form: lowercase, runs of [-_.] -> single '-'.
    return re.sub(r"[-_.]+", "-", name).lower()


def test_every_declared_package_is_pinned_in_lock_file() -> None:
    locked = {
        _normalise(line.split("==", 1)[0])
        for line in REQUIREMENTS_LOCK.read_text(encoding="utf-8").splitlines()
        if "==" in line
    }
    missing = [
        pypi for pypi, _ in DECLARED_PACKAGES if _normalise(pypi) not in locked
    ]
    assert not missing, f"Declared packages missing from lock file: {missing}"
