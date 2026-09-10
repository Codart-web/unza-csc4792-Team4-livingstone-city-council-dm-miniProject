# Team Onboarding - CSC 4792 Team 4 - Livingstone City Council

Deadline: Saturday 12 September 2026, 23:59 GMT+2.
Read this file end to end before running anything.

---

## 1. What we are building (30 seconds)

A curated, documented, multi-source dataset about Livingstone City Council,
delivered as (a) a Kaggle dataset, (b) a Jupyter notebook plus codebase on
GitHub, and (c) a Data in Brief paper. Every value must be traceable to a
public council source. See README.md for the full picture.

---

## 2. Prerequisites before you start

You must have:

- A computer with WSL (Windows) or macOS/Linux
- Git installed
- Python 3.10 or newer
- An SSH key registered with GitHub
- Been added as a collaborator on the repo (the Leader confirms this)

If you do not have an SSH key on GitHub, ask the Leader first.
Do NOT continue until git clone works.

---

## 3. Step 1 - Verify SSH access to GitHub

Run:

    ssh -T git@github.com

Expected (wording varies):

    Hi <your-github-username>! You have successfully authenticated...

If you see permission denied, your SSH key is not set up. Stop and ask.

---

## 4. Step 2 - Clone the repository

    cd ~
    git clone git@github.com:Codart-web/unza-csc4792-Team4-livingstone-city-council-dm-miniProject.git
    cd unza-csc4792-Team4-livingstone-city-council-dm-miniProject

Expected: a new directory is created and Git reports success.

---

## 5. Step 3 - Create the virtual environment

    python3 -m venv .venv
    source .venv/bin/activate

Expected: prompt changes to start with (.venv).

Confirm with:

    which python

Expected: path ends in .venv/bin/python.

---

## 6. Step 4 - Install dependencies (locked, exact versions)

    python -m pip install --upgrade pip setuptools wheel
    python -m pip install --only-binary=:all: -r requirements.lock.txt

Expected: many Downloading / Installing lines, then Successfully installed.
The install may take 5 to 10 minutes the first time.
scipy is the largest single download (about 35 MB).

---

## 7. Step 5 - Verify the environment (MANDATORY)

    python -m pytest -q

Expected output:

    23 passed in X.XXs

If you do not see 23 passed, STOP. Do not proceed.
Report the exact error to the Leader.

---

## 8. Step 6 - Switch to your branch

    git fetch origin
    git checkout feature/<your-assigned-branch>

Replace <your-assigned-branch> with your branch from this table:

| Member | Role | Branch |
|--------|------|--------|
| 1 | Leader / Data Architect | feature/integration |
| 2 | CDF / Project Data Lead | feature/cdf |
| 3 | Finance / Revenue Data Lead | feature/finance |
| 4 | Planning / Infrastructure Data Lead | feature/planning |
| 5 | Governance / Quality Lead | feature/governance |

Expected: Switched to branch feature/... or Already on feature/...

---

## 9. Step 7 - Confirm you are on the correct commit

    git log --oneline -3

The top line MUST be:

    02082da docs: add member onboarding guide for team branches

If the top line differs, run git pull and check again. If it still
differs, report to the Leader.

---

## 10. Step 8 - Report back to the Leader

Send the Leader these three outputs, verbatim:

1. python -m pytest -q          -> expect the 23 passed line
2. git branch --show-current    -> expect your feature branch name
3. git status                   -> expect nothing to commit, clean

The Leader verifies your setup before assigning your first task.

---

## 11. Working rules (non-negotiable)

- NEVER commit to main. Only the Leader merges into main.
- NEVER push to another member branch.
- NEVER commit files under data/raw/ or data/interim/ - they are gitignored by design.
- Register every source in docs/source_register/source_register.csv BEFORE extracting from it.
- Log every source conflict in docs/decisions/decision_log.md BEFORE resolving it.
- NEVER invent, estimate, or copy values. If a value is unavailable, leave it missing.
- Commit prefixes: feat: / fix: / docs: / test: / chore: / data:

---

## 12. Before every push

    python -m pytest -q
    git status

Only push when tests pass and status is clean. Then:

    git push origin feature/<yours>

Then open a Pull Request into main on GitHub.
Assign the Leader as reviewer.
The Leader reviews, requests changes if needed, and merges.

---

## 13. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Permission denied (publickey) | SSH key not set up | Ask Leader; add key to GitHub |
| ensurepip missing on venv | python3-venv not installed | sudo apt install python3-venv |
| pip install fails midway | network drop | rerun the pip install command |
| pytest reports fewer than 23 passed | wrong branch or stale env | git pull; check branch; reinstall from lock file |
| activate: No such file | venv was not created | rerun Step 3 |
| git status ignores your new file | file under gitignored path | confirm path is not data/raw/ or data/interim/ |

---

## 14. What NOT to do until the Leader says GO

- Do NOT scrape the council website yet.
- Do NOT add sources to the register yet.
- Do NOT create new branches.
- Do NOT modify .gitignore, requirements.txt, or requirements.lock.txt.
- Do NOT push anything to main.

Your first task is only: get set up, run pytest, report back.
The Leader sends the Phase 1 kickoff separately.

---

## 15. Escalation

If anything is unclear, or any command fails, or any output surprises you:
paste the exact terminal output to the Leader. Never guess. Never silently
work around. We are on a 2-day clock and miscommunication costs more than
slowness.
