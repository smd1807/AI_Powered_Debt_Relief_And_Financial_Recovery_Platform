"""
System Testing (Epic 5)

End-to-end journey through the exact required endpoint set:
/register -> /login -> /add-loan -> /update-profile -> /settlement-predictor
-> /ai-negotiation-strategy -> /generate-negotiation-email/{loan_id}
-> /ai-history -> /dashboard-data -> /financial-health -> /debt-timeline
-> /delete-loan/{loan_id}

Run with:
    pytest -v
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
def registered_user():
    response = client.post(
        "/register",
        json={"name": "Test User", "email": "testuser@example.com", "password": "SuperSecret123"},
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="module")
def access_token(registered_user):
    response = client.post(
        "/login", json={"email": "testuser@example.com", "password": "SuperSecret123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def created_loan(access_token):
    response = client.post(
        "/add-loan",
        json={
            "lender_name": "HDFC Credit Card",
            "loan_type": "credit_card",
            "loan_amount": 200000,
            "outstanding_amount": 180000,
            "interest_rate": 36,
            "months_overdue": 8,
            "emi": 8000,
        },
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200
    return response.json()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_test_db():
    response = client.get("/test-db")
    assert response.status_code == 200
    assert "Connected" in response.json()["database_status"]


def test_register(registered_user):
    assert registered_user["email"] == "testuser@example.com"


def test_duplicate_register_rejected():
    response = client.post(
        "/register", json={"name": "Dup", "email": "testuser@example.com", "password": "x"}
    )
    assert response.status_code == 400


def test_login_wrong_password_rejected(registered_user):
    response = client.post("/login", json={"email": "testuser@example.com", "password": "wrong"})
    assert response.status_code == 401


def test_login_success(access_token):
    assert access_token is not None


def test_protected_endpoint_requires_auth():
    response = client.get("/loans")
    assert response.status_code == 401


def test_debug_user(access_token):
    response = client.get("/debug-user", headers=auth_headers(access_token))
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"


def test_add_loan(created_loan):
    assert created_loan["lender_name"] == "HDFC Credit Card"


def test_get_loans(access_token, created_loan):
    response = client.get("/loans", headers=auth_headers(access_token))
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_update_profile(access_token):
    response = client.put(
        "/update-profile",
        json={"monthly_income": 50000, "monthly_expenses": 15000},
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["existing_debts"] == 180000
    assert data["health_category"] in ["Low", "Medium", "High"]


def test_dashboard_data(access_token):
    response = client.get("/dashboard-data", headers=auth_headers(access_token))
    assert response.status_code == 200
    assert len(response.json()["loans"]) >= 1


def test_financial_health(access_token):
    response = client.get("/financial-health", headers=auth_headers(access_token))
    assert response.status_code == 200


def test_debt_timeline(access_token):
    response = client.get("/debt-timeline", headers=auth_headers(access_token))
    assert response.status_code == 200
    data = response.json()
    assert "months_to_debt_free" in data
    assert "timeline_preview" in data


def test_settlement_predictor(access_token, created_loan):
    response = client.get(
        f"/settlement-predictor?loan_id={created_loan['loan_id']}",
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200
    data = response.json()[0]
    assert 40 <= data["suggested_settlement_percentage"] <= 75
    assert data["risk_category"] in ["High", "Medium", "Low"]


def test_ai_negotiation_strategy_fallback(access_token, created_loan):
    response = client.get(
        f"/ai-negotiation-strategy?loan_id={created_loan['loan_id']}",
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "fallback"
    assert len(data["negotiation_strategy"]) > 20


def test_ai_negotiation_strategy_friendly_message_when_no_loans():
    """A brand-new user with zero loans should get a friendly guidance
    message instead of a 404 error (Epic 3, Story 1 resilience pattern)."""
    register = client.post(
        "/register",
        json={"name": "No Loans User", "email": "noloans@example.com", "password": "password123"},
    )
    assert register.status_code == 200
    login = client.post("/login", json={"email": "noloans@example.com", "password": "password123"})
    token = login.json()["access_token"]

    response = client.get("/ai-negotiation-strategy", headers=auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert data["loan_id"] is None
    assert "add at least one loan" in data["negotiation_strategy"].lower()


def test_generate_negotiation_email(access_token, created_loan):
    response = client.get(
        f"/generate-negotiation-email/{created_loan['loan_id']}", headers=auth_headers(access_token)
    )
    assert response.status_code == 200
    assert len(response.json()["settlement_letter"]) > 20


def test_ai_history(access_token):
    response = client.get("/ai-history", headers=auth_headers(access_token))
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_delete_loan(access_token, created_loan):
    response = client.delete(
        f"/delete-loan/{created_loan['loan_id']}", headers=auth_headers(access_token)
    )
    assert response.status_code == 200


def test_cleanup():
    # DB file cleanup now happens once, session-wide, in conftest.py —
    # deleting it here would break other test files that share this
    # same database (pytest runs all test modules in one process).
    assert True
    assert True
