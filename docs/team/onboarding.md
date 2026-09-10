# Team Onboarding - CSC 4792 Team 4 Livingstone

Welcome. Read this file end to end before doing anything else.

## Read in this order

1. README.md - project overview, pipeline, and team workflow
2. docs/methodology/environment.md - environment setup and versions
3. docs/source_register/source_register_guide.md - how to register a source
4. docs/team/source_collection_protocol.md - the collection rule
5. docs/quality/source_quality_checklist.md - per-source quality gate

## One-time setup (run once)

    git clone git@github.com:Codart-web/unza-csc4792-Team4-livingstone-city-council-dm-miniProject.git
    cd unza-csc4792-Team4-livingstone-city-council-dm-miniProject
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install --only-binary=:all: -r requirements.lock.txt
    python -m pytest -q

Expected: 23 passed. If it does not pass, stop and report to the Group Leader before proceeding.

## Switch to your branch

    git fetch origin
    git checkout feature/<yours>

Branch to member assignment (see README Team Workflow for the same list):

- Member 1 (Leader / Data Architect)  -> feature/integration
- Member 2 (CDF / Project Data Lead)  -> feature/cdf
- Member 3 (Finance / Revenue Data)   -> feature/finance
- Member 4 (Planning / Infrastructure) -> feature/planning
- Member 5 (Governance / Quality)     -> feature/governance

## Working rules

- Never commit to main.
- Never touch another member branch.
- Never commit files under data/raw/ or data/interim/ - they are gitignored by design.
- Register every source in docs/source_register/source_register.csv before extracting from it.
- Log every source conflict in docs/decisions/decision_log.md before resolving.
- Never invent or estimate values. If a value is unavailable, leave it missing.
- Commit prefixes: feat: / fix: / docs: / test: / chore: / data:

## Before you push

    python -m pytest -q
    git status

Then commit, push, and open a Pull Request into main. The Group Leader reviews and merges.

## If something breaks

Report the exact error output to the Group Leader. Do not work around it silently. Do not delete the venv and start over unless told to.
