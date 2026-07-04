"""
Unit tests for the Settlement Prediction System (Epic 2, Story 3) —
tests calculate_settlement directly, in isolation from the API/DB.
"""
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.settlement_prediction import calculate_settlement  # noqa: E402


@dataclass
class FakeUser:
    monthly_income: float


@dataclass
class FakeLoan:
    loan_id: int
    lender_name: str
    outstanding_amount: float
    interest_rate: float
    months_overdue: int
    emi: float


def test_base_settlement_is_50_when_no_risk_factors():
    # Not overdue, low interest, emi_ratio low, low debt-to-income -> stays at base 50
    user = FakeUser(monthly_income=100000)
    loans = [FakeLoan(1, "HDFC", 10000, 5, 0, 500)]
    result = calculate_settlement(user, loans, emi_ratio=0)

    assert result[0]["suggested_settlement_percentage"] == 50.0
    assert result[0]["risk_score"] == 0
    assert result[0]["risk_category"] == "Low"


def test_overdue_adds_5_percent_and_20_risk():
    user = FakeUser(monthly_income=100000)
    loans = [FakeLoan(1, "HDFC", 10000, 5, 3, 500)]  # overdue
    result = calculate_settlement(user, loans, emi_ratio=0)

    assert result[0]["suggested_settlement_percentage"] == 55.0
    assert result[0]["risk_score"] == 20
    assert result[0]["risk_category"] == "Medium"  # 20 >= 20


def test_high_interest_adds_5_percent_and_10_risk():
    user = FakeUser(monthly_income=100000)
    loans = [FakeLoan(1, "HDFC", 10000, 15, 0, 500)]  # interest_rate > 12
    result = calculate_settlement(user, loans, emi_ratio=0)

    assert result[0]["suggested_settlement_percentage"] == 55.0
    assert result[0]["risk_score"] == 10
    assert result[0]["risk_category"] == "Low"  # 10 < 20


def test_high_emi_ratio_adds_5_percent_and_15_risk():
    user = FakeUser(monthly_income=100000)
    loans = [FakeLoan(1, "HDFC", 10000, 5, 0, 500)]
    result = calculate_settlement(user, loans, emi_ratio=60)  # > 50

    assert result[0]["suggested_settlement_percentage"] == 55.0
    assert result[0]["risk_score"] == 15


def test_high_debt_to_income_adds_5_percent_and_15_risk():
    # outstanding 90000, income 100000 -> DTI = 90% > 80%
    user = FakeUser(monthly_income=100000)
    loans = [FakeLoan(1, "HDFC", 90000, 5, 0, 500)]
    result = calculate_settlement(user, loans, emi_ratio=0)

    assert result[0]["suggested_settlement_percentage"] == 55.0
    assert result[0]["risk_score"] == 15


def test_all_risk_factors_combined_clamped_at_75():
    # Overdue (+5/+20), high interest (+5/+10), high emi_ratio (+5/+15),
    # high DTI (+5/+15) -> 50+20=70% raw, risk_score=60 -> High
    user = FakeUser(monthly_income=10000)
    loans = [FakeLoan(1, "HDFC", 9000, 20, 6, 3000)]
    result = calculate_settlement(user, loans, emi_ratio=90)

    assert result[0]["suggested_settlement_percentage"] == 70.0
    assert result[0]["risk_score"] == 60
    assert result[0]["risk_category"] == "High"


def test_settlement_never_below_40_or_above_75():
    user = FakeUser(monthly_income=100000)
    loans = [FakeLoan(1, "HDFC", 1000, 1, 0, 100)]  # zero risk factors -> still 50, above 40 floor
    result = calculate_settlement(user, loans, emi_ratio=0)
    assert result[0]["suggested_settlement_percentage"] >= 40
    assert result[0]["suggested_settlement_percentage"] <= 75


def test_zero_income_gives_zero_debt_to_income():
    user = FakeUser(monthly_income=0)
    loans = [FakeLoan(1, "HDFC", 50000, 5, 0, 1000)]
    result = calculate_settlement(user, loans, emi_ratio=0)
    # No DTI risk factor triggered since debt_to_income defaults to 0
    assert result[0]["suggested_settlement_percentage"] == 50.0


def test_multiple_loans_each_scored_independently():
    user = FakeUser(monthly_income=100000)
    loans = [
        FakeLoan(1, "Bank A", 10000, 5, 0, 500),  # low risk
        FakeLoan(2, "Bank B", 10000, 20, 5, 800),  # overdue + high interest -> risk_score 30
    ]
    result = calculate_settlement(user, loans, emi_ratio=0)

    assert result[0]["risk_category"] == "Low"
    assert result[1]["risk_category"] == "Medium"  # 20 (overdue) + 10 (high interest) = 30
    assert result[1]["suggested_settlement_percentage"] > result[0]["suggested_settlement_percentage"]
