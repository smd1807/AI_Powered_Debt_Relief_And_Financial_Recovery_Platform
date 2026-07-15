"""
FinRelief AI — FastAPI Backend Entrypoint (Epic 2 / Epic 3)

Run with:
    uvicorn app.main:app --reload

Interactive API docs available at /docs once running — click "Authorize"
after logging in via /login to unlock the protected endpoints.
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database import Base, engine
from app import models  # noqa: F401 (ensures models are registered before create_all)
from app.routers import auth, loans, financial_profiles, settlements, ai_history

load_dotenv()

# Creates all tables on startup if they don't already exist.
Base.metadata.create_all(bind=engine)
print("✅ Database Tables Created Successfully")

app = FastAPI(
    title="FinRelief AI",
    description="AI Powered Debt Relief & Financial Recovery Platform",
    version="0.1.0",
)

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:3000", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Global error handling (Epic 5) ----------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all so an unexpected error never returns a raw 500 stack trace
    to the frontend — always a clean, predictable JSON error shape.
    """
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on the server.", "error": str(exc)},
    )


# ---------- Routers ----------
app.include_router(auth.router)
app.include_router(loans.router)
app.include_router(financial_profiles.router)
app.include_router(settlements.router)
app.include_router(ai_history.router)


# ---------- Root Route ----------
@app.get("/")
def read_root():
    return {"message": "Welcome to FinRelief AI 🚀", "status": "running"}


# ---------- Test Database Connection ----------
@app.get("/test-db")
def test_db():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"database_status": "Connected ✅"}
