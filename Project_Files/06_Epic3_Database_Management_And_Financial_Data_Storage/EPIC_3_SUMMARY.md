# Epic 3: Database Management & Financial Data Storage Setup

**Status:** ✅ Complete
**Stack:** SQLAlchemy ORM over SQLite (swappable to Postgres/MySQL via `DATABASE_URL`)

## Overview
Designed and implemented the relational schema backing every financial
feature in the app: Users, Loans, Financial Profiles, Settlement Records,
and AI History.

## What Was Built
- `app/models.py` — five core tables matching the official ER diagram:
  - `User` (auth + profile ownership)
  - `Loan` (per-lender debt records: amount, EMI, interest, overdue months)
  - `FinancialProfile` (income, expenses, lump sum, computed health score)
  - `SettlementRecord` (historical settlement predictions per loan)
  - `AIHistory` (every negotiation strategy/letter ever generated, with source)
- `app/database.py` — SQLite connection with `check_same_thread=False` for
  safe concurrent request handling, and a `get_db()` FastAPI dependency
  that always closes its session
- Cascading deletes configured (deleting a user cleans up their loans,
  profile, settlement records, and AI history automatically)

## Verification
- 67 backend tests (later grown to 86 across Epics 3–5) exercising loan
  CRUD, profile updates, and settlement/AI-history persistence
- Manually verified via SQLite inspection that foreign-key indexes exist
  on every `user_id`/`loan_id` column (added in Epic 5 for performance)

## Outcome
All 3 stories in this Epic completed. The schema has proven stable across
every later feature (Financial Health, Settlement Predictor, Negotiation,
History) with zero migrations needed beyond the Epic 5 index additions.
