from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountIn(BaseModel):
    name: str
    iban: str | None = None
    bank_name: str | None = None
    account_type: str = "checking"
    currency: str = "EUR"


class AccountOut(AccountIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    balance: Decimal
    created_at: datetime


class CategoryIn(BaseModel):
    name: str
    parent_id: int | None = None
    kind: str = "expense"
    color: str | None = None
    icon: str | None = None
    is_essential: bool = False


class CategoryOut(CategoryIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    booking_date: date
    value_date: date | None
    amount: Decimal
    currency: str
    counterparty: str | None
    purpose: str | None
    category_id: int | None
    category_source: str | None
    category_confidence: Decimal | None
    category_reason: str | None = None
    needs_review: bool = True
    is_recurring: bool
    is_transfer: bool
    notes: str | None


class TransactionUpdate(BaseModel):
    category_id: int | None = None
    notes: str | None = None
    is_transfer: bool | None = None
    needs_review: bool | None = None


class BulkConfirmIn(BaseModel):
    ids: list[int]


class ImportResult(BaseModel):
    imported: int
    skipped: int
    duplicates: int
    account_id: int


class CashflowPoint(BaseModel):
    period: str
    income: Decimal
    expense: Decimal
    net: Decimal


class CategoryBreakdownItem(BaseModel):
    category_id: int | None
    category_name: str
    amount: Decimal
    transactions: int


class GoalIn(BaseModel):
    name: str
    target_amount: Decimal
    saved_amount: Decimal = Decimal("0")
    target_date: date | None = None
    priority: int = 3
    note: str | None = None


class GoalOut(GoalIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
