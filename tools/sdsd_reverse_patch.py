#!/usr/bin/env python3
"""
SDSD Reverse-Specification Transpiler (sdsd_reverse_patch.py)
Spec-Driven Secure Development (SDSD) Starter Kit
Author: Harinath Mallepally
License: MIT

Inverts emergency production hotpatches and git diffs into formal SDSD specification contracts.
During high-severity incidents, engineers apply minimal operational fixes under time-bounded
branch controls. This tool captures the patch diff, isolates modified execution paths,
and automatically synthesizes candidate invariant constraints, blast-radius boundaries,
negative security constraints, and executable red TDD contract test stubs to eliminate spec debt.
"""

import sys
import re
import os
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Safe encoding for Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Import validator from same directory if available
try:
    from tools.sdsd_validate import validate_spec_file
except ImportError:
    try:
        from sdsd_validate import validate_spec_file
    except ImportError:
        validate_spec_file = None


def parse_diff_text(diff_text: str) -> dict:
    """Parses unified diff text to extract modified files, hunks, and code patterns."""
    files_modified = []
    current_file = None
    hunks = []
    current_hunk_header = ""
    added_lines = []
    removed_lines = []

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split(" ")
            if len(parts) >= 4:
                b_path = parts[3].replace("b/", "", 1)
                current_file = b_path
                if current_file not in files_modified and current_file != "/dev/null":
                    files_modified.append(current_file)
        elif line.startswith("+++ b/"):
            b_path = line[6:].strip()
            if b_path not in files_modified and b_path != "/dev/null":
                files_modified.append(b_path)
        elif line.startswith("@@"):
            current_hunk_header = line.strip()
            hunks.append({"file": current_file, "header": line.strip()})
        elif line.startswith("+") and not line.startswith("+++"):
            added_lines.append({"file": current_file, "text": line[1:].strip(), "hunk": current_hunk_header})
        elif line.startswith("-") and not line.startswith("---"):
            removed_lines.append({"file": current_file, "text": line[1:].strip(), "hunk": current_hunk_header})

    return {
        "files": files_modified,
        "hunks": hunks,
        "added_lines": added_lines,
        "removed_lines": removed_lines,
        "raw_diff": diff_text
    }


def infer_domain_aggregate(files: list[str]) -> str:
    """Infers the domain aggregate and component boundary from modified file paths."""
    if not files:
        return "core/emergency/hotpatch"
    
    first_file = files[0].replace("\\", "/")
    parts = [p for p in first_file.split("/") if p not in ("src", "lib", "app", "tests", "test", "pkg")]
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    elif len(parts) == 1:
        base = Path(parts[0]).stem
        return f"domain/{base}"
    return "core/production/hotpatch"


