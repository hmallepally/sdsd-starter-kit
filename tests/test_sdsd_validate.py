#!/usr/bin/env python3
"""
Unit Tests for SDSD Specification Validator
Author: Harinath Mallepally
License: MIT
"""

import unittest
from pathlib import Path
import tempfile
import sys

# Add tools directory to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "tools"))

from sdsd_validate import validate_spec_file

class TestSDSDValidator(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_valid_specification(self):
        valid_content = """# SPEC-101: Payment Processor
Target Domain / Aggregate: Billing / Payment

## 1. Problem Statement & User Value
Processes credit card charges safely.

## 2. Blast Radius & File Boundaries
Permitted: `src/domain/payment/*`
Untouchable Files:
- `src/core/security/*`
- `schema/migrations/*`

## 3. Domain State Machine
| State | Event | Next State |
| `PENDING` | `Authorize` | `AUTHORIZED` |

## 4. Invariants & Negative Constraints
1. Precondition: Account must be active.
2. Postcondition: Payment status must be updated.
3. Negative Constraint: The system must NEVER allow duplicate charge transactions.

## 5. Executable Contract Tests
- `test_should_charge_valid_card`
- `test_should_reject_expired_card`
- `test_should_enforce_idempotency`
"""
        spec_file = self.temp_path / "valid.spec.md"
        spec_file.write_text(valid_content, encoding='utf-8')

        is_valid, errors, warnings = validate_spec_file(spec_file)
        self.assertTrue(is_valid, f"Expected valid, got errors: {errors}")
        self.assertEqual(len(errors), 0)

    def test_missing_negative_constraints_fails(self):
        invalid_content = """# SPEC-102: Incomplete Spec
Target Domain / Aggregate: Billing / Payment

## 1. Problem Statement & User Value
Processes credit card charges safely.

## 2. Blast Radius & File Boundaries
Untouchable Files: `src/core/security/*`

## 3. Domain State Machine
| State | Event | Next State |

## 4. Invariants & Negative Constraints
1. Positive Invariant: Balance must be positive.

## 5. Executable Contract Tests
- `test_should_charge_valid_card`
- `test_should_reject_expired_card`
"""
        spec_file = self.temp_path / "missing_neg.spec.md"
        spec_file.write_text(invalid_content, encoding='utf-8')

        is_valid, errors, warnings = validate_spec_file(spec_file)
        self.assertFalse(is_valid)
        self.assertTrue(any("negative constraints" in e.lower() for e in errors))

    def test_missing_blast_radius_untouchable_files_fails(self):
        invalid_content = """# SPEC-103: No Blast Radius
Target Domain / Aggregate: Billing / Payment

## 1. Problem Statement & User Value
Processes credit card charges safely.

## 2. Blast Radius & File Boundaries
Permitted: all files.

## 3. Domain State Machine
| State | Event | Next State |

## 4. Invariants & Negative Constraints
The system must NEVER allow negative balance.

## 5. Executable Contract Tests
- `test_should_charge_valid_card`
- `test_should_reject_expired_card`
"""
        spec_file = self.temp_path / "no_untouchable.spec.md"
        spec_file.write_text(invalid_content, encoding='utf-8')

        is_valid, errors, warnings = validate_spec_file(spec_file)
        self.assertFalse(is_valid)
        self.assertTrue(any("untouchable" in e.lower() for e in errors))

if __name__ == "__main__":
    unittest.main()
