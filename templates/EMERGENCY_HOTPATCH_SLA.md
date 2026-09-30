# Emergency Hot-Patch SLA & Remediation Protocol

> **Purpose:** Reconciles the realities of critical production incidents (P1 / SEV1 outages) with the SDSD Disposable Code Axiom.

---

## 1. The Operational Reality
During an active production outage at 2:00 AM, system restoration takes precedence over formal specification authoring. Engineers are explicitly permitted to manually hot-patch production code to restore service.

However, unchecked hot-patching creates instant **Spec Drift**, guaranteeing future hallucination regressions when autonomous agents next modify the codebase.

---

## 2. The 24-Hour Spec Remediation Protocol

### Phase A: Incident Declaration & Emergency Deploy
1. The incident commander flags the emergency PR with the label: `HOTPATCH-P1`.
2. The CI/CD pipeline permits the deploy, but automatically:
   - Sets a repository status: `SPEC-DRIFT-ACTIVE`.
   - Opens an automated tracking issue: `SPEC-REMEDIATION-SLA: <Incident-ID>`.
   - Starts a strict **24-hour countdown timer**.

### Phase B: Post-Incident Spec Synchronization (Within 24 Hours)
1. Within 24 hours of incident mitigation, the on-call engineer or pod must:
   - Reverse-engineer the root cause and the hot-patch into the relevant specification contract (`specs/SPEC-XXX.md`).
   - Add the specific failure condition as a permanent **Negative Constraint** and **Regression Test Case**.
   - Command the Developer Agent to regenerate the clean implementation from the amended specification.
2. Verify that the regenerated code cleanly passes all invariant checks and reproduces the hot-patch fix cleanly within architectural boundaries.

### Phase C: Re-synchronization & Gate Release
1. Submit PR linking to the remediation issue.
2. The CI/CD pipeline validates that:
   - `specs/SPEC-XXX.md` has been updated with the incident invariant.
   - All tests pass.
   - Blast radius is restored.
3. The repository clears `SPEC-DRIFT-ACTIVE`, restoring normal deploy gates.

---

## 3. SLA Enforcement Policy
If a `HOTPATCH-P1` is not remediated into the specification within 24 hours:
- Non-emergency CI/CD deployments are blocked automatically.
- Executive escalation is triggered to the engineering leadership team.
