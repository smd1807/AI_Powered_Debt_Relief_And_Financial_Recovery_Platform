"""
Integration tests for Data Handling (Epic 3, Story 3) — proves:
  1. Structured loan/user data is correctly stored and retrieved from SQLite
  2. Query retrieval is correctly scoped per user session (no data leakage
     between different users' loans/profiles/AI history)
  3. JWT token-based authentication protects every protected route
  4. The lump_sum_available field round-trips correctly through the
     Financial_Profile
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_finrelief.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from app.main import app  # noqa: E402

client = TestClient(app)


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register_and_login(name, email, password="password123"):
    client.post("/register", json={"name": name, "email": email, "password": password})
    login = client.post("/login", json={"email": email, "password": password})
    return login.json()["access_token"]


@pytest.fixture(scope="module")
def user_a_token():
    return _register_and_login("User A", "usera_datahandling@example.com")


@pytest.fixture(scope="module")
def user_b_token():
    return _register_and_login("User B", "userb_datahandling@example.com")


def test_loan_data_persists_correctly_in_sqlite(user_a_token):
    create = client.post(
        "/add-loan",
        json={
            "lender_name": "Kotak Bank",
            "loan_type": "personal_loan",
            "loan_amount": 60000,
            "outstanding_amount": 55000,
            "interest_rate": 11,
            "months_overdue": 0,
            "emi": 2500,
        },
        headers=auth_headers(user_a_token),
    )
    assert create.status_code == 200
    loan_id = create.json()["loan_id"]

    # Fetch it back fresh to prove it was actually persisted, not just echoed
    loans = client.get("/loans", headers=auth_headers(user_a_token)).json()
    matching = [l for l in loans if l["loan_id"] == loan_id]
    assert len(matching) == 1
    assert matching[0]["lender_name"] == "Kotak Bank"
    assert matching[0]["outstanding_amount"] == 55000


def test_user_data_isolated_per_session(user_a_token, user_b_token):
    """User B must never see User A's loans, even though both are
    querying the same /loans endpoint against the same database."""
    client.post(
        "/add-loan",
        json={
            "lender_name": "User B Private Bank",
            "loan_type": "credit_card",
            "loan_amount": 10000,
            "outstanding_amount": 9000,
            "interest_rate": 20,
            "months_overdue": 1,
            "emi": 500,
        },
        headers=auth_headers(user_b_token),
    )

    user_a_loans = client.get("/loans", headers=auth_headers(user_a_token)).json()
    user_b_loans = client.get("/loans", headers=auth_headers(user_b_token)).json()

    a_lenders = {l["lender_name"] for l in user_a_loans}
    b_lenders = {l["lender_name"] for l in user_b_loans}

    assert "User B Private Bank" not in a_lenders
    assert "Kotak Bank" not in b_lenders


def test_financial_profile_isolated_per_user(user_a_token, user_b_token):
    client.put(
        "/update-profile",
        json={"monthly_income": 80000, "monthly_expenses": 20000, "lump_sum_available": 15000},
        headers=auth_headers(user_a_token),
    )
    client.put(
        "/update-profile",
        json={"monthly_income": 30000, "monthly_expenses": 10000, "lump_sum_available": 2000},
        headers=auth_headers(user_b_token),
    )

    a_data = client.get("/dashboard-data", headers=auth_headers(user_a_token)).json()
    b_data = client.get("/dashboard-data", headers=auth_headers(user_b_token)).json()

    assert a_data["monthly_income"] == 80000
    assert b_data["monthly_income"] == 30000
    assert a_data["monthly_income"] != b_data["monthly_income"]


def test_lump_sum_available_round_trips_correctly(user_a_token):
    response = client.put(
        "/update-profile",
        json={"monthly_income": 50000, "monthly_expenses": 10000, "lump_sum_available": 25000},
        headers=auth_headers(user_a_token),
    )
    assert response.status_code == 200
    assert response.json()["lump_sum_available"] == 25000

    # Confirm it was actually persisted, not just echoed back
    dashboard = client.get("/dashboard-data", headers=auth_headers(user_a_token)).json()
    assert dashboard["lump_sum_available"] == 25000


def test_ai_history_isolated_per_user(user_a_token, user_b_token):
    loans_a = client.get("/loans", headers=auth_headers(user_a_token)).json()
    if loans_a:
        client.get(
            f"/ai-negotiation-strategy?loan_id={loans_a[0]['loan_id']}",
            headers=auth_headers(user_a_token),
        )

    history_a = client.get("/ai-history", headers=auth_headers(user_a_token)).json()
    history_b = client.get("/ai-history", headers=auth_headers(user_b_token)).json()

    a_ids = {h["history_id"] for h in history_a}
    b_ids = {h["history_id"] for h in history_b}
    assert a_ids.isdisjoint(b_ids)


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/loans"),
        ("get", "/dashboard-data"),
        ("get", "/financial-health"),
        ("get", "/debt-timeline"),
        ("get", "/ai-history"),
        ("get", "/debug-user"),
    ],
)
def test_all_protected_routes_reject_missing_jwt(method, path):
    response = getattr(client, method)(path)
    assert response.status_code == 401


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/loans"),
        ("get", "/dashboard-data"),
        ("get", "/debug-user"),
    ],
)
def test_all_protected_routes_reject_invalid_jwt(method, path):
    response = getattr(client, method)(path, headers=auth_headers("not-a-real-token"))
    assert response.status_code == 401
