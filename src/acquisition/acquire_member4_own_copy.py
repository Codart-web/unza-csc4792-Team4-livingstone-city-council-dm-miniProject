"""
Download the 5 already-verified Member 4 planning PDFs directly onto
this machine. Bypasses the "verified" status filter, since these rows
were already advanced to "acquired" when the Leader completed this
domain earlier - the register is correct, this just gets a personal
copy onto Member 4's own machine too.
"""
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {"User-Agent": "CSC4792-Livingstone-Research/1.0"}
TIMEOUT = 180

FILES = [
    ("SRC-PLAN-001", "http://www.livingstonecouncil.gov.zm/wp-content/uploads/2023/08/LStone-IDP-2021-2031-7.8.23.pdf"),
    ("SRC-PLAN-002", "http://www.livingstonecouncil.gov.zm/wp-content/uploads/2023/12/Environmetal-Mangement-Act-12-of-2011-1.pdf"),
    ("SRC-PLAN-003", "http://www.livingstonecouncil.gov.zm/wp-content/uploads/2023/12/The-Urban-and-Regional-Planning-Act-2015.pdf"),
    ("SRC-PLAN-004", "http://www.livingstonecouncil.gov.zm/wp-content/uploads/2023/12/The-Zambia-National-Public-Health-Institute-Act-No.-19-of-2020pdf.pdf"),
    ("SRC-PLAN-005", "http://www.livingstonecouncil.gov.zm/wp-content/uploads/2026/01/Livingstone-City-Climate-Change-and-Resilience-Strategy.pdf"),
]

OUT_DIR = Path("data/raw/pdf")
OUT_DIR.mkdir(parents=True, exist_ok=True)

for source_id, url in FILES:
    print(f"{source_id} - {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False, stream=True)
        resp.raise_for_status()
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")
        continue
    name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(urlparse(url).path).name)
    out_path = OUT_DIR / f"{source_id}_{name}"
    with out_path.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=1 << 16):
            f.write(chunk)
    print(f"  Saved {out_path.stat().st_size:,} bytes -> {out_path}")
    time.sleep(0.5)

print("\nDone.")
