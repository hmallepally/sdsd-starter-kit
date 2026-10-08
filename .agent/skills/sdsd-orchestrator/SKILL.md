---
name: sdsd-orchestrator
description: Orchestrates Spec-Driven Secure Development (SDSD) workflows including contract linting, autonomous Red-to-Green TDD, blast-radius verification, and emergency hotpatch reverse-transpilation.
---

# SDSD Orchestrator Skill

This skill provides operational workflows for agents acting in an SDSD engineering pod.

## Available Workflows

### 1. Spec Validation (`tools/sdsd_validate.py`)
Run on any specification prior to code generation:
```bash
python tools/sdsd_validate.py <path_to_spec.md>
```
Fails if aggregate root, formal invariants, negative constraints, blast radius, or contract tests are missing or if prompt injection patterns are detected.

### 2. Autonomous TDD Loop
When assigned a validated specification:
1. **RED:** Read the Executable Test Matrix in Section 5/6 of the spec. Write failing contract tests in `tests/unit/...`.
2. **VERIFY RED:** Run `python -m unittest <test_file>` to prove failure.
3. **GREEN:** Write minimal domain entity and service logic in `src/domain/...` to satisfy the tests and negative constraints.
4. **VERIFY GREEN:** Run tests to confirm 100% pass.
5. **CHECK BLAST RADIUS:** Verify no untouchable baseline files were modified (`git status`).

### 3. Emergency Hotpatch Transpilation (`tools/sdsd_reverse_patch.py`)
When a production outage was resolved via a minimal git hotpatch:
```bash
python tools/sdsd_reverse_patch.py --working-tree --incident INC-XXXXX --output specs/hotpatches/SPEC-INC-XXXXX.spec.md
```
Captures the diff, infers domain invariants, extracts negative constraints, and derives red regression tests.
