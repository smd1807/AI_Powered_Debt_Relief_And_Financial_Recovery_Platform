# Epic 4: Frontend Integration & User Interface Development

**Status:** ✅ Complete — 4/4 stories
**Stack:** React + Vite, Axios, Recharts, custom CSS-variable dark theme

## Story 1 — User Interface Development
Built every page of the app with a dark, professional theme: Login/Register,
Dashboard, Financial Health, Loans, Settlement Predictor, Negotiation,
Know Your Rights, and History. Verified visually in-browser (Vite dev
server at `localhost:5173`/`5174`) before any backend wiring existed.

## Story 2 — Frontend Communicates with FastAPI
- `src/api/client.js` — central Axios instance with:
  - A **request interceptor** that attaches the JWT bearer token from
    `localStorage` to every outgoing call
  - A **response interceptor** that catches `401`s, clears the stale
    token, and redirects to `/login` automatically
- `src/api/AuthContext.jsx` + `ProtectedRoute.jsx` — route guarding for
  authenticated pages
- Fixed a bug where a successful login didn't redirect to the dashboard
  (`Login.jsx` now calls `navigate("/")` and auto-redirects if already
  authenticated)
- Fixed a bug where the Dashboard showed a stale `financial_health_score`
  and `existing_debts` snapshot after adding a loan — both are now
  computed live on every request (`app/routers/financial_profiles.py`)

## Story 3 — Financial Health Metrics & Settlement Data Visualization
Verified end-to-end against real backend data:
- Dashboard cards (Health Score, Total Outstanding Debt, Debt-to-Income
  Ratio, Monthly Surplus) update live as loans/profile change
- Recharts bar chart ("Outstanding Debt by Lender") and a debt-repayment
  timeline simulation with an "extra monthly payment" input
- Settlement Predictor page (per-loan % + risk badge)
- Negotiation page (AI strategy + settlement letter, both fallback-labeled)
- Know Your Rights page (RBI-aligned borrower protections)

## Story 4 — UI Enhancements
- Audited the CSS-variable theme against the SkillWallet reference
  palette; kept the existing scheme (functionally equivalent — dark,
  consistent, variable-driven)
- Added a fully working **mobile hamburger menu** (`Navbar.jsx` +
  `index.css` media query at `≤860px`) — previously the nav stacked
  seven links vertically above the page content on mobile, which is now
  collapsed behind a ☰ toggle that auto-closes on navigation
- Verified in Chrome DevTools' mobile emulator (iPhone 12 Pro / 400px width)

## Outcome
All 4 stories complete and verified live in the browser at every step,
not just built-but-untested.
