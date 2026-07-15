"""
Integration tests for Loan & Settlement Processing Functionality
(Epic 3, Story 2) — proves the full pipeline works together:
  1. Loan records stored/retrieved via SQLAlchemy ORM
  2. Settlement percentage calculated from loan data
  3. High/Medium/Low priority assigned per loan
  4. Negotiation letters generated with lender-specific content

This exercises the real database (via the FastAPI TestClient), not
mocks, to prove the full loan -> settlement -> negotiation pipeline.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

# Reuses whichever DATABASE_URL is already active for this test session
# (set by test_api.py) — pytest runs all test modules in one process, so
# app.main / app.database are only ever imported (and their engine bound)
# once. Setting a different DB here would create a mismatch once other
# test files clean up their database file.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_finrelief.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from app.main import app  # noqa: E402

client = TestClient(app)


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def token():
    client.post(
        "/register",
        json={"name": "Loan Pipeline User", "email": "loanpipeline@example.com", "password": "password123"},
    )
    login = client.post(
        "/login", json={"email": "loanpipeline@example.com", "password": "password123"}
    )
    return login.json()["access_token"]


def test_loan_record_stored_and_retrieved_via_orm(token):
    create = client.post(
        "/add-loan",
        json={
            "lender_name": "Axis Bank",
            "loan_type": "personal_loan",
            "loan_amount": 150000,
            "outstanding_amount": 120000,
            "interest_rate": 14,
            "months_overdue": 4,
            "emi": 6000,
        },
        headers=auth_headers(token),
    )
    assert create.status_code == 200
    loan_id = create.json()["loan_id"]

    fetched = client.get("/loans", headers=auth_headers(token))
    assert fetched.status_code == 200
    ids = [l["loan_id"] for l in fetched.json()]
    assert loan_id in ids


def test_settlement_percentage_calculated_from_loan_data(token):
    loans = client.get("/loans", headers=auth_headers(token)).json()
    loan_id = loans[0]["loan_id"]

    prediction = client.get(
        f"/settlement-predictor?loan_id={loan_id}", headers=auth_headers(token)
    )
    assert prediction.status_code == 200
    data = prediction.json()[0]
    assert 40 <= data["suggested_settlement_percentage"] <= 75


def test_priority_level_assigned_high_medium_or_low(token):
    loans = client.get("/loans", headers=auth_headers(token)).json()
    loan_id = loans[0]["loan_id"]

    prediction = client.get(
        f"/settlement-predictor?loan_id={loan_id}", headers=auth_headers(token)
    )
    data = prediction.json()[0]
    assert data["risk_category"] in ["High", "Medium", "Low"]


def test_negotiation_letter_generated_with_lender_specific_content(token):
    loans = client.get("/loans", headers=auth_headers(token)).json()
    loan_id = loans[0]["loan_id"]
    lender_name = loans[0]["lender_name"]

    email = client.get(f"/generate-negotiation-email/{loan_id}", headers=auth_headers(token))
    assert email.status_code == 200
    letter = email.json()["settlement_letter"]
    assert lender_name in letter
    assert "Loan Pipeline User" in letter


def test_full_pipeline_loan_to_negotiation(token):
    """One loan flows all the way through: create -> predict -> negotiate."""
    create = client.post(
        "/add-loan",
        json={
            "lender_name": "ICICI Bank",
            "loan_type": "credit_card",
            "loan_amount": 80000,
            "outstanding_amount": 75000,
            "interest_rate": 32,
            "months_overdue": 6,
            "emi": 3500,
        },
        headers=auth_headers(token),
    )
    loan_id = create.json()["loan_id"]

    settlement = client.get(
        f"/settlement-predictor?loan_id={loan_id}", headers=auth_headers(token)
    ).json()[0]
    # overdue (+20) + high interest >12% (+10) = risk_score 30 -> Medium (needs >=40 for High)
    assert settlement["risk_category"] == "Medium"

    strategy = client.get(
        f"/ai-negotiation-strategy?loan_id={loan_id}", headers=auth_headers(token)
    ).json()
    assert strategy["loan_id"] == loan_id

    letter = client.get(
        f"/generate-negotiation-email/{loan_id}", headers=auth_headers(token)
    ).json()
    assert "ICICI Bank" in letter["settlement_letter"]
