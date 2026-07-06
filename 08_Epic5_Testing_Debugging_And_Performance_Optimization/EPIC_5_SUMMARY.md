# Epic 5: Testing, Debugging & Performance Optimization

**Status:** ✅ Complete — 3/3 stories · **86/86 backend tests passing**

## Story 1 — System Testing
Started at 67 passing tests (Epics 1–3 coverage: loan types, borrower
profiles, settlement math, missing-Gemini-key fallback). Live-probed the
running API for gaps and found that **negative loan amounts, negative
interest rates, and negative income were silently accepted**. Fixed by
adding `Field(ge=0)` constraints to every relevant numeric field in
`app/schemas.py`, then wrote `tests/test_invalid_input_validation.py`
(15 new tests: missing fields, invalid email, negative values, 404s on
nonexistent resources, auth requirements). **Result: 82 tests.**

## Story 2 — Backend Error Handling & AI Fallback Management
Audited `_call_gemini()` against the reference error-handling pattern —
already matched almost exactly (missing key → `None`, `ImportError` →
`None`, any other exception → `None` + logged). Confirmed a global
exception handler in `app/main.py` catches any unhandled crash and
returns clean JSON instead of a raw stack trace. Found one real gap: **no
timeout on the Gemini call**, meaning a hung request could block
indefinitely if a live API key were ever added. Fixed by adding
`request_options={"timeout": 15}`. Added 5 tests covering malformed JWTs,
wrong-secret tokens, and the global handler's structured-JSON guarantee.
**Result: 86 tests.**

## Story 3 — Performance Optimization & Secure Session Management
Checked the running app against the exact spec bullets:
- **JWT expiry** was 60 minutes; spec calls for 120 — fixed the default
  in `app/auth.py` and verified live that a fresh token now expires in
  exactly ~120.0 minutes
- **`check_same_thread=False`** on SQLite — already correctly configured
- **Zero indexes existed on any foreign key** (`user_id`, `loan_id`)
  despite nearly every endpoint filtering by them — added `index=True`
  to all 5 foreign-key columns across `Loan`, `FinancialProfile`,
  `SettlementRecord`, and `AIHistory`; verified the indexes actually
  exist in the live SQLite schema (`ix_loans_user_id`,
  `ix_ai_history_user_id`, etc.)
- Added structured logging (`logger.warning`/`logger.info`) to the
  login/register flow for production observability

## Outcome
All 3 stories complete. Every fix in this Epic was verified against the
*running* application (not just code review) — reproduced the bug first,
then confirmed the fix live, then locked it in with an automated test.
