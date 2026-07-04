from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter()


@router.post("/add-loan", response_model=schemas.LoanOut)
def add_loan(
    payload: schemas.LoanCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loan = models.Loan(user_id=current_user.user_id, **payload.model_dump())
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@router.get("/loans", response_model=list[schemas.LoanOut])
def get_loans(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return (
        db.query(models.Loan)
        .filter(models.Loan.user_id == current_user.user_id)
        .order_by(models.Loan.loan_id.desc())
        .all()
    )


@router.delete("/delete-loan/{loan_id}")
def delete_loan(
    loan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loan = (
        db.query(models.Loan)
        .filter(models.Loan.loan_id == loan_id, models.Loan.user_id == current_user.user_id)
        .first()
    )
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    db.delete(loan)
    db.commit()
    return {"detail": "Loan deleted"}
