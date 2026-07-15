# Epic 2: AI Integration & Financial Processing Setup

**Status:** ✅ Complete
**Stack:** Google Gemini API (`google-generativeai`) with a rule-based fallback engine

## Overview
Integrated AI-generated negotiation strategy and settlement-letter
generation, backed by a Google Gemini call that gracefully degrades to a
deterministic, rule-based fallback engine whenever a live API key isn't
configured (which is the default state of this project).

## What Was Built
- `app/services/negotiation_engine.py::_call_gemini()` — calls Gemini
  1.5-flash if `GOOGLE_API_KEY` is set; returns `None` on missing key,
  `ImportError`, or any other exception so the caller can fall through to
  the fallback engine
- `app/services/fallback.py` — deterministic negotiation strategy and
  settlement-letter generator, used whenever Gemini is unavailable
- `app/services/settlement_prediction.py` — settlement-percentage and
  risk-category calculation based on overdue months, interest rate, EMI
  burden, and debt-to-income ratio (clamped between 40–75%)
- Every AI response — whether from Gemini or the fallback — is logged to
  `AIHistory` with a `source` field (`"llm"` or `"fallback"`) for full
  transparency

## Verification
- `tests/test_negotiation_engine.py`, `tests/test_fallback_logic.py`,
  `tests/test_settlement_prediction.py` — cover missing-API-key behavior,
  fallback stability across repeated calls, and settlement-bound clamping
- Live-tested in the browser: Settlement Predictor correctly returned
  **65% (~₹52,000)** with a **High** risk badge for a sample ₹80,000 loan;
  Negotiation page generated both a negotiation strategy and a full
  settlement letter, both explicitly labeled `SOURCE: FALLBACK`

## Outcome
All 5 stories in this Epic completed. The AI layer works correctly with
or without a live Gemini key — a deliberate design choice so the app is
demoable and reliable out of the box.
