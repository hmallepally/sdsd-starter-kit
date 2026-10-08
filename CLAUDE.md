# Claude Code Guide: Spec-Driven Secure Development (SDSD) Starter Kit

## Core Architecture
This repository implements Spec-Driven Secure Development (SDSD) where:
- Specifications (`specs/`) are the immutable source of truth.
- Source code (`src/`) is ephemeral, disposable compiled output.
- All tasks follow strict TDD (Red -> Green -> Refactor) within defined Aggregate Roots.

## Build and Test Commands
- **Validate Specifications:** `python tools/sdsd_validate.py --all`
- **Run Unit & Contract Tests:** `python -m unittest discover tests`
- **Run Reverse-Patch Transpiler:** `python tools/sdsd_reverse_patch.py --working-tree --incident INC-001`
- **Run Quickstart Demo:** `python quickstart.py`

## Critical Rules
- **No Direct Code Patching:** If an invariant or bug occurs, update `specs/` first, derive failing tests, and regenerate.
- **Blast-Radius Enforcement:** Never modify files outside the specification's `Permitted Files`. Modifying untouchable files (auth, migrations, dependency manifests) fails CI.
- **Negative Constraints:** Treat negative constraints (what the system must NEVER do) as primary security boundaries.
