"""
Fallback Logic (Epic 2)

If no LLM provider is configured (or the live call fails/times out),
this guarantees AI_History still gets a sensible, deterministic
negotiation_strategy AND settlement_letter instead of erroring out.
"""


def fallback_negotiation_output(
    borrower_name: str,
    lender_name: str,
    outstanding_amount: float,
    settlement,
) -> dict:
    """
    Returns {negotiation_strategy, settlement_letter, ai_response}.
    ai_response is always "fallback" here.
    """
    offer = round(settlement.recommended_amount * 0.9, 2)  # open a little below prediction

    negotiation_strategy = (
        f"Open the conversation with {lender_name} by acknowledging the debt but explaining "
        f"a genuine financial hardship. Propose a one-time full-and-final settlement of "
        f"approximately ₹{offer:,.0f} (about {round((offer/outstanding_amount)*100, 1)}% of the "
        f"outstanding ₹{outstanding_amount:,.0f}). Ask for the agreement in writing before making "
        f"any payment, and request an updated credit bureau report / no-dues certificate as part "
        f"of the terms. If refused, be prepared to raise the offer in small increments toward "
        f"₹{settlement.recommended_amount:,.0f} ({settlement.settlement_percent}% of outstanding), "
        f"the model's predicted ceiling the lender is likely to accept."
    )

    settlement_letter = (
        f"Subject: Proposal for One-Time Settlement — Account of {borrower_name}\n\n"
        f"Dear {lender_name} Team,\n\n"
        f"I am writing regarding my outstanding balance of ₹{outstanding_amount:,.0f}. Due to "
        f"ongoing financial hardship, I am unable to clear this amount in full at this time. "
        f"I would like to propose a one-time full-and-final settlement of ₹{offer:,.0f} in "
        f"complete closure of this account.\n\n"
        f"I request that, upon receipt of this payment, the account be marked as settled and "
        f"reported accordingly to the credit bureau, with a formal no-dues certificate issued "
        f"to me for my records.\n\n"
        f"I would appreciate the opportunity to discuss this proposal at your earliest "
        f"convenience and look forward to resolving this matter amicably.\n\n"
        f"Sincerely,\n{borrower_name}"
    )

    return {
        "negotiation_strategy": negotiation_strategy,
        "settlement_letter": settlement_letter,
        "ai_response": "fallback",
    }
