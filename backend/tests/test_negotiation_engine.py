"""
Unit tests for the AI Negotiation Strategy Engine (Epic 2, Story 4) —
tests _call_gemini() directly, matching the exact spec: returns None
when no API key is set, when the SDK import fails, or when any error
occurs — always falling through to the rule-based fallback.
"""
import os
import sys
import importlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _reload_engine_with_key(monkeypatch, key: str):
    monkeypatch.setenv("GOOGLE_API_KEY", key)
    from app.services import negotiation_engine
    importlib.reload(negotiation_engine)
    return negotiation_engine


def test_call_gemini_returns_none_when_no_api_key(monkeypatch):
    engine = _reload_engine_with_key(monkeypatch, "")
    assert engine._call_gemini("test prompt") is None


def test_call_gemini_returns_none_on_sdk_exception(monkeypatch):
    engine = _reload_engine_with_key(monkeypatch, "fake-key-123")

    class BoomModel:
        def generate_content(self, prompt):
            raise RuntimeError("simulated API failure")

    class FakeGenAI:
        def configure(self, api_key):
            pass

        def GenerativeModel(self, name):
            return BoomModel()

    monkeypatch.setitem(sys.modules, "google.generativeai", FakeGenAI())
    result = engine._call_gemini("test prompt")
    assert result is None


def test_call_gemini_returns_text_on_success(monkeypatch):
    engine = _reload_engine_with_key(monkeypatch, "fake-key-123")

    class FakeResponse:
        text = '{"negotiation_strategy": "Be firm.", "settlement_letter": "Dear Sir..."}'

    class FakeModel:
        def generate_content(self, prompt, request_options=None):
            return FakeResponse()

    class FakeGenAI:
        def configure(self, api_key):
            pass

        def GenerativeModel(self, name):
            assert name == "gemini-1.5-flash"
            return FakeModel()

    monkeypatch.setitem(sys.modules, "google.generativeai", FakeGenAI())
    result = engine._call_gemini("test prompt")
    assert result is not None
    assert "negotiation_strategy" in result


def test_generate_negotiation_output_falls_back_without_key(monkeypatch):
    engine = _reload_engine_with_key(monkeypatch, "")

    from dataclasses import dataclass

    @dataclass
    class FakeSettlement:
        settlement_percent: float
        recommended_amount: float
        priority_level: str

    settlement = FakeSettlement(settlement_percent=55.0, recommended_amount=50000, priority_level="Medium")
    result = engine.generate_negotiation_output(
        borrower_name="Test User",
        lender_name="Test Bank",
        outstanding_amount=90000,
        settlement=settlement,
    )
    assert result["ai_response"] == "fallback"
    assert len(result["negotiation_strategy"]) > 0
    assert len(result["settlement_letter"]) > 0
