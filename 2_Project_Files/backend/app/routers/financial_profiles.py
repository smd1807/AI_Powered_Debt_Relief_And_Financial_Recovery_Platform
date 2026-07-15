from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.financial_engine import calculate_financial_health, simulate_debt_timeline
from app.auth import get_current_user

router = APIRouter()


def _active_loans(user: models.User):
    return [l for l in user.loans if l.status != "settled"]


@router.put("/update-profile", response_model=schemas.DashboardDataOut)
def update_profile(
    payload: schemas.UpdateProfileRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Recalculates and upserts the current user's Financial_Profile
    (1:1 relationship — one row per user, updated in place) using the
    Financial Engine Module's calculate_financial_health().
    """
    active_loans = _active_loans(current_user)
    health = calculate_financial_health(payload, active_loans)

    profile = (
        db.query(models.FinancialProfile)
        .filter(models.FinancialProfile.user_id == current_user.user_id)
        .first()
    )
    # financial_health_score stored as an inverse of EMI burden (0-100, higher = healthier)
    score = round(max(0.0, 100 - health["emi_ratio_percent"]), 2)

    if profile:
        profile.monthly_income = payload.monthly_income
        profile.monthly_expenses = payload.monthly_expenses
        profile.existing_debts = health["total_outstanding"]
        profile.financial_health_score = score
        profile.lump_sum_available = payload.lump_sum_available
    else:
        profile = models.FinancialProfile(
            user_id=current_user.user_id,
            monthly_income=payload.monthly_income,
            monthly_expenses=payload.monthly_expenses,
            existing_debts=health["total_outstanding"],
            financial_health_score=score,
            lump_sum_available=payload.lump_sum_available,
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)

    return schemas.DashboardDataOut(
        profile_id=profile.profile_id,
        user_id=current_user.user_id,
        monthly_income=profile.monthly_income,
        monthly_expenses=profile.monthly_expenses,
        existing_debts=profile.existing_debts,
        financial_health_score=profile.financial_health_score,
        lump_sum_available=profile.lump_sum_available,
        updated_at=profile.updated_at,
        health_category=health["stress_level"],
        debt_to_income_ratio=health["debt_to_income_percent"],
        disposable_income=health["surplus"],
        loans=active_loans,
    )


@router.get("/dashboard-data", response_model=schemas.DashboardDataOut)
def dashboard_data(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    active_loans = _active_loans(current_user)
    profile = (
        db.query(models.FinancialProfile)
        .filter(models.FinancialProfile.user_id == current_user.user_id)
        .first()
    )

    if not profile:
        return schemas.DashboardDataOut(
            profile_id=0,
            user_id=current_user.user_id,
            monthly_income=0,
            monthly_expenses=0,
            existing_debts=sum(l.outstanding_amount for l in active_loans),
            financial_health_score=0,
            lump_sum_available=0,
            updated_at=None,
            health_category="Unknown",
            debt_to_income_ratio=0,
            disposable_income=0,
            loans=active_loans,
        )

    health = calculate_financial_health(profile, active_loans)
    live_score = round(max(0.0, 100 - health["emi_ratio_percent"]), 2)

    return schemas.DashboardDataOut(
        profile_id=profile.profile_id,
        user_id=current_user.user_id,
        monthly_income=profile.monthly_income,
        monthly_expenses=profile.monthly_expenses,
        existing_debts=health["total_outstanding"],
        financial_health_score=live_score,
        lump_sum_available=profile.lump_sum_available,
        updated_at=profile.updated_at,
        health_category=health["stress_level"],
        debt_to_income_ratio=health["debt_to_income_percent"],
        disposable_income=health["surplus"],
        loans=active_loans,
    )


@router.get("/financial-health", response_model=schemas.FinancialHealthOut)
def financial_health(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    active_loans = _active_loans(current_user)
    profile = (
        db.query(models.FinancialProfile)
        .filter(models.FinancialProfile.user_id == current_user.user_id)
        .first()
    )
    if not profile:
        return schemas.FinancialHealthOut(
            financial_health_score=0,
            health_category="Unknown",
            debt_to_income_ratio=0,
            disposable_income=0,
            existing_debts=sum(l.outstanding_amount for l in active_loans),
        )

    health = calculate_financial_health(profile, active_loans)

    return schemas.FinancialHealthOut(
        financial_health_score=round(max(0.0, 100 - health["emi_ratio_percent"]), 2),
        health_category=health["stress_level"],
        debt_to_income_ratio=health["debt_to_income_percent"],
        disposable_income=health["surplus"],
        existing_debts=health["total_outstanding"],
    )


@router.get("/debt-timeline", response_model=schemas.DebtTimelineOut)
def debt_timeline(
    extra_payment: float = 0,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    active_loans = _active_loans(current_user)
    profile = (
        db.query(models.FinancialProfile)
        .filter(models.FinancialProfile.user_id == current_user.user_id)
        .first()
    )
    result = simulate_debt_timeline(profile, active_loans, extra_payment=extra_payment)
    return schemas.DebtTimelineOut(**result)