def synthesize_invariants_and_threats(parsed: dict) -> tuple[list[str], list[str], list[dict]]:
    """Synthesizes candidate invariants, negative constraints, and test scenarios from diff patterns."""
    invariants = []
    negative_constraints = []
    test_scenarios = []

    added_texts = [item["text"] for item in parsed["added_lines"]]
    all_added_joined = " \n ".join(added_texts)

    # 1. Null / None / Boundary Check Analysis
    if re.search(r'\b(is None|== null|!= null|is not None|nil|undefined)\b', all_added_joined, re.IGNORECASE):
        invariants.append("**Invariant 1 (Defensive Null Safety):** Input arguments and dereferenced entity attributes must be validated non-null before execution flow enters state transformation routines.")
        negative_constraints.append("The system must NEVER allow null or uninitialized reference states to propagate into database or external ledger operations.")
        test_scenarios.append({
            "id": "TC-HOTPATCH-001",
            "name": "Null / Uninitialized Payload Guard",
            "input": "Null or missing parameter payload in hotpatched path",
            "assertion": "Throws validation exception; halts execution without state corruption"
        })

    # 2. Financial / Range / Value Bounds Analysis
    if re.search(r'(<=|<|>|>=)\s*0|\b(balance|amount|limit|capacity|quota)\b', all_added_joined, re.IGNORECASE):
        invariants.append("**Invariant 2 (Strict Non-Negative Bounds):** Quantity and monetary values must satisfy strictly positive and bounded domain constraints (Value >= 0) across all transition steps.")
        negative_constraints.append("The service shall not permit execution of negative, zero-value, or overflow transactions under any circumstance.")
        test_scenarios.append({
            "id": "TC-HOTPATCH-002",
            "name": "Boundary & Limit Enforcement",
            "input": "Zero, negative, or overflow values exceeding bounded threshold",
            "assertion": "Rejects request with HTTP 422 / DomainValidationException"
        })

    # 3. Exception / Timeout / Concurrency Analysis
    if re.search(r'\b(try|catch|except|timeout|retry|atomic|lock|mutex)\b', all_added_joined, re.IGNORECASE):
        invariants.append("**Invariant 3 (Atomic Recovery & State Consistency):** Concurrent execution errors or upstream service timeouts must roll back local state mutations atomically to preserve system consistency.")
        negative_constraints.append("The system is forbidden from leaving orphaned database locks or uncommitted partial transactions during unexpected exception unwinding.")
        test_scenarios.append({
            "id": "TC-HOTPATCH-003",
            "name": "Transient Fault & State Rollback Contract",
            "input": "Upstream service timeout / database transaction failure",
            "assertion": "Rolls back atomic transaction; returns safe error envelope"
        })

    # Ensure baseline invariants if not enough detected
    if len(invariants) < 2:
        invariants.append("**Invariant (Hotpatch State Integrity):** The hotpatched operational path must maintain strict backward compatibility with existing bounded context state contracts.")
        invariants.append("**Invariant (Deterministic Execution):** Identical request inputs must yield identical state mutations without unintended side-effects.")

    if len(negative_constraints) < 2:
        negative_constraints.append("The service must NEVER bypass authentication, authorization, or tenant boundary perimeters during hotpatched execution.")
        negative_constraints.append("All external API communications shall not transmit unencrypted secrets or unmasked PII tokens.")

    # Guarantee at least 3 test scenarios (satisfying SDSD contract minimums)
    current_ids = {t["id"] for t in test_scenarios}
    if "TC-HOTPATCH-001" not in current_ids:
        test_scenarios.insert(0, {
            "id": "TC-HOTPATCH-001",
            "name": "Hotpatch Functional Regression Verification",
            "input": "Valid operational workload matching hotpatched condition",
            "assertion": "Executes successfully and returns verified HTTP 200 / success status"
        })
    if "TC-HOTPATCH-002" not in current_ids:
        test_scenarios.append({
            "id": "TC-HOTPATCH-002",
            "name": "Negative Constraint & Boundary Guard",
            "input": "Malformed or out-of-bounds input payload triggering previous outage",
            "assertion": "Safely intercepted with deterministic failure code; zero service degradation"
        })
    if "TC-HOTPATCH-003" not in current_ids:
        test_scenarios.append({
            "id": "TC-HOTPATCH-003",
            "name": "State Invariant & Fault Rollback Contract",
            "input": "Simulated downstream dependency timeout or unexpected interruption",
            "assertion": "Rolls back pending state transitions; preserves database invariant integrity"
        })

    return invariants, negative_constraints, test_scenarios


def generate_spec_markdown(
    parsed: dict,
    spec_id: str,
    incident_id: str,
    author: str,
    target_component: str
) -> str:
    """Generates a complete, formally compliant SDSD specification document."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    invariants, negative_constraints, test_scenarios = synthesize_invariants_and_threats(parsed)

    allowed_files = parsed["files"] if parsed["files"] else ["src/hotpatch_target.py"]
    allowed_files_md = "\n".join([f"- `{f}`" for f in allowed_files])

    invariants_md = "\n".join([f"- {inv}" for inv in invariants])
    negatives_md = "\n".join([f"{i+1}. {nc}" for i, nc in enumerate(negative_constraints)])

    test_rows_md = "\n".join([
        f"| `{t['id']}` | {t['name']} | {t['input']} | {t['assertion']} |"
        for t in test_scenarios
    ])

    diff_summary = f"Synthesized from {len(parsed['files'])} file(s), {len(parsed['hunks'])} diff hunk(s), +{len(parsed['added_lines'])} / -{len(parsed['removed_lines'])} lines."

    spec_content = f"""# {spec_id}: Emergency Hotpatch Remediation Specification

