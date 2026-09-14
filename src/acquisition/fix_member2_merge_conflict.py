"""
Fix Member 2's committed merge conflict in for_member_2.csv.

What happened: Member 2 pulled main, hit a real merge conflict (both
sides had edited the same 37 rows independently), and committed the
file WITHOUT resolving it - leaving literal <<<<<<< / ======= / >>>>>>>
markers baked into the CSV.

This script:
1. Reads the conflicted file (with markers).
2. Parses the HEAD side (Member 2's real verification work - quoted,
   comma-adjacent format) and normalizes it: strips quotes, fixes
   responsible_member to "Member 2" (consistent with every other row
   in the register - all 110+ other rows use "Member N"/"LEADER", not
   real names), lowercases status values to match convention.
3. Parses the incoming side for the 3 CDF news-derived rows
   (SRC-CDF-038/039/040) that Member 2's side is missing entirely.
4. Writes a clean, corrected for_member_2.csv: 37 normalized rows +
   3 news rows = 40 total (matching the pre-conflict row count).
5. Applies the same corrected rows into the master source_register.csv.

Does NOT change any status value Member 2 set (verified/inaccessible/
rejected) - only fixes formatting/corruption, per the rule that a
member's actual judgement calls are not silently overridden.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

CONFLICTED = Path("/tmp/member2_remote.csv")
FOR_MEMBER_2 = Path("docs/source_register/for_member_2.csv")
MASTER = Path("docs/source_register/source_register.csv")

FIELDNAMES = ["source_id", "source_title", "source_type", "year", "data_domain",
              "url", "retrieval_date", "responsible_member", "extraction_method",
              "status", "notes"]

NEWS_IDS = {"SRC-CDF-038", "SRC-CDF-039", "SRC-CDF-040"}


def split_conflict(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    head_start = next(i for i, l in enumerate(lines) if l.startswith("<<<<<<<"))
    sep = next(i for i, l in enumerate(lines) if l.startswith("======="))
    tail_end = next(i for i, l in enumerate(lines) if l.startswith(">>>>>>>"))
    head_block = "\n".join(lines[head_start + 1:sep])
    incoming_block = "\n".join(lines[sep + 1:tail_end])
    return head_block, incoming_block


def parse_head(head_block: str) -> list[dict]:
    reader = csv.reader(io.StringIO(head_block), delimiter="|", quotechar='"')
    rows = list(reader)
    header, data_rows = rows[0], rows[1:]
    out = []
    for r in data_rows:
        d = dict(zip(header, r))
        d["responsible_member"] = "Member 2"
        d["status"] = d["status"].strip().lower()
        out.append({k: d.get(k, "") for k in FIELDNAMES})
    return out


def parse_incoming_news_rows(incoming_block: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(incoming_block), delimiter="|")
    return [r for r in reader if r["source_id"] in NEWS_IDS]


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter="|")
        w.writeheader()
        w.writerows(rows)


def update_master(fixed_rows: list[dict]) -> None:
    by_id = {r["source_id"]: r for r in fixed_rows}
    with MASTER.open("r", encoding="utf-8", newline="") as f:
        master_rows = list(csv.DictReader(f, delimiter="|"))
        fieldnames = list(master_rows[0].keys())

    updated = 0
    for r in master_rows:
        if r["source_id"] in by_id:
            fixed = by_id[r["source_id"]]
            r["responsible_member"] = fixed["responsible_member"]
            r["status"] = fixed["status"]
            r["notes"] = fixed["notes"]
            updated += 1

    with MASTER.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        w.writeheader()
        w.writerows(master_rows)
    print(f"Updated {updated} matching rows in {MASTER}")


def main() -> None:
    text = CONFLICTED.read_text(encoding="utf-8")
    head_block, incoming_block = split_conflict(text)

    member2_rows = parse_head(head_block)
    news_rows = parse_incoming_news_rows(incoming_block)

    all_rows = member2_rows + news_rows
    print(f"Member 2's own rows (normalized): {len(member2_rows)}")
    print(f"News-derived rows merged in: {len(news_rows)}")
    print(f"Total rows in fixed file: {len(all_rows)}")

    write_csv(FOR_MEMBER_2, all_rows)
    print(f"Wrote clean file: {FOR_MEMBER_2}")

    update_master(all_rows)

    print("\nStatus breakdown:")
    counts = {}
    for r in all_rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    for s, n in sorted(counts.items()):
        print(f"  {s:14s} {n}")


if __name__ == "__main__":
    main()
