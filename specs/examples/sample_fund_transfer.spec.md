# SPEC-001: Idempotent Account Fund Transfer Service

> **Status:** `APPROVED (Human Gate 1 Signed)`  
> **Component:** `core/billing/transfer`  
> **Risk Classification:** `CRITICAL FINANCIAL`  
> **Target Cycle Cadence:** `35 Minutes`  
> **Authors:** Product Specialist (Jane Doe) & Specification Engineer (Harinath Mallepally)

---

## 1. Context & Business Intent

### Problem Statement
Customers occasionally experience network timeouts when executing domestic peer-to-peer or B2B fund transfers. If the user clicks "Submit" multiple times or the client retries over flaky cellular networks, duplicate debit transactions can occur, causing overdrafts and financial reconciliation discrepancies.

### Target Outcome
Provide an atomic, idempotent fund transfer service between accounts within the same organization. Duplicate requests with the same `idempotency_key` within a 24-hour window must return the original transaction receipt without re-executing balance mutations.

---

## 2. Domain State Machine

```
                      ┌──────────────────────┐
                      │      INITIATED       │
                      └──────────┬───────────┘
                                 │
                     [Validate Balances & Limits]
                                 │
                                 ▼
                      ┌──────────────────────┐
            ┌─────────┤      VALIDATED       ├─────────┐
            │         └──────────┬───────────┘         │
    [System Error]               │               [Insufficient]
            │          [Execute Atomic Ledger]         │
            ▼                    │                     ▼
┌──────────────────────┐         ▼          ┌──────────────────────┐
│        FAILED        │  ┌──────────────┐  │       REJECTED       │
└──────────────────────┘  │  COMPLETED   │  └──────────────────────┘
                          └──────────────┘
```

### Transition Invariants
- `INITIATED -> VALIDATED`: Permitted only if `source_account.status == ACTIVE` and `dest_account.status == ACTIVE`.
- `VALIDATED -> COMPLETED`: Permitted only if atomic debit of source and credit of destination succeed in a single database transaction.
- `INITIATED -> REJECTED`: Triggered if `source_account.available_balance < transfer_amount + fee`.
- `INITIATED -> FAILED`: Triggered if external ledger service is unreachable after 3 exponential backoff attempts.

---

## 3. Mathematical & Domain Invariants

* **Invariant 1 (Conservation of Capital):**
  $$\Delta \text{Balance}(\text{Source}) + \Delta \text{Balance}(\text{Destination}) = 0$$
  At no point may money be created or destroyed during a transfer.
* **Invariant 2 (Non-Negative Balance Rule):**
  $$\text{SourceAccount.available\_balance} \ge 0 \quad \forall t$$
  The service must reject any transfer that would reduce available balance below zero (unless an explicit pre-approved overdraft facility is attached).
* **Invariant 3 (Idempotency Contract):**
  For any request $R$ with key $K$, if $R$ is received at time $t_2$ where $t_2 - t_1 < 24\text{ hours}$ and $R(K, t_1)$ was processed, the service must return the stored receipt of $R(K, t_1)$ with HTTP status `200 OK` and must **not** execute additional ledger mutations.

---

## 4. Threat Model & Security Boundaries (Negative Constraints)

1. **Negative Constraint 1 (No Cross-Tenant Transfers):**
   The service must NEVER allow a transfer where `source_account.tenant_id != dest_account.tenant_id` unless the transfer is flagged as an authorized inter-tenant clearing operation with cryptographic proof.
2. **Negative Constraint 2 (Zero PII/Financial Secrets in Logs):**
   The service must NEVER write bank account numbers, tax IDs, or full card details to standard application logs. Only tokenized account IDs (`act_tok_xxxx`) may be logged.
3. **Negative Constraint 3 (Strict Parameterization):**
   All SQL / database queries must use bound parameters; dynamic string concatenation is strictly forbidden.
4. **Negative Constraint 4 (Rate Limiting):**
   A maximum of 5 transfer requests per account per minute is permitted. Excess requests must receive HTTP `429 Too Many Requests`.

---

## 5. Blast-Radius Boundary Envelope

Autonomous agents generating code for this feature are strictly bound by the following path rules:

### Allowed Files (May Create or Edit):
- `src/domain/billing/transfer_service.py` (or `.ts` / `.go`)
- `src/domain/billing/transfer_model.py`
- `tests/unit/billing/test_transfer_service.py`
- `tests/unit/billing/test_transfer_idempotency.py`

### Forbidden Baseline (Untouchable Files — Any Edit Fails CI):
- `src/auth/**` (Authentication middleware)
- `schema/migrations/**` (Database migrations)
- `config/production.env` (Infrastructure configuration)
- `.github/**` (CI/CD pipelines)

---

## 6. Executable Test Matrix (Red TDD Contract)

| Test ID | Scenario | Input Conditions | Expected Assertion / Behavior |
|:---|:---|:---|:---|
| `TC-TR-001` | Happy path transfer | Valid accounts, source has \$500, transfer \$100 | Source: \$400, Dest: +\$100, Status: `COMPLETED` |
| `TC-TR-002` | Insufficient funds | Source has \$50, transfer \$100 | Throws `InsufficientFundsException`, zero balance change |
| `TC-TR-003` | Idempotent replay | Repeat `TC-TR-001` with same `idempotency_key` | Returns identical receipt, balances unchanged |
| `TC-TR-004` | Cross-tenant breach | Source `tenant_id=A`, Dest `tenant_id=B` | Throws `TenantIsolationBreachException`, logs security alert |
| `TC-TR-005` | Zero / Negative amount | Amount = \$0 or -\$50 | Throws `InvalidTransferAmountException` |
| `TC-TR-006` | Inactive destination | Dest account has `status=FROZEN` | Throws `AccountNotActiveException`, zero debit |

---

## 7. Human Gate 1 Sign-Off

- [x] **Product Specialist Sign-Off:** Business intent, state model, and idempotency window verified. (Signed: Jane Doe, 2026-09-29)
- [x] **Specification Engineer Sign-Off:** Threat invariants, negative constraints, and blast radius locked. (Signed: Harinath Mallepally, 2026-09-29)
- [x] **Blast Radius Locked:** Allowed files strictly confined to `billing/transfer*`.
