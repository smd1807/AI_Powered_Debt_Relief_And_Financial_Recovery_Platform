"""
AI Negotiation Strategy Engine (Epic 2, Story 4)
Fallback Logic Implementation (Epic 2, Story 5)

_call_gemini() matches the official task spec exactly (from both the
Story 4 and Story 5 descriptions): uses importlib to load the
google-generativeai SDK, reads GOOGLE_API_KEY, model "gemini-1.5-flash",
and returns None (falling through to the rule-based fallback) whenever
the key is missing, the SDK import fails, or any error occurs.
"""
import os
import json
import importlib
from dotenv import load_dotenv

from app.services.fallback import fallback_negotiation_output

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")


def _call_gemini(prompt: str) -> str:
    """Call Google Gemini API if key is available, otherwise use rule-based fallback."""
    if not GOOGLE_API_KEY:
        return None  # Will fall through to fallback

    try:
        genai = importlib.import_module("google.generativeai")
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Explicit timeout (Epic 5: API timeout and unexpected response handling)
        # so a slow/hanging Gemini call can never block a request indefinitely —
        # it fails fast and falls through to the rule-based fallback instead.
        response = model.generate_content(prompt, request_options={"timeout": 15})
        return response.text
    except ImportError:
        return None
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None


def _build_prompt(borrower_name, lender_name, outstanding_amount, settlement, user_notes):
    return (
        f"You are a debt settlement negotiation advisor. Borrower '{borrower_name}' owes "
        f"₹{outstanding_amount:,.0f} to {lender_name}. A settlement model predicts "
        f"{settlement.settlement_percent}% (₹{settlement.recommended_amount:,.0f}) as a likely "
        f"full-and-final settlement, priority: {settlement.priority_level}. "
        f"Additional context: {user_notes or 'none provided'}. "
        f"Respond with ONLY a raw JSON object (no markdown fences) with exactly two keys: "
        f"'negotiation_strategy' (a short 4-6 sentence practical negotiation approach) and "
        f"'settlement_letter' (a formal settlement proposal letter addressed to the lender, "
        f"signed by the borrower)."
    )


def _parse_gemini_json(text: str) -> dict:
    text = text.strip()
    # Gemini sometimes wraps JSON in ```json ... ``` fences despite instructions — strip them.
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


def generate_negotiation_output(
    borrower_name: str,
    lender_name: str,
    outstanding_amount: float,
    settlement,
    user_notes: str = None,
) -> dict:
    """
    Returns {negotiation_strategy, settlement_letter, ai_response}.
    ai_response is "llm" on a successful live Gemini call, "fallback" otherwise.
    """
    prompt = _build_prompt(borrower_name, lender_name, outstanding_amount, settlement, user_notes)
    raw_text = _call_gemini(prompt)

    if raw_text is not None:
        try:
            result = _parse_gemini_json(raw_text)
            return {
                "negotiation_strategy": result["negotiation_strategy"],
                "settlement_letter": result["settlement_letter"],
                "ai_response": "llm",
            }
        except Exception as e:
            # Parsing failure -> silently degrade to fallback
            # (Epic 5: Backend Error Handling & AI Fallback Management).
            print(f"Gemini response parsing error: {e}")

    return fallback_negotiation_output(borrower_name, lender_name, outstanding_amount, settlement)
