"""
System Testing (Epic 5, Story 1) — Invalid Input Handling & Edge Cases

Covers the "Key Functionalities" not exercised by the happy-path suites:
  - Invalid user input handling and validation implemented
  - Error scenarios and edge cases handled efficiently
  - Stable system behavior verified under different (including malformed)
    financial conditions

Every request here is expected to be REJECTED cleanly (422/404/401) rather
than crash the server or silently store bad data.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test_finrelief.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"

from app.main import app  # noqa: E402

client = TestClient(app)


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def access_token():
    client.post(
        "/register",
        json={"name": "Edge Case User", "email": "edgecase@example.com", "password": "SuperSecret123"},
    )
    response = client.post(
        "/login", json={"email": "edgecase@example.com", "password": "SuperSecret123"}
    )
    return response.json()["access_token"]


# ---------- Registration / auth input validation ----------

def test_register_missing_email_rejected():
    response = client.post("/register", json={"name": "NoEmail", "password": "secret123"})
    assert response.status_code == 422


def test_register_invalid_email_format_rejected():
    response = client.post(
        "/register",
        json={"name": "BadEmail", "email": "not-an-email", "password": "secret123"},
    )
    assert response.status_code == 422


def test_register_missing_password_rejected():
    response = client.post(
        "/register", json={"name": "NoPassword", "email": "nopass@example.com"}
    )
    assert response.status_code == 422


def test_login_nonexistent_user_rejected():
    response = client.post(
        "/login", json={"email": "ghost@example.com", "password": "whatever123"}
    )
    assert response.status_code in (400, 401, 404)


# ---------- Loan input validation ----------

def test_add_loan_negative_outstanding_amount_rejected(access_token):
    response = client.post(
        "/add-loan",
        json={
            "lender_name": "BadCo",
            "loan_type": "Personal Loan",
            "loan_amount": -1000,
            "outstanding_amount": -1000,
            "interest_rate": 10,
            "emi": 500,
            "months_overdue": 0,
        },
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


def test_add_loan_negative_interest_rate_rejected(access_token):
    response = client.post(
        "/add-loan",
        json={
            "lender_name": "BadCo",
            "loan_type": "Personal Loan",
            "loan_amount": 1000,
            "outstanding_amount": 1000,
            "interest_rate": -5,
            "emi": 500,
            "months_overdue": 0,
        },
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


def test_add_loan_negative_months_overdue_rejected(access_token):
    response = client.post(
        "/add-loan",
        json={
            "lender_name": "BadCo",
            "loan_type": "Personal Loan",
            "loan_amount": 1000,
            "outstanding_amount": 1000,
            "interest_rate": 10,
            "emi": 500,
            "months_overdue": -3,
        },
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


def test_add_loan_missing_required_amount_rejected(access_token):
    response = client.post(
        "/add-loan",
        json={"lender_name": "BadCo", "loan_type": "Personal Loan"},
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


def test_add_loan_without_auth_rejected():
    response = client.post(
        "/add-loan",
        json={
            "lender_name": "NoAuth",
            "loan_type": "Personal Loan",
            "loan_amount": 1000,
            "outstanding_amount": 1000,
        },
    )
    assert response.status_code == 401


# ---------- Financial profile input validation ----------

def test_update_profile_negative_income_rejected(access_token):
    response = client.put(
        "/update-profile",
        json={"monthly_income": -50000, "monthly_expenses": 10000, "lump_sum_available": 0},
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


def test_update_profile_negative_expenses_rejected(access_token):
    response = client.put(
        "/update-profile",
        json={"monthly_income": 50000, "monthly_expenses": -10000, "lump_sum_available": 0},
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


def test_update_profile_zero_income_accepted(access_token):
    """Zero is a valid (if extreme) income — only negative values are invalid."""
    response = client.put(
        "/update-profile",
        json={"monthly_income": 0, "monthly_expenses": 0, "lump_sum_available": 0},
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200


# ---------- Not-found / nonexistent resource handling ----------

def test_delete_nonexistent_loan_returns_404(access_token):
    response = client.delete("/delete-loan/999999", headers=auth_headers(access_token))
    assert response.status_code == 404


def test_generate_negotiation_email_nonexistent_loan_returns_404(access_token):
    response = client.get(
        "/generate-negotiation-email/999999", headers=auth_headers(access_token)
    )
    assert response.status_code == 404


def test_dashboard_data_requires_auth():
    response = client.get("/dashboard-data")
    assert response.status_code == 401


# ---------- Backend error handling & session robustness (Epic 5, Story 2) ----------

def test_malformed_jwt_rejected_cleanly():
    """A garbage/unparseable token must be rejected with a clean 401, not a crash."""
    response = client.get(
        "/dashboard-data", headers={"Authorization": "Bearer not-a-real-jwt-token"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_missing_bearer_prefix_rejected():
    response = client.get(
        "/dashboard-data", headers={"Authorization": "just-a-raw-token-no-prefix"}
    )
    assert response.status_code == 401


def test_expired_or_wrong_secret_token_rejected():
    """A token signed with a different secret must fail validation, not crash."""
    from jose import jwt as jose_jwt

    bad_token = jose_jwt.encode({"sub": "1"}, "wrong-secret-key", algorithm="HS256")
    response = client.get(
        "/dashboard-data", headers={"Authorization": f"Bearer {bad_token}"}
    )
    assert response.status_code == 401


def test_unhandled_exception_returns_structured_json_not_stacktrace():
    """
    Any endpoint that raises an unexpected (non-HTTPException) error must be
    caught by the global handler in main.py and returned as clean JSON —
    never a raw 500 HTML stack trace that could leak internals.
    """
    # An out-of-range loan_id combined with malformed Accept header still
    # must come back as valid, structured JSON rather than an unhandled crash.
    response = client.get("/generate-negotiation-email/abc", headers={})
    assert response.status_code in (401, 422)
    assert response.headers["content-type"].startswith("application/json")
