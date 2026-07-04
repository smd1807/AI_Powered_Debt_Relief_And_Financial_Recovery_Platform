"""
Settlement Prediction System (Epic 2, Story 3)

Matches the official task spec exactly: calculate_settlement(user, loans,
emi_ratio=0) — a rule-based model computing optimal settlement percentages
and risk categories per loan.

`user` needs .monthly_income. `loans` need .loan_id, .lender_name,
.outstanding_amount, .interest_rate, .months_overdue, .emi
(our SQLAlchemy Loan rows have exactly these attributes).

No DB/FastAPI imports here on purpose — kept testable in isolation.
"""


def calculate_settlement(user, loans, emi_ratio=0):
    """Calculates optimal settlement percentages and risk categories per loan."""
    total_outstanding = sum(loan.outstanding_amount for loan in loans)

    # Calculate Debt-to-Income ratio
    if user.monthly_income > 0:
        debt_to_income = (total_outstanding / user.monthly_income) * 100
    else:
        debt_to_income = 0

    settlement_results = []

    for loan in loans:
        # Base settlement = 50%
        settlement = 50.0
        risk_score = 0

        # +5% if overdue
        if loan.months_overdue > 0:
            settlement += 5
            risk_score += 20

        # +5% if EMI ratio > 50
        if emi_ratio > 50:
            settlement += 5
            risk_score += 15

        # +5% if interest_rate > 12%
        if loan.interest_rate > 12:
            settlement += 5
            risk_score += 10

        # +5% if debt_to_income > 80%
        if debt_to_income > 80:
            settlement += 5
            risk_score += 15

        # Clamp settlement: Minimum 40%, Maximum 75%
        settlement = max(40, min(75, settlement))

        # Determine risk category
        if risk_score >= 40:
            risk_category = "High"
        elif risk_score >= 20:
            risk_category = "Medium"
        else:
            risk_category = "Low"

        settlement_results.append(
            {
                "loan_id": loan.loan_id,
                "lender_name": loan.lender_name,
                "outstanding_amount": loan.outstanding_amount,
                "interest_rate": loan.interest_rate,
                "emi": loan.emi,
                "suggested_settlement_percentage": settlement,
                "risk_score": risk_score,
                "risk_category": risk_category,
            }
        )

    return settlement_results
