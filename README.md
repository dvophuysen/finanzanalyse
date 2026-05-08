# Finanzanalyse

Selbst-gehostetes Haushaltsbuch als **Home-Assistant-Add-on** mit
KI-gestützter Auto-Kategorisierung von Banktransaktionen.

## Funktionen

- CSV-Import gängiger Online-Banking-Exporte
- Lernende Auto-Kategorisierung (Regelwerk + LLM-Fallback)
- Dashboard mit Cashflow-Verlauf und Kategorien-Aufteilung
- Inline-Kategorisierung in der Transaktionsliste
- Sparziele mit Fortschrittsanzeige
- LLM-Provider austauschbar: Azure OpenAI, OpenAI, Anthropic, Ollama

## Installation

In Home Assistant:

1. **Einstellungen → Add-ons → Add-on Store → ⋮ → Repositories**
2. Adresse hinzufügen:
   ```
   https://github.com/dvophuysen/finanzanalyse
   ```
3. Add-on **Finanzanalyse** installieren, in der Konfiguration die
   LLM-Verbindungsdaten eintragen, starten.

Detaillierte Anleitung: [`docs/installation.md`](docs/installation.md)

## Stack

| Schicht | Technologie |
|---|---|
| Add-on | Home Assistant Supervisor + Ingress |
| Frontend | Next.js 14, TypeScript, Tailwind, Recharts (statisch exportiert) |
| Backend | Python 3, FastAPI, SQLAlchemy |
| Datenbank | SQLite (in `/data`, Teil der HA-Backups) |
| KI | Azure OpenAI (Default) – konfigurierbar |

## Datenhaltung

Die Datenbank liegt ausschließlich lokal auf dem Host, der das Add-on
ausführt. Vor LLM-Anfragen werden personenbezogene Felder maskiert.

## Repo-Struktur

```
.
├── repository.yaml          # HA-Add-on-Repo-Marker
├── finanzanalyse/           # Das Add-on
│   ├── config.yaml
│   ├── Dockerfile
│   ├── build.yaml
│   ├── run.sh
│   ├── backend/             # FastAPI
│   └── frontend/            # Next.js
├── docs/installation.md
└── docker-compose.yml       # Optionaler Dev-Stack
```

## Lizenz

Privatprojekt. Nutzung auf eigene Verantwortung.
