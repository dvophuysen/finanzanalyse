# Verträge

Strukturelle Definition des Vertragsschemas. Konkrete Vertragsdaten
(Vermieter, Versicherungsgesellschaften, Beträge) sind PII und gehören
in `private/contracts/` oder werden über das Admin-UI in der DB
gepflegt.

## Vertragsarten

- `rent` – Wohnungsmiete, Stellplatz, Lagerraum
- `insurance` – Haftpflicht, Hausrat, KFZ, Kranken, Leben
- `subscription` – Streaming, Telekom, Cloud-Dienste
- `loan` – Kredit, Finanzierung
- `utility` – Strom, Gas, Wasser, Internet
- `other` – alles, was nicht in die obigen passt

## Lifecycle-Felder

Siehe `../SCHEMA-DRAFT.md` Abschnitt „Contract". Pflichtfelder:

- `name`, `kind`, `counterparty_anchor`, `frequency`, `category_id`,
  `start_date`
- `amount_expected` darf null sein bei variablen Beträgen (Strom,
  Wasser)
- `end_date` null = laufend

## Erkennungs-Heuristik

Eine Buchung wird einem Vertrag zugeordnet, wenn:

1. `counterparty` matcht `Contract.counterparty_anchor` (fuzzy oder
   regex, siehe Diskussion in `SCHEMA-DRAFT.md`)
2. Buchungsdatum liegt im Lifecycle-Fenster
3. Optional: Betrag liegt innerhalb einer Toleranz um
   `amount_expected` (z. B. ±10 %)
