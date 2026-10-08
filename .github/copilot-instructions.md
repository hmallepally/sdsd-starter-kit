# GitHub Copilot Repository Instructions: Spec-Driven Secure Development (SDSD)

You are operating within a repository governed by **Spec-Driven Secure Development (SDSD)**. 
In this environment, **the machine-readable specification is the sole immutable source of truth, and code is an ephemeral, disposable compiled output.**

---

## 🧭 Non-Negotiable Operational Axioms:

1. **The Disposable Code Principle:** Never patch source code directly to solve a requirements change or bug. Update the contract in `/specs/` first, derive failing tests, and regenerate the implementation.
2. **Strict TDD (Red -> Green -> Refactor):** You must author failing contract tests (derived from Section 5 / Executable Test Matrix) BEFORE writing any domain or service logic. Confirm tests fail before making them pass.
3. **Blast-Radius Isolation:** You are strictly confined to the `Permitted Files` declared in the target specification. Modifying any file listed under `Untouchable Files` (e.g., `src/auth/*`, `schema/migrations/*`, `package.json`, `pom.xml`, `requirements.txt`) will fail CI immediately.
4. **Negative Constraint Enforcement:** Always inspect Section 4 of the specification. The system must explicitly enforce what it must *never* do (e.g., no negative balances, no cross-tenant leakage, zero unencrypted secrets in logs, strict SQL parameterization).
5. **Non-Functional Performance & Runtime Guardrails:**
   - Enforce server-side pagination and database indexing ($C_{\text{perf}}$); never load entire tables into application heap memory.
   - Enforce configuration parity across environments ($C_{\text{env}}$) with fail-fast connectivity checks.
6. **No Speculative Refactoring:** Do not 'clean up', optimize, or re-architect code outside the active aggregate root boundary.

---

## 🛠️ Local Verification Commands:
- **Validate Specifications:** `python tools/sdsd_validate.py --all`
- **Run Contract Test Suite:** `python -m unittest discover tests` (or `pytest`)
- **Transpile Emergency Hotpatch:** `python tools/sdsd_reverse_patch.py --working-tree --incident INC-XXXXX`
