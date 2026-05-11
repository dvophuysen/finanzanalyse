# Privat-Daten (gitignored)

Alles unter `private/` wird **nicht** versioniert. Hier liegen
anwender-spezifische Inhalte, die im öffentlichen Repo nichts verloren
haben.

## Erwarteter Inhalt

| Pfad | Zweck |
|---|---|
| `kategorien/anker-und-mehrdeutigkeiten.md` | Reale Empfänger-Strings + Kategorie-Mapping |
| `contracts/*.md` oder `contracts.yaml` | Konkrete Verträge mit Vermieter, Beträgen, Lifecycle |
| `familie.md` | Familienkontext für den LLM-Prompt |
| `vermoegen-snapshot.md` | Optional: Stand der Vermögenswerte |

## Wie die App damit umgeht

Der Backend-Seeder prüft, ob `private/` existiert und liest – falls
vorhanden – diese Dateien zusätzlich zur strukturellen Doku aus
`docs/context/` ein. Fehlen sie, läuft die App trotzdem (mit leerer
Kontext-Kenntnis, bis der Anwender Daten im UI pflegt).

## Sicherheit

- Niemals `git add private/` oder `git add -A` ohne vorherigen
  `git status`-Check.
- Backup auf Host-Ebene reicht (HA-Backup deckt `/data` ab).

Diese README wird als einzige Datei in `private/` versioniert, damit
der Ordner im Repo sichtbar bleibt.
