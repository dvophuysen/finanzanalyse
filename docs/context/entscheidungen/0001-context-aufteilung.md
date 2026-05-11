# ADR 0001 – Aufteilung Kontext-Wissen: öffentlich vs. privat

Status: angenommen, 2026-05-11

## Kontext

Die App-Architektur erfordert detailliertes Domänen-Wissen
(Kategorien-Hierarchie, Tag-Familien, Vertragsschema,
Empfänger-Mehrdeutigkeiten). Dieses Wissen wuchs bisher in einem
privaten Context-Repo. Für die Implementierungsarbeit muss es im
App-Repo erreichbar sein – das aber ist öffentlich.

## Entscheidung

Wissen wird in zwei Klassen geteilt:

1. **Strukturell, generisch** → `docs/context/` im öffentlichen
   App-Repo. Enthält Kategorien-Hierarchie ohne Klarnamen,
   Tag-Familien-Schema, Vertragsschema, ADRs, Roadmap.
2. **Personenbezogen** → `private/` (gitignored) oder direkt in der
   DB via Admin-UI. Enthält reale Empfänger-Strings, konkrete
   Verträge mit Beträgen, Familienkontext, Vermögens-Snapshots.

Trennlinie wird über die Anti-PII-Policy in `docs/context/README.md`
gezogen und vor jedem Commit geprüft.

## Konsequenzen

- App-Code bleibt generisch und Open-Source-tauglich.
- Anwender-spezifische Daten leaken nicht ins öffentliche Repo.
- Seed-Logik liest aus `docs/context/` (Struktur) und optional aus
  `private/` (Inhalte).
- Beim Übernehmen aus dem privaten Context-Repo muss jede Datei
  PII-bereinigt werden, bevor sie nach `docs/context/` wandert.