> **Status:** `PROVISIONAL_HOTPATCH (Human Gate 1 Pending Post-Incident Sign-Off)`  
> **Component:** `{target_component}`  
> **Risk Classification:** `HIGH OPERATIONAL (EMERGENCY REMEDIATION)`  
> **Target Cycle Cadence:** `15 Minutes (Hotpatch Retrofit SLA: < 24 Hours)`  
> **Authors:** Incident Response Lead & Specification Engineer ({author})  
> **Incident Reference:** `{incident_id}`  
> **Generation Metadata:** `{diff_summary}`  

---

## 1. Context & Business Intent

### Problem Statement
During an active production incident ({incident_id}), an operational deficiency was identified requiring immediate remediation to restore service stability and prevent user impact. An emergency code hotpatch was deployed under time-bounded operational authority. This specification retroactively codifies the invariant boundaries and formal contracts governing the hotpatched behavior to eliminate architectural drift.

### Target Outcome
Formalize the operational constraints introduced by the hotpatch. Establish automated invariant guards, explicit negative security bounds, and executable red TDD contract test cases to ensure that future autonomous multi-agent code generation does not regress the production fix.

---

## 2. Domain State Machine

```
                      +----------------------+
                      |      INITIATED       |
                      +----------+-----------+
                                 |
                      [Precondition Validation]
                                 |
                                 v
                      +----------------------+
            +---------+      VALIDATED       +---------+
            |         +----------+-----------+         |
    [System Fault]               |               [Invalid Input]
            |           [Execute Safe Mutation]        |
            v                    |                     v
+----------------------+         v          +----------------------+
|        FAILED        |  +--------------+  |       REJECTED       |
+----------------------+  |  COMPLETED   |  +----------------------+
                          +--------------+
```

### Transition Invariants
- `INITIATED -> VALIDATED`: Permitted only if all defensive preconditions and null-checks are strictly satisfied.
- `VALIDATED -> COMPLETED`: Permitted only upon verified, deterministic state transformation without unintended side-effects.
- `INITIATED -> REJECTED`: Triggered immediately if boundary checks fail; execution halts deterministically.
- `VALIDATED -> FAILED`: Triggered if downstream dependency fails; atomic rollback restores baseline state.

---

## 3. Mathematical & Domain Invariants

{invariants_md}

---

## 4. Threat Model & Security Boundaries (Negative Constraints)

{negatives_md}

---

## 5. Blast-Radius Boundary Envelope

Autonomous agents executing code modifications for this hotpatched domain are strictly constrained by the following path rules:

### Allowed Files (May Create or Edit):
{allowed_files_md}

### Forbidden Baseline (Untouchable Files — Any Edit Fails CI):
- `src/auth/**` (Authentication middleware)
- `schema/migrations/**` (Database schema and migrations)
- `config/production.env` (Infrastructure configuration)
- `.github/**` (CI/CD pipeline workflows)
- `package.json`, `pom.xml`, `requirements.txt`, `Cargo.toml` (Dependency manifests — zero automated changes permitted to prevent supply-chain poisoning)

---

## 6. Executable Test Matrix (Red TDD Contract)

| Test ID | Scenario | Input Conditions | Expected Assertion / Behavior |
|:---|:---|:---|:---|
{test_rows_md}

---

## 7. Human Gate 1 Sign-Off

