"""
SQLAlchemy ORM models for FinRelief AI — matches docs/ER_DIAGRAM.md
(the official SkillWallet task spec) exactly:
Users, Loans, Financial_Profiles, Settlement_Records, AI_History.
"""
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # stored as a bcrypt hash
    created_at = Column(DateTime, default=datetime.utcnow)

    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    financial_profile = relationship(
        "FinancialProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    settlement_records = relationship(
        "SettlementRecord", back_populates="user", cascade="all, delete-orphan"
    )
    ai_history = relationship("AIHistory", back_populates="user", cascade="all, delete-orphan")


class Loan(Base):
    __tablename__ = "loans"

    loan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    loan_type = Column(String(50), default="other")
    loan_amount = Column(Float, nullable=False)
    outstanding_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0.0)  # annual %
    due_date = Column(Date, nullable=True)

    # Practical extras beyond the spec, used internally by the AI engines.
    lender_name = Column(String(150), default="Unknown Lender")
    months_overdue = Column(Integer, default=0)
    status = Column(String(20), default="active")  # active | settled | defaulted
    emi = Column(Float, default=0.0)  # monthly installment amount

    user = relationship("User", back_populates="loans")
    settlement_records = relationship(
        "SettlementRecord", back_populates="loan", cascade="all, delete-orphan"
    )


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    monthly_income = Column(Float, nullable=False, default=0.0)
    monthly_expenses = Column(Float, nullable=False, default=0.0)
    existing_debts = Column(Float, nullable=False, default=0.0)
    financial_health_score = Column(Float, nullable=False, default=0.0)
    lump_sum_available = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="financial_profile")


class SettlementRecord(Base):
    __tablename__ = "settlement_records"

    settlement_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    loan_id = Column(Integer, ForeignKey("loans.loan_id"), nullable=False, index=True)
    settlement_prediction = Column(String(30), nullable=False)  # e.g. "68% likely"
    recommended_amount = Column(Float, nullable=False)
    priority_level = Column(String(20), default="Medium")  # High | Medium | Low
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="settlement_records")
    loan = relationship("Loan", back_populates="settlement_records")


class AIHistory(Base):
    __tablename__ = "ai_history"

    history_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    negotiation_strategy = Column(Text, nullable=False)
    settlement_letter = Column(Text, nullable=False)
    ai_response = Column(String(20), default="fallback")  # "llm" or "fallback"
    generated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ai_history")
