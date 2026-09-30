# Multi-Role Separation of Concerns & The SDSD Triad Architecture

The SDSD framework replaces bloated Scrum teams and isolated coder silos with an integrated, multi-role epistemic pipeline built on highly specialized, sophisticated craft.

---

## 🏛️ The SDSD Triad: Highly Specialized Core Unit

Every autonomous execution cell in an SDSD organization is a **Triad** of three specialized engineering practitioners:

1. **Product Specialist / Business Architect:**
   * **Discipline:** Domain topology modeling, customer outcomes, and finite-state boundary architecture.
   * **Agent Pairing:** Business Architect Agent (`.agent/prompts/01_business_architect.md`).
   * **Key Focus:** Operates in *Exploration Mode* (Barke et al., 2023), resolving latent business ambiguity before code generation.
   * **Gate Ownership:** **Human Gate 1 (Spec Sign-Off)** — validates business intent.

2. **Specification Engineer (Test Architect):**
   * **Discipline:** Mathematical invariant modeling (Meyer's DbC $Q, R, I$), negative security constraints, and blast-radius perimeter envelopes.
   * **Agent Pairing:** Specification Writer Agent (`.agent/prompts/02_specification_writer.md`).
   * **Key Focus:** Defines explicit state boundaries, untouchable-file baselines, and failing TDD contract matrices.
   * **Gate Ownership:** Verifies invariant coverage and blast-radius security for **Human Gate 1**.

3. **Systems Steersperson (Senior Software Architect):**
   * **Discipline:** Domain-Driven Design (DDD), Clean Architecture, Test-Driven Development (TDD), and multi-agent fleet navigation.
   * **Agent Pairing:** Developer Agent (`.agent/prompts/03_developer_tdd.md`).
   * **Key Focus:** Operates in *Acceleration Mode* (Barke et al., 2023), enforcing the strict Red-Green-Refactor cycle where agents must make failing contract tests pass without modifying assertions.
   * **Gate Ownership:** Prepares candidate pull requests for adversarial review.

4. **Invariant Guardian (Automated Reviewer Agent):**
   * **Discipline:** Decoupled adversarial AST and diff auditing running on an independent model family.
   * **Agent Pairing:** Invariant Reviewer Agent (`.agent/prompts/04_invariant_reviewer.md`).
   * **Key Focus:** Verifies untouchable-file compliance, OWASP Top 10 standards, and test branch coverage to eliminate agent sycophancy before human PR merge.

---

## 👥 The 2+1 Triad Team Formula (9-Person Self-Sufficient Pod)

To sustain high-cadence delivery while continuously upskilling engineering talent, organizations scale via the **2+1 Triad Formula**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   SDSD NINE-PERSON TEAM (POD)                          │
│                                                                        │
│   ┌───────────────────────────┐      ┌───────────────────────────┐     │
│   │     REGULAR TRIAD 1       │      │     REGULAR TRIAD 2       │     │
│   │  • Product Specialist     │      │  • Product Specialist     │     │
│   │  • Specification Engineer │      │  • Specification Engineer │     │
│   │  • Systems Steersperson   │      │  • Systems Steersperson   │     │
│   └───────────────────────────┘      └───────────────────────────┘     │
│            (Senior Production Feature Delivery — 30-45m Cadence)       │
│                                                                        │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │                     JUNIOR TRIAD (TRAINING)                  │     │
│   │  • Junior Product Specialist                                 │     │
│   │  • Junior Specification Engineer                             │     │
│   │  • Junior Systems Steersperson                               │     │
│   └──────────────────────────────────────────────────────────────┘     │
│           (Structured Apprenticeship & Direct Workflow Shadowing)      │
└────────────────────────────────────────────────────────────────────────┘
```

* **Self-Sufficiency & Zero Administrative Overhead:**
  The team contains all required technical and domain skills. **Ad-hoc administrative roles (dedicated Scrum Masters, agile coaches, ticket administrators) are completely eliminated.**
* **Continuous Talent Pipeline:**
  Junior engineers in the training triad master specification modeling, invariant construction, and agent steering through direct apprenticeship on real production services.
* **Flexible Enterprise Deployment:**
  Organizations deploy specialized teams of 3 regular senior triads for mission-critical core platforms, while utilizing standard 9-person pods (2 regular + 1 junior) for ongoing feature development.

---

## 🎯 The Two-Team Management & Governance Layer

To maintain overarching architectural cohesion and strategic alignment, management oversight is structured across **pairs of teams**:

```
                ┌───────────────────────────────────────┐
                │        LEADERSHIP PAIR (2 TEAMS)      │
                │  • 1 Dedicated Product Manager        │
                │  • 1 Dedicated Engineering Manager    │
                └───────────────────┬───────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
       ┌─────────────────────────┐     ┌─────────────────────────┐
       │     SDSD TEAM ALPHA     │     │     SDSD TEAM BETA      │
       │  (9 Engineers / 3 Triads│     │  (9 Engineers / 3 Triads│
       └─────────────────────────┘     └─────────────────────────┘
```

* **1 Dedicated Product Manager:** Oversees strategic product portfolio roadmap, cross-pod customer priorities, and executive stakeholder alignment.
* **1 Dedicated Engineering Manager:** Provides cross-aggregate architectural governance, audits API contracts, manages operational infrastructure, and leads talent development and performance coaching.
