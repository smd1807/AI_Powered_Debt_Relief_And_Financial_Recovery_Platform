from types import SimpleNamespace
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from app.services.financial_engine import calculate_financial_health
from app.services.settlement_prediction import calculate_settlement

router = APIRouter()


@router.get("/settlement-predictor", response_model=list[schemas.SettlementPredictionOut])
def settlement_predictor(
    loan_id: Optional[int] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Predicts settlement for one loan (if loan_id given) or every active
    loan belonging to the current user (if omitted). Uses the Financial
    Engine's emi_ratio as an input to the Settlement Prediction System,
    and stores a SettlementRecord per loan for history.
    """
    query = db.query(models.Loan).filter(models.Loan.user_id == current_user.user_id)
    active_query = query.filter(models.Loan.status != "settled")
    all_active_loans = active_query.all()

    if loan_id is not None:
        target_loans = [l for l in all_active_loans if l.loan_id == loan_id]
        if not target_loans:
            raise HTTPException(status_code=404, detail="Loan not found")
    else:
        target_loans = all_active_loans

    profile = (
        db.query(models.FinancialProfile)
        .filter(models.FinancialProfile.user_id == current_user.user_id)
        .first()
    )
    user_for_calc = profile or SimpleNamespace(monthly_income=0, monthly_expenses=0)

    health = calculate_financial_health(user_for_calc, all_active_loans)
    emi_ratio = health["emi_ratio_percent"]

    results = calculate_settlement(user_for_calc, target_loans, emi_ratio=emi_ratio)

    for r in results:
        record = models.SettlementRecord(
            user_id=current_user.user_id,
            loan_id=r["loan_id"],
            settlement_prediction=f"{r['suggested_settlement_percentage']}% suggested",
            recommended_amount=round(
                r["outstanding_amount"] * r["suggested_settlement_percentage"] / 100, 2
            ),
            priority_level=r["risk_category"],
        )
        db.add(record)
    db.commit()

    return [schemas.SettlementPredictionOut(**r) for r in results]
