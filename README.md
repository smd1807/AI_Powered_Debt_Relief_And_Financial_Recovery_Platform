# FinRelief AI

**AI-Powered Debt Relief & Financial Recovery Platform**

🔗 **Live Demo:** [ai-powered-debt-relief-and-financia-three.vercel.app](https://ai-powered-debt-relief-and-financia-three.vercel.app)

An AI-powered web platform for automated debt analysis, settlement prediction, and negotiation support. Built for the SkillWallet Google Cloud Generative AI program.

---

## Overview

FinRelief AI helps borrowers understand their financial health, predict realistic debt settlements, and generate negotiation strategies with lenders. The platform pairs a rule-based financial engine with Google Gemini AI, falling back gracefully to rule-based logic when the AI service is unavailable.

## Features

- Secure user authentication and loan management
- Live financial health dashboard — DTI ratio, surplus, stress level
- Debt payoff timeline projection
- Settlement prediction and AI-generated negotiation strategies
- Automated settlement letter generation
- Borrower rights and education resources

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, SQLite, JWT |
| Frontend | React, Vite |
| AI | Google Gemini API |
| Testing | Pytest — 86 passing tests |
| Deployment | Render (backend), Vercel (frontend) |

## Team

Kureti Sai Meghana · Ananya Lakshmi Tanneru · Ch Nikhil Kumar · Rehan Shaik · Rukhya Muskan Shaik

## Setup

```bash
# Backend
cd 9_Project_Files/backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd 9_Project_Files/frontend
npm install
npm run dev
```

---

*Built as part of the SmartBridge / SkillWallet Google Cloud Generative AI program.*
