"""Auto-Kategorisierung: erst Regelwerk, dann LLM als Fallback."""

from __future__ import annotations

import logging
import re
from decimal import Decimal

from sqlalchemy.orm import Session

from .. import models
from ..llm import llm

log = logging.getLogger(__name__)


def _normalize(s: str) -> str:
    """Fuer fuzzy Kategorie-Name-Vergleich: lowercase, nur alnum."""
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _resolve_category(cat_name: str, by_name: dict[str, models.Category]) -> models.Category | None:
    if not cat_name:
        return None
    if cat_name in by_name:
        return by_name[cat_name]
    norm = _normalize(cat_name)
    for name, cat in by_name.items():
        if _normalize(name) == norm:
            return cat
    for name, cat in by_name.items():
        n = _normalize(name)
        if norm and (norm in n or n in norm):
            return cat
    return None

LLM_SYSTEM = (
    "Du bist ein Finanz-Assistent für deutsche Privat-Haushalte. "
    "Aufgabe: ordne eine Bank-Transaktion einer Haushaltsbuch-Kategorie zu. "
    "Antworte ausschließlich mit JSON: "
    '{"category": "<Name aus Liste>", "confidence": 0.0-1.0, "reason": "kurz"}.'
)


def _build_user_prompt(tx: models.Transaction, categories: list[str]) -> str:
    return (
        "Kategorien (wähle exakt eine):\n- "
        + "\n- ".join(categories)
        + f"\n\nTransaktion:\n"
        f"  Betrag: {tx.amount} {tx.currency}\n"
        f"  Empfänger/Auftraggeber: {tx.counterparty or '-'}\n"
        f"  Verwendungszweck: {tx.purpose or '-'}\n"
        f"  Buchungsdatum: {tx.booking_date.isoformat()}\n"
    )


def _match_rule(tx: models.Transaction, rules: list[models.CategorizationRule]) -> models.CategorizationRule | None:
    haystack_parts: list[str] = []
    if tx.counterparty:
        haystack_parts.append(tx.counterparty.lower())
    if tx.purpose:
        haystack_parts.append(tx.purpose.lower())
    haystack = " | ".join(haystack_parts)
    if not haystack:
        return None

    for rule in rules:
        pattern = rule.pattern.lower()
        try:
            if re.search(pattern, haystack):
                return rule
        except re.error:
            if pattern in haystack:
                return rule
    return None


def categorize(db: Session, tx: models.Transaction, use_llm: bool = True) -> None:
    """Setzt category_id, category_source, category_confidence auf der Transaktion."""

    if tx.category_id and tx.category_source == "user":
        return  # User-Entscheidung respektieren

    rules = (
        db.query(models.CategorizationRule)
        .order_by(models.CategorizationRule.hits.desc())
        .all()
    )
    rule = _match_rule(tx, rules)
    if rule:
        tx.category_id = rule.category_id
        tx.category_source = "rule"
        tx.category_confidence = Decimal("0.9")
        rule.hits = (rule.hits or 0) + 1
        return

    if not use_llm:
        return

    categories = db.query(models.Category).filter(models.Category.kind != "transfer").all()
    cat_names = [c.name for c in categories]
    by_name = {c.name: c for c in categories}

    try:
        result = llm.complete_json(LLM_SYSTEM, _build_user_prompt(tx, cat_names))
    except Exception as e:
        log.warning("LLM call failed for tx %r: %s", tx.counterparty or tx.purpose, e)
        return

    if not result:
        log.warning("LLM returned empty/invalid JSON for tx %r", tx.counterparty or tx.purpose)
        return

    cat_name = result.get("category")
    cat = _resolve_category(cat_name, by_name)
    if not cat:
        log.warning(
            "LLM-Kategorie '%s' nicht in Liste fuer tx %r (Verwendung: %r)",
            cat_name, tx.counterparty, tx.purpose,
        )
        return

    confidence = result.get("confidence", 0.6)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.6

    log.info("LLM kategorisiert '%s' -> '%s' (conf=%.2f)", tx.counterparty or tx.purpose, cat.name, confidence)
    tx.category_id = cat.id
    tx.category_source = "ai"
    tx.category_confidence = Decimal(str(round(confidence, 3)))


def learn_from_user_correction(db: Session, tx: models.Transaction) -> None:
    """Wenn User Kategorie setzt: Regel anlegen, falls Counterparty bekannt."""
    if not tx.counterparty or not tx.category_id:
        return
    pattern = re.escape(tx.counterparty.strip().lower())[:120]
    if not pattern:
        return
    existing = (
        db.query(models.CategorizationRule)
        .filter(models.CategorizationRule.pattern == pattern)
        .first()
    )
    if existing:
        existing.category_id = tx.category_id
        existing.source = "user"
        return
    db.add(
        models.CategorizationRule(
            pattern=pattern,
            match_field="counterparty",
            category_id=tx.category_id,
            source="user",
        )
    )
