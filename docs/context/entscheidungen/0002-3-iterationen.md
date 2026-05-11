# ADR 0002 – Drei-Iterations-Schnitt für die Architektur-Migration

Status: angenommen, 2026-05-11

## Kontext

Datenmodell, UI und LLM-Kompetenz müssen erweitert werden (Tags,
Splits, Verträge, Empfänger-Profile). Eine Big-Bang-Migration wäre
riskant, fünf kleine Schritte würden zu viele halbe Zustände erzeugen.

## Entscheidung

Drei Versionen, jede vollständig deploybar:

| Version | Inhalt |
|---|---|
| 0.4.0 | Schema + Seed + Bestandsdaten-Migration + Backend-Adapter (UI bleibt) |
| 0.5.0 | UI-Revolution: Cascading, Tag-Editor, Split-UI, Konfidenz-Anzeige, Vertragsübersicht |
| 0.6.0 | LLM-Prompt mit Empfänger-Profilen, Konfidenz-Logik, Recategorize-Lauf |

Begründung:

- **0.4.0 muss atomar** sein, weil Schema + Seed + Migration eng
  gekoppelt sind. Trennen würde inkonsistente Zustände erzeugen.
- **UI und LLM** lassen sich danach sauber trennen, weil die
  Datenbank-Struktur stabil ist.
- Die App bleibt in jeder Phase produktiv nutzbar.

## Konsequenzen

- Vor 0.4.0-Push ein voller DB-Dump nach `data/backups/`.
- Backend-Adapter ist Wegwerf-Code, wird in 0.5.0 entfernt, sobald
  das neue UI die Splits/Tags selbst rendert.
- Jeder Versions-Push begleitet von Smoke-Test gegen reale CSV-Daten.
