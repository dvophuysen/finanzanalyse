"""Analytics-Helfer: Cashflow, Kategorien-Breakdown."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


def monthly_cashflow(db: Session, months: int = 12) -> list[dict]:
    rows = db.execute(select(models.Transaction)).scalars().all()
    by_month: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: {"income": Decimal("0"), "expense": Decimal("0")}
    )
    for tx in rows:
        if tx.is_transfer:
            continue
        key = tx.booking_date.strftime("%Y-%m")
        if tx.amount >= 0:
            by_month[key]["income"] += tx.amount
        else:
            by_month[key]["expense"] += -tx.amount

    sorted_keys = sorted(by_month.keys())[-months:]
    return [
        {
            "period": k,
            "income": by_month[k]["income"],
            "expense": by_month[k]["expense"],
            "net": by_month[k]["income"] - by_month[k]["expense"],
        }
        for k in sorted_keys
    ]


def category_breakdown(
    db: Session, start: date | None = None, end: date | None = None
) -> list[dict]:
    q = db.query(models.Transaction)
    if start:
        q = q.filter(models.Transaction.booking_date >= start)
    if end:
        q = q.filter(models.Transaction.booking_date <= end)
    txs = q.all()

    cats = {c.id: c.name for c in db.query(models.Category).all()}

    bucket: dict[int | None, dict] = defaultdict(
        lambda: {"amount": Decimal("0"), "transactions": 0}
    )
    for tx in txs:
        if tx.is_transfer or tx.amount >= 0:
            continue  # nur Ausgaben
        bucket[tx.category_id]["amount"] += -tx.amount
        bucket[tx.category_id]["transactions"] += 1

    out = []
    for cat_id, data in sorted(bucket.items(), key=lambda kv: kv[1]["amount"], reverse=True):
        out.append(
            {
                "category_id": cat_id,
                "category_name": cats.get(cat_id, "Unkategorisiert") if cat_id else "Unkategorisiert",
                "amount": data["amount"],
                "transactions": data["transactions"],
            }
        )
    return out
