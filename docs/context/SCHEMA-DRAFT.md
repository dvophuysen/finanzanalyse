# Schema-Draft 0.4.0

Vorgeschlagene Erweiterung des Datenmodells. Status: **Draft**.
Bevor irgendeine Migration geschrieben wird, muss dieser Stand vom
Anwender bestätigt werden.

## Status Quo (0.3.0)

Aktuelle Tabellen in `backend/app/models.py`:

- `Account`, `Category` (selbst-referenziell für Hierarchie),
  `CategorizationRule`, `Transaction`, `Budget`, `Goal`
- Eine Buchung hat genau eine Kategorie (`category_id` nullable)
- Wiederkehrend nur als Boolean `is_recurring` ohne weitere Struktur
- Konfidenz und Quelle sind bereits an der Buchung, aber kein
  Empfänger-übergreifendes Profil

## Lücken, die 0.4.0 schließt

1. **Splits** – eine Buchung kann mehrere Kategorie-Anteile haben
   (klassisch: Rewe-Einkauf zu 70 % Lebensmittel, 30 % Drogerie).
2. **Tags** – orthogonal zur Kategorie, in Familien organisiert
   (z. B. Familie „Anlass" mit Werten Geburtstag, Weihnachten, Urlaub).
3. **Verträge** – Mietvertrag, Versicherung, Abo als eigene Entität
   mit Lifecycle (Start, Ende, Kündigungsfrist, Betrag, Frequenz),
   nicht nur ein Boolean an der Buchung.
4. **Empfänger-Profile** – pro Counterparty-Anker eine Wahrscheinlichkeits-
   Verteilung über mögliche Kategorien, daraus leitet sich die
   LLM-Konfidenz ab.

## Vorgeschlagene neue Tabellen

```text
TagFamily
  id, name (unique), description, is_multi_select (bool)

Tag
  id, family_id -> TagFamily, name, color
  (name unique innerhalb family_id)

TransactionTag
  transaction_id -> Transaction
  tag_id -> Tag
  PK (transaction_id, tag_id)

TransactionSplit
  id, transaction_id -> Transaction
  category_id -> Category
  amount (Numeric 14,2) — Summe aller Splits = Transaction.amount
  note (nullable)
  Constraint: mindestens 1 Split pro Buchung nach Migration

Contract
  id, name, kind (rent|insurance|subscription|loan|utility|other),
  counterparty_anchor (string, fuzzy-match key),
  amount_expected (Numeric, nullable bei variabel),
  frequency (monthly|quarterly|yearly|irregular),
  category_id -> Category (default-Zuordnung),
  start_date, end_date (nullable für laufend),
  notice_period_days (nullable),
  notes (text)

ContractBooking
  contract_id -> Contract
  transaction_id -> Transaction
  PK (contract_id, transaction_id)

CounterpartyProfile
  id, anchor (unique, normalisiert)
  display_name (lesbar)
  default_category_id (nullable)
  confidence_baseline (0.0..1.0)
  alternative_categories (JSON: list of {category_id, weight})
  last_seen_at, hits
```

## Änderungen an bestehenden Tabellen

```text
Transaction
  + has_splits (bool, default false) — Cache, ob TransactionSplit existiert
  + contract_id (nullable) — Quick-Lookup, redundant zu ContractBooking
  + counterparty_profile_id (nullable) — Cache nach Anker-Match
  - is_recurring (bleibt für Backwards-Compat, wird aber von
    Contract-Existenz abgeleitet)

Category
  + sort_order (int) — explizite Sortierung im Cascading-UI
  + description (text) — Kontext für LLM
```

## Migrationsplan (0.4.0)

1. **Dump** der bestehenden SQLite-DB als JSON nach `data/backups/`.
2. **Schema-Migration** (Alembic) – neue Tabellen, neue Spalten,
   keine Drops.
3. **Seed** der Kategorien-Hierarchie und Tag-Familien aus
   `docs/context/kategorien/`.
4. **Bestandsdaten-Migration**:
   - Für jede `Transaction` mit `category_id`: einen `TransactionSplit`
     anlegen mit `amount = transaction.amount`.
   - Counterparty-Profile aus den eindeutigen Counterpartys aufbauen,
     `default_category_id = häufigste vergebene Kategorie`.
   - `is_recurring=True` → Stub-`Contract` mit `kind=other`, manuell
     nachzupflegen.
5. **Smoke-Tests** gegen die Adapter-API, dass das alte Frontend weiter
   funktioniert.

## Offene Fragen

- Sollen Tags multi-select per Familie sein, oder soll das pro Familie
  einstellbar sein (Feld `is_multi_select` an `TagFamily`)?
- Wird `CounterpartyProfile.anchor` regex-basiert oder substring-basiert
  ermittelt? Aktuell hat `CategorizationRule` schon ein `match_field`.
- Sollen Contract-Bookings auch Splits unterstützen (anteiliger
  Mietvertrag bei WG)? Vermutlich nicht in 0.4.0.
