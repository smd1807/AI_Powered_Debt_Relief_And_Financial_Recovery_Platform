"""
Unit tests for the Financial Engine Module (Epic 2, Story 2) —
tests calculate_financial_health, calculate_loan_priority, and
simulate_debt_timeline directly, in isolation from the API/DB.
"""
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.financial_engine import (  # noqa: E402
    calculate_financial_health,
    calculate_loan_priority,
    simulate_debt_timeline,
)


@dataclass
class FakeUser:
    monthly_income: float
    monthly_expenses: float


@dataclass
class FakeLoan:
    loan_id: int
    lender_name: str
    outstanding_amount: float
    interest_rate: float
    months_overdue: int
    emi: float


def test_calculate_financial_health_basic():
    user = FakeUser(monthly_income=50000, monthly_expenses=15000)
    loans = [
        FakeLoan(1, "HDFC", 180000, 36, 8, 8000),
        FakeLoan(2, "SBI", 50000, 10, 0, 2000),
    ]
    result = calculate_financial_health(user, loans)

    assert result["total_emi"] == 10000
    assert result["total_outstanding"] == 230000
    assert result["surplus"] == 25000  # 50000 - 15000 - 10000
    assert result["emi_ratio_percent"] == 20.0  # 10000/50000*100
    assert result["stress_level"] == "Low"  # emi_ratio < 30
    assert result["total_loans"] == 2


def test_calculate_financial_health_high_stress():
    user = FakeUser(monthly_income=20000, monthly_expenses=5000)
    loans = [FakeLoan(1, "HDFC", 300000, 36, 12, 12000)]
    result = calculate_financial_health(user, loans)

    assert result["emi_ratio_percent"] == 60.0  # 12000/20000*100
    assert result["stress_level"] == "High"  # > 50


def test_calculate_financial_health_zero_income():
    user = FakeUser(monthly_income=0, monthly_expenses=5000)
    loans = [FakeLoan(1, "HDFC", 100000, 10, 0, 1000)]
    result = calculate_financial_health(user, loans)

    assert result["emi_ratio_percent"] == 0
    assert result["debt_to_income_percent"] == 0
    assert result["stress_level"] == "Low"


def test_calculate_loan_priority_overdue_is_high():
    loans = [FakeLoan(1, "HDFC", 100000, 10, 3, 5000)]  # overdue -> High
    result = calculate_loan_priority(loans)
    assert result[0]["priority"] == "High"


def test_calculate_loan_priority_high_interest_is_high():
    loans = [FakeLoan(1, "HDFC", 100000, 15, 0, 5000)]  # interest > 12 -> High
    result = calculate_loan_priority(loans)
    assert result[0]["priority"] == "High"


def test_calculate_loan_priority_medium():
    loans = [FakeLoan(1, "HDFC", 100000, 9, 0, 5000)]  # interest > 8, not overdue -> Medium
    result = calculate_loan_priority(loans)
    assert result[0]["priority"] == "Medium"


def test_calculate_loan_priority_low():
    loans = [FakeLoan(1, "HDFC", 100000, 5, 0, 5000)]  # nothing triggered -> Low
    result = calculate_loan_priority(loans)
    assert result[0]["priority"] == "Low"


def test_calculate_loan_priority_sorted_high_first():
    loans = [
        FakeLoan(1, "Low Priority Bank", 50000, 5, 0, 2000),
        FakeLoan(2, "High Priority Bank", 100000, 20, 3, 8000),
        FakeLoan(3, "Medium Priority Bank", 70000, 9, 0, 3000),
    ]
    result = calculate_loan_priority(loans)
    priorities = [r["priority"] for r in result]
    assert priorities == ["High", "Medium", "Low"]


def test_simulate_debt_timeline_pays_off_loan():
    user = FakeUser(monthly_income=50000, monthly_expenses=15000)
    loans = [FakeLoan(1, "HDFC", 10000, 12, 0, 5000)]  # small balance, big EMI
    result = simulate_debt_timeline(user, loans)

    assert result["months_to_debt_free"] > 0
    assert result["final_remaining_balance"] == 0
    assert len(result["timeline_preview"]) <= 12


def test_simulate_debt_timeline_extra_payment_speeds_up_payoff():
    user = FakeUser(monthly_income=50000, monthly_expenses=15000)
    loans_a = [FakeLoan(1, "HDFC", 100000, 12, 0, 3000)]
    loans_b = [FakeLoan(1, "HDFC", 100000, 12, 0, 3000)]

    without_extra = simulate_debt_timeline(user, loans_a, extra_payment=0)
    with_extra = simulate_debt_timeline(user, loans_b, extra_payment=2000)

    assert with_extra["months_to_debt_free"] <= without_extra["months_to_debt_free"]
