# Multi-Role Separation of Concerns in SDSD Pods

The SDSD framework shifts enterprise development from isolated coder silos to an integrated, multi-role epistemic pipeline.

---

## 1. Product Specialist / Business Analyst (Problem Architect)
* **Mission:** Ingest customer needs and business objectives; explore domain topologies.
* **Agent Pairing:** Business Architect Agent (`.agent/prompts/01_business_architect.md`).
* **Key Activities:**
  - Evaluates 2–3 competing architecture approaches before implementation.
  - Formalizes finite-state machines (FSMs) for business entities.
  - Identifies business edge cases and concurrency hazards.
* **Gate Ownership:** **Human Gate 1 (Spec Sign-Off)** — validates business intent before engineering generation begins.

---

## 2. System Test Engineer (Specification Engineer)
* **Mission:** Transform conceptual business models into formal, executable invariant contracts.
* **Agent Pairing:** Specification Writer Agent (`.agent/prompts/02_specification_writer.md`).
* **Key Activities:**
  - Formulates negative constraints and security invariants.
  - Specifies blast-radius boundaries (allowed vs. forbidden files).
  - Authors the executable TDD test contract matrix.
* **Gate Ownership:** Verifies invariant coverage and security completeness for **Human Gate 1**.

---

## 3. Development Expert (Systems Steersperson)
* **Mission:** Steer autonomous TDD generation; enforce Clean Architecture and DDD principles.
* **Agent Pairing:** Developer Agent (`.agent/prompts/03_developer_tdd.md`).
* **Key Activities:**
  - Enforces strict Red-Green-Refactor cycle: failing tests *before* implementation.
  - Confines agent modifications strictly within the blast radius.
  - Verifies local builds, compiler passes, and unit test execution.
* **Gate Ownership:** Prepares candidate pull requests (PRs) for adversarial review.

---

## 4. Invariant Guardian (Code Reviewer Agent)
* **Mission:** Adversarial, decoupled inspection of PR diffs against invariant contracts.
* **Agent Pairing:** Invariant Reviewer Agent (`.agent/prompts/04_invariant_reviewer.md`).
* **Key Activities:**
  - Scans git diff against forbidden file lists.
  - Audits for OWASP Top 10 vulnerabilities and secret leakage.
  - Verifies 100% invariant test branch coverage.
* **Gate Ownership:** Pre-approves PRs for **Human Gate 2 (Architecture & Production Sign-Off)**.
