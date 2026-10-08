#!/usr/bin/env python3
"""
Unit Tests for SDSD Reverse-Specification Transpiler (sdsd_reverse_patch.py)
Author: Harinath Mallepally
License: MIT
"""

import unittest
import tempfile
import sys
from pathlib import Path

# Add tools directory to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "tools"))

from sdsd_reverse_patch import (
    parse_diff_text,
    generate_spec_markdown,
    infer_domain_aggregate,
)


class TestSDSDReversePatch(unittest.TestCase):

    def setUp(self):
        self.sample_diff = """diff --git a/src/domain/billing/transfer_service.py b/src/domain/billing/transfer_service.py
index 1234567..89abcdef 100644
--- a/src/domain/billing/transfer_service.py
+++ b/src/domain/billing/transfer_service.py
@@ -45,6 +45,12 @@ class TransferService:
         if source.tenant_id != destination.tenant_id:
             raise TenantIsolationBreachException("Cross-tenant transfer forbidden")
+
+        # Hotpatch INC-98241: Enforce minimum transfer threshold
+        if amount < Decimal("0.01"):
+            raise InvalidTransferAmountException("Transfer amount must be at least 0.01")
+
         source.debit(amount)
         destination.credit(amount)
"""

    def test_parse_diff_text_extracts_files_and_hunks(self):
        parsed = parse_diff_text(self.sample_diff)
        self.assertIn("files", parsed)
        self.assertEqual(len(parsed["files"]), 1)
        self.assertEqual(parsed["files"][0], "src/domain/billing/transfer_service.py")
        self.assertTrue(len(parsed["added_lines"]) > 0)
        self.assertTrue(any("InvalidTransferAmountException" in item["text"] for item in parsed["added_lines"]))

    def test_infer_domain_aggregate(self):
        files = ["src/domain/billing/transfer_service.py"]
        aggregate = infer_domain_aggregate(files)
        self.assertIn("billing", aggregate.lower())

    def test_generate_spec_contains_required_sdsd_sections(self):
        parsed = parse_diff_text(self.sample_diff)
        spec_text = generate_spec_markdown(
            parsed=parsed,
            spec_id="SPEC-HOTPATCH-INC-98241",
            incident_id="INC-98241",
            author="Harinath Mallepally",
            target_component="core/billing/transfer",
        )

        # Invariant checks per SDSD contract axioms
        self.assertIn("# SPEC-HOTPATCH-INC-98241", spec_text)
        self.assertIn("## 1. Context & Business Intent", spec_text)
        self.assertIn("## 2. Domain State Machine", spec_text)
        self.assertIn("## 3. Mathematical & Domain Invariants", spec_text)
        self.assertIn("## 4. Threat Model & Security Boundaries (Negative Constraints)", spec_text)
        self.assertIn("## 5. Blast-Radius Boundary Envelope", spec_text)
        self.assertIn("## 6. Executable Test Matrix (Red TDD Contract)", spec_text)

        # Verify negative constraints and test cases
        self.assertIn("Negative Constraint", spec_text)
        self.assertIn("TC-HOTPATCH-", spec_text)
        self.assertIn("INC-98241", spec_text)

    def test_synthesized_spec_passes_sdsd_validator(self):
        from sdsd_validate import validate_spec_file

        with tempfile.TemporaryDirectory() as tmp_dir:
            parsed = parse_diff_text(self.sample_diff)
            spec_text = generate_spec_markdown(
                parsed=parsed,
                spec_id="SPEC-INC-TEST-001",
                incident_id="INC-TEST-001",
                author="Test Author",
                target_component="core/billing/transfer",
            )
            spec_file = Path(tmp_dir) / "test_hotpatch.spec.md"
            spec_file.write_text(spec_text, encoding="utf-8")

            is_valid, errors, warnings = validate_spec_file(spec_file)
            self.assertTrue(is_valid, f"Synthesized spec failed validation: {errors}")
            self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
