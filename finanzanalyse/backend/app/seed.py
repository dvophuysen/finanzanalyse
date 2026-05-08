"""Seed-Kategorien für ein deutsches Familien-Haushaltsbuch."""

from sqlalchemy.orm import Session

from . import models

SEED_CATEGORIES: list[tuple[str, str, bool, str]] = [
    # name, kind, is_essential, color
    ("Einkommen / Gehalt", "income", True, "#10b981"),
    ("Sonstige Einnahmen", "income", False, "#34d399"),
    ("Wohnen / Miete", "expense", True, "#0ea5e9"),
    ("Nebenkosten / Strom / Gas", "expense", True, "#0284c7"),
    ("Internet / Telefon / Mobilfunk", "expense", True, "#0369a1"),
    ("Versicherungen", "expense", True, "#6366f1"),
    ("Gesundheit / Apotheke", "expense", True, "#ec4899"),
    ("Lebensmittel / Supermarkt", "expense", True, "#f59e0b"),
    ("Drogerie / Haushalt", "expense", True, "#fbbf24"),
    ("Restaurants / Essen gehen", "expense", False, "#ef4444"),
    ("Lieferdienste / Bestellen", "expense", False, "#dc2626"),
    ("Mobilität / Auto / Tank", "expense", True, "#84cc16"),
    ("ÖPNV / Bahn", "expense", True, "#65a30d"),
    ("Kinder / Schule / Kita", "expense", True, "#a855f7"),
    ("Freizeit / Hobbys", "expense", False, "#f472b6"),
    ("Urlaub / Reisen", "expense", False, "#14b8a6"),
    ("Shopping / Kleidung", "expense", False, "#fb7185"),
    ("Streaming / Abos", "expense", False, "#8b5cf6"),
    ("Bargeld / ATM", "expense", False, "#94a3b8"),
    ("Sparen / Investieren", "expense", False, "#22c55e"),
    ("Umbuchung / Transfer", "transfer", False, "#64748b"),
    ("Sonstiges / Unkategorisiert", "expense", False, "#9ca3af"),
]


SEED_RULES: list[tuple[str, str]] = [
    # pattern (case-insensitive substring), category name
    ("rewe", "Lebensmittel / Supermarkt"),
    ("edeka", "Lebensmittel / Supermarkt"),
    ("aldi", "Lebensmittel / Supermarkt"),
    ("lidl", "Lebensmittel / Supermarkt"),
    ("kaufland", "Lebensmittel / Supermarkt"),
    ("penny", "Lebensmittel / Supermarkt"),
    ("netto", "Lebensmittel / Supermarkt"),
    ("dm-drogerie", "Drogerie / Haushalt"),
    ("rossmann", "Drogerie / Haushalt"),
    ("amazon", "Shopping / Kleidung"),
    ("zalando", "Shopping / Kleidung"),
    ("ikea", "Shopping / Kleidung"),
    ("netflix", "Streaming / Abos"),
    ("spotify", "Streaming / Abos"),
    ("disney", "Streaming / Abos"),
    ("apple.com/bill", "Streaming / Abos"),
    ("google", "Streaming / Abos"),
    ("shell", "Mobilität / Auto / Tank"),
    ("aral", "Mobilität / Auto / Tank"),
    ("esso", "Mobilität / Auto / Tank"),
    ("total", "Mobilität / Auto / Tank"),
    ("db vertrieb", "ÖPNV / Bahn"),
    ("deutsche bahn", "ÖPNV / Bahn"),
    ("bvg", "ÖPNV / Bahn"),
    ("hvv", "ÖPNV / Bahn"),
    ("vodafone", "Internet / Telefon / Mobilfunk"),
    ("telekom", "Internet / Telefon / Mobilfunk"),
    ("o2", "Internet / Telefon / Mobilfunk"),
    ("1&1", "Internet / Telefon / Mobilfunk"),
    ("stadtwerke", "Nebenkosten / Strom / Gas"),
    ("e.on", "Nebenkosten / Strom / Gas"),
    ("vattenfall", "Nebenkosten / Strom / Gas"),
    ("enbw", "Nebenkosten / Strom / Gas"),
    ("allianz", "Versicherungen"),
    ("huk", "Versicherungen"),
    ("axa", "Versicherungen"),
    ("debeka", "Versicherungen"),
    ("apotheke", "Gesundheit / Apotheke"),
    ("lieferando", "Lieferdienste / Bestellen"),
    ("uber eats", "Lieferdienste / Bestellen"),
    ("flink", "Lieferdienste / Bestellen"),
    ("gorillas", "Lieferdienste / Bestellen"),
    ("mcdonald", "Restaurants / Essen gehen"),
    ("burger king", "Restaurants / Essen gehen"),
    ("starbucks", "Restaurants / Essen gehen"),
]


def seed(db: Session) -> None:
    by_name: dict[str, models.Category] = {
        c.name: c for c in db.query(models.Category).all()
    }

    for name, kind, essential, color in SEED_CATEGORIES:
        if name in by_name:
            continue
        cat = models.Category(name=name, kind=kind, is_essential=essential, color=color)
        db.add(cat)
        db.flush()
        by_name[name] = cat

    existing_patterns = {
        r.pattern for r in db.query(models.CategorizationRule).all()
    }
    for pattern, cat_name in SEED_RULES:
        if pattern in existing_patterns:
            continue
        cat = by_name.get(cat_name)
        if not cat:
            continue
        db.add(
            models.CategorizationRule(
                pattern=pattern,
                match_field="counterparty",
                category_id=cat.id,
                source="seed",
            )
        )

    db.commit()
