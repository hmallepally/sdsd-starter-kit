# Repository Instructions: Spec-Driven Secure Development (SDSD)

## Operational Axioms for AI Coding Agents:
1. **Never Touch Code Directly Without a Specification:** Every code change must trace to an approved specification file in `/specs/`.
2. **TDD is Mandatory:** You must write failing unit/contract tests verifying the specification's invariants BEFORE generating any implementation code.
3. **Respect Blast Radius:** You are strictly forbidden from modifying any file listed in the specification's `Untouchable Files` section.
4. **Never Bypass Security Invariants:** All negative constraints defined in the spec must be verified with dedicated adversarial tests.
5. **No Hallucinated Refactoring:** Do not 'clean up' or refactor unrelated files outside the spec's blast radius.
