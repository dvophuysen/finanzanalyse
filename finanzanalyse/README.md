# Finanzanalyse – Home Assistant Add-on

Haushaltsbuch mit KI-gestützter Auto-Kategorisierung.

## Konfiguration

| Option | Beschreibung |
|---|---|
| `llm_provider` | KI-Quelle (`azure` / `openai` / `anthropic` / `ollama`) |
| `azure_openai_endpoint` | Endpoint-URL der Azure-OpenAI-Resource |
| `azure_openai_api_key` | API-Key der Resource |
| `azure_openai_deployment` | Name des Modell-Deployments |
| `azure_openai_api_version` | API-Version, Default `2024-10-21` |
| `household_adults` / `household_children` | Optionale Haushaltsangaben (für künftige Benchmark-Funktionen) |

## Persistenz

Die SQLite-Datenbank liegt unter `/data/finanzanalyse.db` und ist
automatisch Teil der Home-Assistant-Snapshots.

## Bedienung

Nach dem Start erscheint **Finanzen** in der HA-Sidebar (Ingress).
Konto anlegen → CSV importieren → Kategorien prüfen.
