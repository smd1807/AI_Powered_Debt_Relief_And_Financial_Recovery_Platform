"""
Unit tests for Fallback Logic Implementation (Epic 2, Story 5) —
proves the system stays stable and fully functional even with no
active Gemini API key, and that the fallback output is well-formed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.fallback import fallback_negotiation_output  # noqa: E402
from app.services.settlement_prediction import calculate_settlement  # noqa: E402
from dataclasses import dataclass


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


def test_fallback_output_has_all_required_fields():
    user = FakeUser(monthly_income=50000)
    loan = FakeLoan(1, "HDFC Bank", 100000, 20, 3, 4000)
    settlement_result = calculate_settlement(user, [loan], emi_ratio=0)[0]

    from types import SimpleNamespace

    settlement = SimpleNamespace(
        settlement_percent=settlement_result["suggested_settlement_percentage"],
        recommended_amount=round(
            loan.outstanding_amount * settlement_result["suggested_settlement_percentage"] / 100, 2
        ),
        priority_level=settlement_result["risk_category"],
    )

    output = fallback_negotiation_output("Test User", "HDFC Bank", 100000, settlement)

    assert "negotiation_strategy" in output
    assert "settlement_letter" in output
    assert "ai_response" in output
    assert output["ai_response"] == "fallback"
    assert len(output["negotiation_strategy"]) > 20
    assert len(output["settlement_letter"]) > 20


def test_fallback_letter_addresses_correct_lender_and_borrower():
    from types import SimpleNamespace

    settlement = SimpleNamespace(settlement_percent=60.0, recommended_amount=60000, priority_level="Medium")
    output = fallback_negotiation_output("Jane Doe", "SBI Bank", 100000, settlement)

    assert "Jane Doe" in output["settlement_letter"]
    assert "SBI Bank" in output["settlement_letter"]


def test_system_stable_across_repeated_fallback_calls():
    """Simulates the AI engine being called many times with no API key —
    the system must never crash and always return usable output."""
    from types import SimpleNamespace

    for i in range(10):
        settlement = SimpleNamespace(
            settlement_percent=50.0 + i, recommended_amount=10000 * (i + 1), priority_level="Low"
        )
        output = fallback_negotiation_output(f"User {i}", f"Bank {i}", 20000 * (i + 1), settlement)
        assert output["ai_response"] == "fallback"
        assert output["negotiation_strategy"]
        assert output["settlement_letter"]


def test_negotiation_engine_never_raises_without_api_key(monkeypatch):
    """End-to-end: generate_negotiation_output must never raise, even
    with GOOGLE_API_KEY completely unset."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    import importlib
    from app.services import negotiation_engine

    importlib.reload(negotiation_engine)

    from types import SimpleNamespace

    settlement = SimpleNamespace(settlement_percent=55.0, recommended_amount=55000, priority_level="Medium")

    try:
        result = negotiation_engine.generate_negotiation_output(
            borrower_name="Stability Test",
            lender_name="Test Bank",
            outstanding_amount=100000,
            settlement=settlement,
        )
    except Exception as e:
        assert False, f"generate_negotiation_output raised unexpectedly: {e}"

    assert result["ai_response"] == "fallback"
