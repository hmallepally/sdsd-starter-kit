# SDSD Starter Kit: Spec-Driven Secure Development for AI-Native Pods

> **The Official Reference Implementation for the SDSD Pod Model & "Specification Is All You Need"**  
> *Author: Harinath Mallepally*  
> *License: MIT*

---

## ⚡ The Core Axiom

> **"Code is an ephemeral, disposable compiled artifact. The specification is the single source of truth. When something goes wrong or requirements evolve, never patch the code—patch the specification."**

---

## 🎯 What is this Starter Kit?

This repository is designed for **The Q1 Lighthouse Pod** (1 Senior Development Expert + 1 Product Specialist operating dual AI IDEs). It provides the exact guardrails, prompt templates, and repository instructions needed to achieve a predictable **30–45 minute delivery cadence** per feature while eliminating architectural drift and security regressions.

---

## 📂 Repository Topology

```
sdsd-starter-kit/
├── .github/workflows/
│   ├── spec-drift-check.yml       # Fails CI if code changed without a matching spec change
│   └── blast-radius-check.yml     # Enforces untouchable file boundaries
├── .agent/
│   ├── rules/
│   │   ├── sdsd_core_axioms.md    # Non-negotiable SDSD operational rules
│   │   └── role_separation.md     # Multi-role separation of concerns
│   ├── prompts/
│   │   ├── 01_business_architect.md # Problem space exploration & state machine drafting
│   │   ├── 02_specification_writer.md # Invariants, negative constraints, blast radius
│   │   ├── 03_developer_tdd.md    # Strict TDD execution (failing tests first -> pass)
│   │   └── 04_invariant_reviewer.md # Adversarial audit against invariants & sycophancy
│   └── instructions/
│       └── copilot-instructions.md # Context injection for Copilot / Antigravity / Cursor
├── templates/
│   ├── SDSD_SPEC_TEMPLATE.md      # Standard invariant-first specification template
│   └── EMERGENCY_HOTPATCH_SLA.md  # 24-hour spec remediation protocol for P1 outages
└── specs/examples/
    └── sample_fund_transfer.spec.md # Complete reference specification
```

---

## 🚀 The 4-Step Pod Workflow (30–45 Minute Cycle)

```
[Problem Need] 
      │
      ▼
1. BUSINESS ARCHITECT AGENT  ──> Explores 3 trade-offs, drafts candidate state machine
      │
      ▼
2. SPECIFICATION ENGINEER    ──> Human Product/Test expert formalizes invariants & blast radius
      │
      ▼  [Human Gate 1: Spec Sign-Off]
      │
3. DEVELOPER AGENT (TDD+DDD) ──> Writes failing contract tests FIRST, then passes implementation
      │
      ▼
4. INVARIANT REVIEWER AGENT  ──> Decoupled adversarial model audits blast radius & security
      │
      ▼  [Human Gate 2: PR Merge]
[Production Deploy]
```

---

## 🛡️ Key Safety Guardrails Included

1. **Blast-Radius Enforcement:** Specify files that AI agents are forbidden to touch.
2. **Negative Constraints:** Explicitly tell AI what the system must *never* do.
3. **Emergency Hot-Patch Protocol:** Manual hot-patches during P1 outages trigger an automatic `SPEC-DRIFT` CI alert with a strict 24-hour SLA to update the specification.
