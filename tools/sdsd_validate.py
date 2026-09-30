#!/usr/bin/env python3
"""
SDSD Specification Validator & Invariant Linter
Spec-Driven Secure Development (SDSD) Starter Kit
Author: Harinath Mallepally
License: MIT

Validates that an SDSD specification satisfies all formal contract requirements:
1. Aggregate Root & Domain Boundary defined (Evans, 2003)
2. Blast-Radius Perimeter & Untouchable Files specified (Martin, 2017)
3. Formal Invariants (Preconditions, Postconditions, Class Invariants) (Meyer, 1992)
4. Explicit Negative Constraints ("What the system must NEVER do")
5. Executable TDD Contract Tests defined (Beck, 2002)
"""

import sys
import re
import os
import argparse
from pathlib import Path

REQUIRED_CONCEPTS = [
    (r'(?:##\s*\d*\.?\s*(?:Context|Problem\s+Statement|Business\s+Intent))', 'Problem Statement & Domain Context'),
    (r'(?:##\s*\d*\.?\s*Domain\s+State\s+Machine|State\s+Machine)', 'Domain State Machine'),
    (r'(?:##\s*\d*\.?\s*.*Invariants.*)', 'Domain Invariants & Contracts'),
    (r'(?:##\s*\d*\.?\s*.*(?:Negative\s+Constraints|Threat\s+Model).*)', 'Negative Security Constraints'),
    (r'(?:##\s*\d*\.?\s*Blast[- ]Radius.*)', 'Blast-Radius Perimeter & Untouchable Files'),
    (r'(?:##\s*\d*\.?\s*Executable\s+Test.*|##\s*\d*\.?\s*.*Contract\s+Tests.*)', 'Executable Contract Tests'),
]

NEGATIVE_CONSTRAINT_KEYWORDS = [r'\bnever\b', r'\bshall not\b', r'\bforbidden\b', r'\bprohibited\b']

def validate_spec_file(file_path: Path) -> tuple[bool, list[str], list[str]]:
    """Validates a single .spec.md file against SDSD contract axioms."""
    errors = []
    warnings = []

    if not file_path.exists():
        return False, [f"File not found: {file_path}"], []

    content = file_path.read_text(encoding='utf-8')

    # 1. Header Metadata Check
    if not re.search(r'SPEC-[A-Z0-9_-]+|Spec\s*ID', content, re.IGNORECASE):
        errors.append("Missing Spec identifier (e.g., 'SPEC-001' or 'Spec ID: SPEC-...').")
    
    if not re.search(r'(?:Component|Target Domain|Aggregate):', content, re.IGNORECASE):
        errors.append("Missing Domain / Component / Aggregate Root boundary declaration.")

    # 2. Required Concepts Check
    for pattern, concept_name in REQUIRED_CONCEPTS:
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Missing required concept: {concept_name}")

    # 3. Blast-Radius & Untouchable Files Check
    if not re.search(r'untouchable|forbidden|zero-modification', content, re.IGNORECASE):
        errors.append("Specification must explicitly define 'Untouchable Files' or forbidden path baselines.")

    # 4. Invariant Formalisms Check (Negative Constraints)
    has_negative_constraints = False
    for kw in NEGATIVE_CONSTRAINT_KEYWORDS:
        if re.search(kw, content, re.IGNORECASE):
            has_negative_constraints = True
            break
    
    if not has_negative_constraints:
        errors.append("Specification must specify explicit negative constraints ('NEVER', 'FORBIDDEN', or 'SHALL NOT').")

    # 5. Executable Contract Tests Check
    test_matches = re.findall(r'(\bTC-[\w-]+\b|\btest_\w+\b|`test_\w+`|`TC-[\w-]+`)', content)
    if not test_matches:
        errors.append("Specification must list executable test assertions or test cases (e.g. `TC-TR-001` or `test_should_...`).")
    elif len(test_matches) < 2:
        warnings.append(f"Found only {len(test_matches)} test identifier. Recommended minimum: 3.")

    # 6. Anti-Vibe Coding Heuristic: Check for vague requirements
    vague_phrases = [r'\bshould be fast\b', r'\bstandard validation\b', r'\betc\.\b', r'\btodo\b']
    for vp in vague_phrases:
        if re.search(vp, content, re.IGNORECASE):
            warnings.append(f"Potentially ambiguous specification phrase detected matching '{vp}'. Replace with deterministic assertions.")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def main():
    parser = argparse.ArgumentParser(description="SDSD Specification Validator & Invariant Linter")
    parser.add_argument("spec_path", nargs="?", help="Path to a .spec.md file to validate")
    parser.add_argument("--all", action="store_true", help="Validate all .spec.md files in the repository")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent

    if args.all:
        spec_files = list(repo_root.glob("**/*.spec.md"))
        if not spec_files:
            print("No .spec.md files found in repository.")
            sys.exit(0)
    elif args.spec_path:
        spec_files = [Path(args.spec_path)]
    else:
        spec_files = list((repo_root / "specs").glob("**/*.spec.md"))
        if not spec_files:
            parser.print_help()
            sys.exit(1)

    print("=" * 80)
    print("SPEC-DRIVEN SECURE DEVELOPMENT (SDSD) SPECIFICATION LINTER")
    print("=" * 80)

    total_files = len(spec_files)
    total_passed = 0
    has_failures = False

    for spec_file in spec_files:
        try:
            rel_path = spec_file.relative_to(repo_root)
        except ValueError:
            rel_path = spec_file
        print(f"\nValidating: {rel_path} ...")
        is_valid, errors, warnings = validate_spec_file(spec_file)

        for err in errors:
            print(f"  [ERROR] {err}")
        for warn in warnings:
            print(f"  [WARN]  {warn}")

        if args.strict and warnings:
            is_valid = False

        if is_valid:
            print("  [PASS] Specification complies with all SDSD formal contract axioms.")
            total_passed += 1
        else:
            print("  [FAIL] Specification does not meet formal contract standards.")
            has_failures = True

    print("\n" + "=" * 80)
    print(f"LINTER SUMMARY: {total_passed}/{total_files} specifications passed.")
    print("=" * 80)

    if has_failures:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
