"""
Pydantic schemas matching the required endpoint set:
/register, /login, /update-profile, /add-loan, /loans, /delete-loan/{id},
/dashboard-data, /settlement-predictor, /ai-negotiation-strategy,
/generate-negotiation-email/{loan_id}, /ai-history, /financial-health,
/debt-timeline.
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, Field


# ---------- Auth ----------

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    name: str
    email: EmailStr
    created_at: datetime


# ---------- Loan ----------

class LoanCreate(BaseModel):
    lender_name: str = "Unknown Lender"
    loan_type: str = "other"
    loan_amount: float = Field(ge=0)
    outstanding_amount: float = Field(ge=0)
    interest_rate: float = Field(default=0.0, ge=0)
    due_date: Optional[date] = None
    months_overdue: int = Field(default=0, ge=0)
    emi: float = Field(default=0.0, ge=0)


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    loan_id: int
    user_id: int
    lender_name: str
    loan_type: str
    loan_amount: float
    outstanding_amount: float
    interest_rate: float
    due_date: Optional[date]
    months_overdue: int
    status: str
    emi: float


# ---------- Financial Profile ----------

class UpdateProfileRequest(BaseModel):
    monthly_income: float = Field(ge=0)
    monthly_expenses: float = Field(default=0.0, ge=0)
    lump_sum_available: float = Field(default=0.0, ge=0)


class FinancialProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    profile_id: int
    user_id: int
    monthly_income: float
    monthly_expenses: float
    existing_debts: float
    financial_health_score: float
    lump_sum_available: float
    updated_at: datetime


class DashboardDataOut(FinancialProfileOut):
    health_category: str
    debt_to_income_ratio: float
    disposable_income: float
    loans: List[LoanOut] = []


class FinancialHealthOut(BaseModel):
    financial_health_score: float
    health_category: str
    debt_to_income_ratio: float
    disposable_income: float
    existing_debts: float


class DebtTimelineMonth(BaseModel):
    month: int
    remaining_balance: float


class DebtTimelineOut(BaseModel):
    months_to_debt_free: int
    final_remaining_balance: float
    timeline_preview: List[DebtTimelineMonth]


# ---------- Settlement Records ----------

class SettlementPredictionOut(BaseModel):
    loan_id: int
    lender_name: str
    outstanding_amount: float
    interest_rate: float
    emi: float
    suggested_settlement_percentage: float
    risk_score: int
    risk_category: str


# ---------- AI History ----------

class NegotiationStrategyOut(BaseModel):
    loan_id: Optional[int] = None
    negotiation_strategy: str
    source: str


class NegotiationEmailOut(BaseModel):
    loan_id: Optional[int] = None
    settlement_letter: str
    source: str


class AIHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    history_id: int
    user_id: int
    negotiation_strategy: str
    settlement_letter: str
    ai_response: str
    generated_at: datetime
