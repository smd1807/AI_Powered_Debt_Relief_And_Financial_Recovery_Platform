from types import SimpleNamespace
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from app.services.financial_engine import calculate_financial_health
from app.services.settlement_prediction import calculate_settlement
from app.services.negotiation_engine import generate_negotiation_output

router = APIRouter()


def _resolve_loan(loan_id: Optional[int], current_user: models.User, db: Session) -> models.Loan:
    query = db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id)
    if loan_id is not None:
        query = query.filter(models.Loan.loan_id == loan_id)
    loan = query.order_by(models.Loan.loan_id.desc()).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


def _latest_settlement_or_predict(
    loan: models.Loan, current_user: models.User, db: Session
) -> SimpleNamespace:
    """Returns an object with .settlement_percent, .recommended_amount, .priority_level —
    the shape the negotiation engine expects — sourced from the latest SettlementRecord
    if one exists, otherwise computed fresh via the Settlement Prediction System."""
    latest = (
        db.query(models.SettlementRecord)
        .filter(models.SettlementRecord.loan_id == loan.loan_id)
        .order_by(models.SettlementRecord.settlement_id.desc())
        .first()
    )
    if latest:
        percent = round((latest.recommended_amount / loan.outstanding_amount) * 100, 2)
        return SimpleNamespace(
            settlement_percent=percent,
            recommended_amount=latest.recommended_amount,
            priority_level=latest.priority_level,
        )

    profile = (
        db.query(models.FinancialProfile)
        .filter(models.FinancialProfile.user_id == current_user.user_id)
        .first()
    )
    user_for_calc = profile or SimpleNamespace(monthly_income=0, monthly_expenses=0)
    active_loans = [l for l in current_user.loans if l.status != "settled"]
    health = calculate_financial_health(user_for_calc, active_loans)

    result = calculate_settlement(user_for_calc, [loan], emi_ratio=health["emi_ratio_percent"])[0]
    return SimpleNamespace(
        settlement_percent=result["suggested_settlement_percentage"],
        recommended_amount=round(
            loan.outstanding_amount * result["suggested_settlement_percentage"] / 100, 2
        ),
        priority_level=result["risk_category"],
    )


def _save_history_safely(db: Session, **kwargs) -> models.AIHistory:
    """Saves an AIHistory row; on failure, rolls back so the request can
    still return a usable result instead of a broken transaction."""
    history = models.AIHistory(**kwargs)
    try:
        db.add(history)
        db.commit()
    except Exception:
        db.rollback()
    return history


@router.get("/ai-negotiation-strategy", response_model=schemas.NegotiationStrategyOut)
def ai_negotiation_strategy(
    loan_id: Optional[int] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Friendly guidance instead of an error when the borrower has no loans yet.
        if loan_id is None:
            active_loans = [l for l in current_user.loans if l.status != "settled"]
            if not active_loans:
                return schemas.NegotiationStrategyOut(
                    loan_id=None,
                    negotiation_strategy="Please add at least one loan to generate an AI strategy.",
                    source="fallback",
                )

        loan = _resolve_loan(loan_id, current_user, db)
        settlement = _latest_settlement_or_predict(loan, current_user, db)

        ai_result = generate_negotiation_output(
            borrower_name=current_user.name,
            lender_name=loan.lender_name,
            outstanding_amount=loan.outstanding_amount,
            settlement=settlement,
        )

        _save_history_safely(
            db,
            user_id=current_user.user_id,
            negotiation_strategy=ai_result["negotiation_strategy"],
            settlement_letter=ai_result["settlement_letter"],
            ai_response=ai_result["ai_response"],
        )

        return schemas.NegotiationStrategyOut(
            loan_id=loan.loan_id,
            negotiation_strategy=ai_result["negotiation_strategy"],
            source=ai_result["ai_response"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Strategy error: {str(e)}")


@router.get("/generate-negotiation-email/{loan_id}", response_model=schemas.NegotiationEmailOut)
def generate_negotiation_email(
    loan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        loan = _resolve_loan(loan_id, current_user, db)
        settlement = _latest_settlement_or_predict(loan, current_user, db)

        ai_result = generate_negotiation_output(
            borrower_name=current_user.name,
            lender_name=loan.lender_name,
            outstanding_amount=loan.outstanding_amount,
            settlement=settlement,
        )

        _save_history_safely(
            db,
            user_id=current_user.user_id,
            negotiation_strategy=ai_result["negotiation_strategy"],
            settlement_letter=ai_result["settlement_letter"],
            ai_response=ai_result["ai_response"],
        )

        return schemas.NegotiationEmailOut(
            loan_id=loan.loan_id,
            settlement_letter=ai_result["settlement_letter"],
            source=ai_result["ai_response"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Negotiation email error: {str(e)}")


@router.get("/ai-history", response_model=list[schemas.AIHistoryOut])
def ai_history(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        return (
            db.query(models.AIHistory)
            .filter(models.AIHistory.user_id == current_user.user_id)
            .order_by(models.AIHistory.history_id.desc())
            .all()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI History error: {str(e)}")