- [ ] **Incident Commander Sign-Off:** Operational stability restored and root cause isolated. (Signed: _______________, {today})
- [ ] **Specification Engineer Sign-Off:** Invariant contracts, negative constraints, and blast-radius perimeter validated. (Signed: {author}, {today})
- [ ] **Post-Incident Review (PIR) Certified:** Specification merged to main branch; spec-drift deployment blocker cleared.
"""
    return spec_content


def get_git_diff(commit_ref: str = None, working_tree: bool = False) -> str:
    """Retrieves diff from git repository."""
    if working_tree:
        cmd = ["git", "diff", "HEAD"]
    elif commit_ref:
        cmd = ["git", "show", commit_ref]
    else:
        cmd = ["git", "diff", "HEAD~1", "HEAD"]
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return res.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def main():
    parser = argparse.ArgumentParser(
        description="SDSD Reverse-Specification Transpiler: Inverts production hotpatches into formal SDSD contracts."
    )
    parser.add_argument("--diff", "-d", help="Path to unified diff / patch file (or '-' for stdin)")
    parser.add_argument("--stdin", action="store_true", help="Read diff directly from stdin")
    parser.add_argument("--commit", "-c", help="Git commit hash or range (e.g., HEAD~1, abc1234)")
    parser.add_argument("--working-tree", "-w", action="store_true", help="Capture uncommitted working-tree diff")
    parser.add_argument("--output", "-o", help="Output path for the generated .spec.md file")
    parser.add_argument("--spec-id", help="Custom Specification ID (default: auto-generated timestamp)")
    parser.add_argument("--incident", default="INC-HOTPATCH-001", help="Incident ticket reference (default: INC-HOTPATCH-001)")
    parser.add_argument("--author", default="Harinath Mallepally", help="Author name (default: Harinath Mallepally)")
    parser.add_argument("--validate", action="store_true", default=True, help="Validate synthesized spec using SDSD linter")
    parser.add_argument("--no-validate", action="store_false", dest="validate", help="Skip automatic linter validation")

    args = parser.parse_args()

    # Obtain diff text
    diff_text = ""
    if args.diff:
        if args.diff == "-":
            diff_text = sys.stdin.read()
        else:
            diff_path = Path(args.diff)
            if not diff_path.exists():
                print(f"Error: Diff file not found: {diff_path}", file=sys.stderr)
                sys.exit(1)
            diff_text = diff_path.read_text(encoding="utf-8")
    elif args.stdin:
        diff_text = sys.stdin.read()
    elif args.working_tree:
        diff_text = get_git_diff(working_tree=True)
    elif args.commit:
        diff_text = get_git_diff(commit_ref=args.commit)
    else:
        # Check if working tree has diff
        diff_text = get_git_diff(working_tree=True)
        if not diff_text or not diff_text.strip():
            # Check last commit
            diff_text = get_git_diff("HEAD~1")

    if not diff_text or not diff_text.strip():
        # Fallback sample diff for testing / demonstration
        print("[INFO] No git diff detected in environment. Using synthesized sample emergency hotpatch diff for demonstration.")
        diff_text = """diff --git a/src/domain/billing/transfer_service.py b/src/domain/billing/transfer_service.py
--- a/src/domain/billing/transfer_service.py
+++ b/src/domain/billing/transfer_service.py
@@ -42,6 +42,10 @@ def execute_transfer(source_account, dest_account, amount):
+    if amount is None or amount <= 0:
+        raise InvalidTransferAmountException("Transfer amount must be strictly positive")
+    if source_account is None or dest_account is None:
+        raise NullAccountException("Source and destination accounts must not be null")
     return process_ledger_update(source_account, dest_account, amount)
"""

    parsed = parse_diff_text(diff_text)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    spec_id = args.spec_id or f"SPEC-HOTPATCH-{timestamp}"
    target_component = infer_domain_aggregate(parsed["files"])

    spec_markdown = generate_spec_markdown(
        parsed=parsed,
        spec_id=spec_id,
        incident_id=args.incident,
        author=args.author,
        target_component=target_component
    )

    # Determine destination
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(spec_markdown, encoding="utf-8")
        print(f"[SUCCESS] Synthesized SDSD specification written to: {out_path}")
    else:
        print("=" * 80)
        print("SYNTHESIZED SDSD EMERGENCY SPECIFICATION")
        print("=" * 80)
        print(spec_markdown)
        print("=" * 80)

    # Automatic validation
    if args.validate:
        if validate_spec_file:
            print("\n[VALIDATION] Running SDSD Invariant Linter on synthesized specification...")
            test_path = Path(args.output) if args.output else Path("specs/hotpatches/temp_hotpatch.spec.md")
            test_path.parent.mkdir(parents=True, exist_ok=True)
            test_path.write_text(spec_markdown, encoding="utf-8")

            is_valid, errors, warnings = validate_spec_file(test_path)
            for err in errors:
                print(f"  [ERROR] {err}")
            for warn in warnings:
                print(f"  [WARN]  {warn}")

            if not args.output and test_path.exists():
                test_path.unlink()

            if is_valid:
                print("  [PASS] Synthesized specification satisfies all SDSD contract axioms and DevSecOps defenses.")
            else:
                print("  [FAIL] Synthesized specification failed contract validation.")
                sys.exit(1)
        else:
            print("[WARN] sdsd_validate module not available for immediate contract validation.")


if __name__ == "__main__":
    main()
