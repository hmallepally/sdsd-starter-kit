# Core Operational Axioms of SDSD

These axioms are non-negotiable operational principles within any Spec-Driven Secure Development (SDSD) repository.

---

### Axiom 1: The Disposable Code Principle
> **Code is an ephemeral, compiled artifact. The specification is the single sacred source of truth.**

- In the pre-AI era, human writing of code was expensive, making the codebase the primary artifact.
- In the SDSD era, syntax generation cost approaches zero.
- When an edge case surfaces or a test fails, **never patch the code directly**. Diagnose the root cause, amend the specification contract, and command the agent to regenerate the implementation.

---

### Axiom 2: Negative Constraint Supremacy
> **Specifying what the system MUST NEVER do is exponentially more protective than specifying what it should do.**

- Hallucinating LLMs readily invent non-existent behaviors or relax security checks unless explicitly constrained.
- Every specification must contain explicit, machine-verifiable negative constraints:
  - *No transaction may proceed without tenant validation.*
  - *No authentication token may be logged in plaintext.*
  - *No state transition may bypass the intermediate verification state.*

---

### Axiom 3: Blast-Radius Enclosure
> **Every feature generation task must have an immutable file-boundary perimeter.**

- Autonomous agents must operate within explicit file-path envelopes (e.g., `src/billing/**`, `tests/unit/billing/**`).
- Untouchable baselines (authentication modules, database migration scripts, infrastructure configs) are formally locked.
- Any unauthorized file modification halts the PR pipeline immediately.

---

### Axiom 4: Epistemic Decoupling (Adversarial Triangulation)
> **An agent must never review its own output, and reviewer agents must be epistemically independent.**

- Sycophancy and shared blind spots occur when the same LLM context generates and verifies code.
- Reviewer agents must use independent model architectures (e.g., Gemini auditing Claude, or separate instances with adversarial system prompts).
- Deterministic linters, SAST tools, and test suites provide objective arbitration.

---

### Axiom 5: Dynamic Triad Reallocation
> **Engineering capacity is modular and dynamic; triads reallocate between greenfield innovation and maintenance without structural friction.**

- Enterprise engineering is not solely about greenfield feature generation; continuous maintenance, telemetry enhancement, and defect resolution consume substantial operational bandwidth.
- Triads represent portable, self-contained atomic units of execution.
- Depending on seasonal demand, operational debt, or strategic pivots, organizations dynamically scale triads up or down across workstreams without reconfiguring organizational hierarchy or introducing handoff delays.

---

### Axiom 6: The Analog Resilience Drill
> **Cognitive muscle and manual software engineering craft must be deliberately exercised to prevent deskilling.**

- Over-reliance on generative AI introduces intellectual atrophy and operational vulnerability in the event of upstream model failure or tooling disruption.
- SDSD mandates periodic "analog sprints" (a 3:1 operational rhythm—3 weeks AI-augmented, 1 week manual—or a mandatory quarterly analog drill).
- During analog exercises, human triads analyze, model, and implement features end-to-end without AI assistance, reinforcing that deep human analysis, systems orchestration, and core engineering craftsmanship remain the paramount assets.

---

### Axiom 7: Universal Legacy Invariant Envelopes
> **Legacy monolithic codebases require the exact same contract guardrails as greenfield systems.**

- In legacy brownfield environments, generative AI poses severe regression risks due to unmapped coupling and tribal knowledge.
- SDSD addresses legacy fear by locking existing files behind untouchable-file perimeters, establishing Strangler-Fig anti-corruption layers, and defining explicit negative constraints before permitting agent modification.
- Agents operate strictly within bounded blast radii, transforming fragile legacy codebases into secure, contractually verified platforms.

