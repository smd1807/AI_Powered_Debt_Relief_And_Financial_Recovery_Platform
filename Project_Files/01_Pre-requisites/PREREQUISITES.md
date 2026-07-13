# Pre-requisites — FinRelief AI

> Matches the official "Pre-requisites" task description on SkillWallet
> exactly: the tools, frameworks, libraries, and learning materials
> required for environment setup, frontend/backend development, database
> management, AI integration, authentication, and overall implementation.

## Core Stack & Resources

**Python 3.11+** — Core programming language used to build the application
backend, manage APIs, financial processing logic, and AI-powered
negotiation modules.
https://www.python.org/downloads/

**FastAPI Documentation** — High-performance Python web framework used to
create REST APIs for frontend-backend communication, authentication,
financial processing, and AI integration services.
https://fastapi.tiangolo.com/

**React.js Documentation** — Frontend JavaScript library used to build the
responsive borrower dashboard and interactive user interface components.
https://react.dev/

**Vite Documentation** — Modern frontend build tool used for fast React.js
development, hot reload functionality, and optimized production builds.
https://vitejs.dev/

**Google Gemini API** — AI service used for generating intelligent
negotiation strategies, settlement recommendations, and lender-specific
negotiation letters.
https://aistudio.google.com/app/apikey

**SQLAlchemy ORM Documentation** — Python ORM library used for database
management, model creation, and relational data handling within the
platform.
https://www.sqlalchemy.org/

**SQLite Documentation** — Lightweight relational database used to
securely store borrower information, loan details, settlement records,
and AI history data.
https://www.sqlite.org/docs.html

**Git Version Control** — Source code management system used for tracking
project changes, version history, and collaborative development
workflows.
https://git-scm.com/doc

**GitHub Repository Hosting** — Cloud-based repository platform used for
project hosting, version control, and source code management.
https://github.com/

**Python Virtual Environment (venv)** — Environment isolation tool used
to manage Python dependencies separately and maintain stable package
versions across development setups.
https://docs.python.org/3/library/venv.html

**Visual Studio Code** — Recommended development environment used for
coding, debugging, API testing, and project management.
https://code.visualstudio.com/

**JWT Authentication Documentation** — Secure authentication mechanism
used for protected API access and user session management.
https://jwt.io/

## Setup Checklist

- [ ] Install Python 3.11+
- [ ] Install Node.js 18+ (for React + Vite)
- [ ] Install Git
- [ ] Create a GitHub repository for the project
- [ ] `cd backend && python3 -m venv venv && source venv/bin/activate`
- [ ] `pip install -r requirements.txt`
- [ ] Get a Google Gemini API key from https://aistudio.google.com/app/apikey
- [ ] `cp .env.example .env` and paste the Gemini key into `LLM_API_KEY`
      (set `LLM_PROVIDER=gemini`)
- [ ] `uvicorn app.main:app --reload` → confirm http://localhost:8000/docs loads
- [ ] `cd frontend && npm install`
- [ ] `cp .env.example .env`
- [ ] `npm run dev` → confirm http://localhost:5173 loads and connects to the backend

> Note: the project runs completely end-to-end even without a Gemini key —
> the AI Negotiation Strategy Engine automatically falls back to a
> rule-based engine (see Epic 2 / Epic 5) so the app is demoable with zero
> external accounts if needed.
