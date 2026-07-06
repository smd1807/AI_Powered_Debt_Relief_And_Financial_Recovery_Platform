# Project Workflow — FinRelief AI

> Matches the official "Project Flow" epic → "Project Workflow" task
> description on SkillWallet exactly.

## Overview

The AI Powered Debt Relief & Financial Recovery Platform follows a
structured full-stack development workflow designed for intelligent debt
management and financial recovery automation. The platform integrates
**React.js** frontend services, **FastAPI** backend APIs, **SQLite**
database management, and **Google Gemini AI** integration to analyze
borrower financial profiles, predict settlements, and generate
AI-powered negotiation strategies through a secure, responsive, and
scalable web application.

## High-level architecture

```
   ┌──────────────┐      ┌──────────────────┐      ┌────────────────────┐
   │   Frontend    │ HTTP │      Backend      │  ORM │      Database       │
   │ React + Vite  │◄────►│  FastAPI (Python) │◄────►│  SQLite (SQLAlchemy)│
   └──────────────┘      └──────────────────┘      └────────────────────┘
                                   │
                                   ▼
                         ┌───────────────────────┐
                         │   Google Gemini API    │
                         │  (negotiation strategy, │
                         │   settlement letters)   │
                         └───────────────────────┘
```

## Full Epic & Story Breakdown

### Epic 1. FinRelief AI Application Development & System Setup
- Story 1: Python Backend Environment Setup
- Story 2: Backend Dependency Installation Using Requirements.txt
- Story 3: Frontend Setup (React.js + Vite)
- Story 4: Project Structure & Full-Stack Directory Organization

### Epic 2. AI Integration & Financial Processing Setup
- Story 1: FastAPI Backend & API Endpoints
- Story 2: Financial Engine Module
- Story 3: Settlement Prediction System
- Story 4: AI Negotiation Strategy Engine
- Story 5: Fallback Logic Implementation

### Epic 3. Database Management & Financial Data Storage Setup
- Story 1: API Development Functionality
- Story 2: Loan & Settlement Processing Functionality
- Story 3: Data Handling

### Epic 4. Frontend Integration & User Interface Development
- Story 1: User Interface Development
- Story 2: Frontend Communication With FastAPI
- Story 3: Financial Health Metrics & Settlement Data Visualization
- Story 4: UI Enhancements

### Epic 5. Testing, Debugging & Performance Optimization
- Story 1: System Testing
- Story 2: Backend Error Handling & AI Fallback Management
- Story 3: Performance Optimization & Secure Session Management

### Epic 6. Version Control, Project Finalization & Deployment Readiness
- Story 1: GitHub Repository Setup & Version Control Management
- Story 2: Project Cleanup & Modular Folder Structure Organization
- Story 3: Deployment Configuration & Production Readiness Setup

## End-to-end user journey (functional flow)

1. **Register** — borrower creates an account (Users entity).
2. **Add loans** — borrower logs each loan/debt with a lender (Loans entity).
3. **Build financial profile** — Financial Engine calculates DTI ratio,
   disposable income, and a financial health score (Financial_Profiles entity).
4. **Predict settlement** — Settlement Prediction System estimates a
   realistic settlement percentage and priority level per loan
   (Settlement_Records entity).
5. **Generate negotiation strategy** — AI Negotiation Strategy Engine
   (Google Gemini, with automatic rule-based Fallback Logic) produces a
   negotiation approach and a settlement letter (AI_History entity).
6. **Review on dashboard** — the React frontend visualizes health score,
   debt breakdown, settlement predictions, and negotiation output.

## Mapping to the codebase (current build status)

| Epic | Status | Where it lives |
|---|---|---|
| Epic 1 | ✅ Built & tested | `backend/` (FastAPI + SQLAlchemy skeleton), `frontend/` (React + Vite skeleton) |
| Epic 2 | ✅ Built & tested | `backend/app/services/financial_engine.py`, `settlement_prediction.py`, `negotiation_engine.py` (Gemini), `fallback.py` |
| Epic 3 | ✅ Built & tested | `backend/app/models.py`, `database.py`, all router CRUD endpoints |
| Epic 4 | ✅ Built & tested | `frontend/src/pages/*`, `frontend/src/api/client.js`, `Charts.jsx` |
| Epic 5 | 🔶 Partially built | `tests/test_api.py` (9 passing), global exception handler in `main.py`, automatic Gemini→fallback degradation. **JWT session management still to be added.** |
| Epic 6 | ⬜ Not started yet | `.gitignore` exists; GitHub push, cleanup pass, and deployment config still pending |
