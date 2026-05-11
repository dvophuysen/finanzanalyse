# App-Kontext

Strukturierte Doku zur Datenarchitektur, Kategorien-Systematik und
Roadmap der Finanzanalyse-App. Dient als Single Source of Truth für
Schema-Entscheidungen, Migrations-Schritte und das fachliche Modell.

## Anti-PII-Policy

Dieses Repo ist **öffentlich**. In `docs/context/` darf ausschließlich
**strukturelles** Wissen liegen, keine personenbezogenen Daten.

| Erlaubt hier | Nicht erlaubt hier |
|---|---|
| Kategorien-Hierarchie (generische Namen) | Klarnamen von Personen, Vermietern, Empfängern |
| Tag-Familien und deren Werte | Konkrete Beträge aus realen Buchungen |
| Vertragsschema, Felder, Lifecycle | Konkrete Vertragsdaten (Mietverträge, Versicherungen) |
| Architektur-ADRs, Roadmap | IBANs, Kontostände, Bankzugangsdaten |
| Beispiel-Anker abstrakt („Friseur=Floristik-Mehrdeutigkeit") | Reale Empfänger-Strings („Custom Art Tattoo = …") |

Personenbezogene Daten gehören in `private/` (gitignored) oder werden
zur Laufzeit über das Admin-UI in der DB gepflegt.

## Inhalt

| Pfad | Zweck |
|---|---|
| `ROADMAP.md` | Drei-Iterations-Plan für die Architektur-Migration |
| `SCHEMA-DRAFT.md` | Vorgeschlagenes neues Datenmodell (Tags, Splits, Verträge, Empfänger-Profile) |
| `kategorien/` | Kategorien-Katalog und Tag-Familien (Struktur, ohne PII) |
| `vertraege/` | Vertragsschema und Lifecycle (Struktur, ohne PII) |
| `entscheidungen/` | Architecture Decision Records |

## Status

Skelett steht. Inhalte werden aus dem privaten Context-Repo
übernommen, sobald sie PII-bereinigt sind.
