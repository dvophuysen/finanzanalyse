# Roadmap: Architektur-Migration

Drei Iterationen. Jede liefert einen vollständig deploybaren Stand.
Ziel: Datenmodell, UI und LLM-Kompetenz Schritt für Schritt heben,
ohne die App zwischendurch unbenutzbar zu machen.

## 0.4.0 – Daten-Fundament

Schema-Migration, Stammdaten-Seed, Bestandsdaten-Migration. UI bleibt
funktional über einen Adapter, der die neue Struktur auf das bestehende
Interface mappt (zeigt z. B. nur die Hauptkategorie an, ignoriert
Splits und Tags zunächst).

Beinhaltet:

- Neue Tabellen für **Tags**, **Tag-Familien**, **Splits**,
  **Verträge**, **Empfänger-Profile** (siehe `SCHEMA-DRAFT.md`)
- Seed der Kategorien-Hierarchie aus `kategorien/`
- Seed der Tag-Familien aus `kategorien/tags.md`
- Migration der 127 Bestandsbuchungen auf die neue Struktur
- DB-Export vor Migration als Rollback-Punkt
- Backend-Adapter, sodass das alte Frontend weiter läuft

Risiko: Schema-Änderung. Gegenmaßnahme: vollständiger Dump vor der
Migration, dry-run gegen Kopie, Idempotenz-Tests.

## 0.5.0 – UI-Revolution

Sichtbare Neuerung. Datenmodell ist bereits da, jetzt wird es bedienbar.

Beinhaltet:

- Cascading-Auswahl Hauptkategorie → Unterkategorie
- Tag-Editor (orthogonal zu Kategorie, mehrere Tags pro Buchung)
- Split-UI für Buchungen mit mehreren Kategorie-Anteilen
- Konfidenz-Anzeige (grün/gelb/rot) in der Transaktionsliste
- Eigene Vertragsübersicht-Seite

## 0.6.0 – KI-Kompetenz

Neuer LLM-Prompt mit der vollen Strukturkenntnis.

Beinhaltet:

- Empfänger-Profil-Logik (Anker → mehrere mögliche Kategorien je
  Counterparty, Konfidenz daraus abgeleitet)
- Konfidenz-Berechnung nach Konfliktlage (grün = ein Anker, gelb =
  mehrere plausible, rot = unbekannt)
- Familienkontext in den Prompt einspielen (aus `private/`)
- Recategorize-Run gegen Bestandsdaten

## Was bewusst draußen bleibt

- Mehrbenutzer-Modus
- Mobile-App
- Bankschnittstellen-Anbindung (CSV-Import bleibt der Weg)
