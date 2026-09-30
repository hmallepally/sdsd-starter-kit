# SDSD Starter Kit: Spec-Driven Secure Development for AI-Native Pods

> **The Official Reference Implementation for the SDSD Pod Model & "Specification Is All You Need"**  
> *Author: Harinath Mallepally (Doctoral Researcher & Senior Enterprise Software Architect)*  
> *Companion Paper: "Specification Is All You Need: Spec-Driven Secure Development (SDSD) and Multi-Agent Orchestration in Enterprise Software Engineering" (Target: IEEE Software - SEIP Track)*  
> *License: MIT*

---

## ⚡ The Core Axiom

> **"In an AI-native software lifecycle, code is no longer the primary intellectual asset; the machine-readable specification is the single source of truth, and code is merely an ephemeral, compiled artifact. When a defect occurs or requirements evolve, engineers never patch the code directly; they refine the specification, and the multi-agent pipeline regenerates the implementation."**

---

## 🎯 What is this Starter Kit?

This repository is designed for **The Q1 Lighthouse Pod** (1 Senior Systems Steersperson + 1 Product Specialist operating dual AI IDEs). It provides the exact guardrails, automated invariant linters, prompt templates, and repository instructions needed to achieve a predictable **30–45 minute delivery cadence** per atomic feature while eliminating architectural drift and security regressions.

---

## 📚 Theoretical Foundations

SDSD is grounded in 30 years of classical software engineering contract theory modernized for multi-agent generative systems:

1. **Bertrand Meyer's Design by Contract (DbC, 1992, 1997):** Formalizes system operations as mathematical contracts governed strictly by Preconditions ($Q$), Postconditions ($R$), and Class Invariants ($I$).
2. **Eric Evans' Domain-Driven Design (DDD, 2003):** Leverages Aggregate Roots as transactional invariant boundaries and context-window firewalls to prevent agentic side-effects.
3. **Kent Beck's Test-Driven Development (TDD, 2002) & Freeman & Pryce (2009):** Implements an automated execution harness where Developer Agents are restricted to making failing contract tests pass without altering test assertions.
4. **Empirical Grounding:** Directly counteracts the doubling of code churn and refactoring collapse documented by GitClear (Harding & King, 2024), human verification fatigue (Mozannar et al., 2024; Kabir et al., 2024), single-prompt failure modes (SWE-bench, Jimenez et al., 2024), and supply-chain vulnerabilities (Pearce et al., 2022).

---

## 📂 Repository Topology

```
sdsd-starter-kit/
├── .github/workflows/
│   ├── spec-drift-check.yml       # Fails CI if code changed without a matching spec change
│   └── blast-radius-check.yml     # Enforces untouchable file boundaries and runs linter
├── .agent/
│   ├── rules/
│   │   ├── sdsd_core_axioms.md    # Non-negotiable SDSD operational rules & DbC axioms
│   │   └── role_separation.md     # Multi-role separation of concerns (Exploration vs. Acceleration)
│   ├── prompts/
│   │   ├── 01_business_architect.md # Problem space exploration & state machine drafting
│   │   ├── 02_specification_writer.md # Invariants, negative constraints, blast radius
│   │   ├── 03_developer_tdd.md    # Strict TDD execution (failing tests first -> pass)
│   │   └── 04_invariant_reviewer.md # Adversarial audit against invariants & sycophancy
│   └── instructions/
│       └── copilot-instructions.md # Context injection for Copilot / Antigravity / Cursor
├── tools/
│   └── sdsd_validate.py           # CLI specification validator & invariant linter
├── templates/
│   ├── SDSD_SPEC_TEMPLATE.md      # Standard invariant-first specification template
│   └── EMERGENCY_HOTPATCH_SLA.md  # 24-hour spec remediation protocol for P1 outages
├── tests/
│   └── test_sdsd_validate.py      # Automated test suite for the specification linter
└── specs/examples/
    └── sample_fund_transfer.spec.md # Complete reference specification
```

---

## 🚀 The 4-Step Pod Workflow (30–45 Minute Cycle)

```
[Problem Need] 
      │
      ▼
1. BUSINESS ARCHITECT AGENT  ──> Explores 3 trade-offs, drafts candidate state machine (Exploration Mode)
      │
      ▼
2. SPECIFICATION ENGINEER    ──> Human Product/Test expert formalizes invariants & blast radius
      │
      ▼  [Human Gate 1: Spec Sign-Off & Linter Pass]
      │
3. DEVELOPER AGENT (TDD+DDD) ──> Writes failing contract tests FIRST, then passes implementation (Acceleration Mode)
      │
      ▼
4. INVARIANT REVIEWER AGENT  ──> Decoupled adversarial model audits blast radius & security
      │
      ▼  [Human Gate 2: PR Merge]
[Production Deploy]
```

---

## 🛠️ Local Verification & Specification Linting

Before feeding any specification to an autonomous developer agent, run the built-in validator to verify that it satisfies all formal contract axioms:

```bash
# Validate a specific specification
python tools/sdsd_validate.py specs/examples/sample_fund_transfer.spec.md

# Validate all specifications in the repository
python tools/sdsd_validate.py --all

# Run the automated unit test suite
python tests/test_sdsd_validate.py
```

### What `sdsd_validate.py` Checks:
1. **DDD Aggregate Boundary:** Ensures the target Aggregate Root is explicitly declared.
2. **Blast-Radius Isolation:** Confirms that untouchable files are specified to prevent multi-file drift.
3. **Formal Invariants:** Validates that preconditions, postconditions, and class invariants are present.
4. **Explicit Negative Constraints:** Ensures the specification defines what the system must **NEVER** permit (anti-hallucination guardrail).
5. **Executable Contract Tests:** Verifies that failing test assertions (`TC-...` or `test_should_...`) are codified.

---

## 🛡️ Enterprise Safety Guardrails Included

1. **Blast-Radius Enforcement:** Specify files that AI agents are strictly forbidden to touch.
2. **Negative Constraints:** Explicitly tell AI what the system must *never* do to eliminate CWE security bugs.
3. **Emergency Hot-Patch Protocol (24-Hour SLA):** Manual hot-patches during P1 outages trigger an automatic `SPEC-DRIFT` CI alert with a strict 24-hour SLA to update the specification before any non-emergency code can deploy.
