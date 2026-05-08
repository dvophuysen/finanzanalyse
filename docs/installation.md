# Installations-Anleitung

Schritt-für-Schritt-Anleitung zur Installation des Add-ons in Home Assistant OS.

Du brauchst:
- Ein laufendes **Home Assistant OS**
- Einen Browser, in dem Home Assistant geöffnet ist
- Einen **Azure-OpenAI-Endpoint** mit deployten Modell (Endpoint, API-Key, Deployment-Name)

Geplante Zeit: ca. 15 Minuten.

---

## Schritt 1 – Verbindungswerte aus Azure besorgen

1. Anmelden auf **portal.azure.com**.
2. Suche oben nach **"Azure OpenAI"** und öffne die betreffende Resource.
3. In der Seitenleiste auf **"Keys and Endpoint"** klicken. Notiere:
   - **Endpoint** (Form: `https://<name>.openai.azure.com`)
   - **API-Key** (Key 1, Augensymbol klicken zum Anzeigen)
4. In der Seitenleiste **"Model deployments"** öffnen und den **Deployment-Namen**
   notieren – das ist nicht der Modellname, sondern der vergebene Deployment-Name
   (Spalte "Deployment name").

---

## Schritt 2 – Repository in Home Assistant hinzufügen

1. Home-Assistant-Oberfläche öffnen.
2. Profil-Icon (unten links) → sicherstellen, dass **"Erweiterter Modus"** aktiv ist.
3. **Einstellungen → Add-ons → Add-on Store**.
4. Oben rechts auf **⋮ → Repositories**.
5. Adresse einfügen:
   ```
   https://github.com/dvophuysen/finanzanalyse
   ```
6. **Hinzufügen** → **Schließen**.

Im Add-on-Store erscheint nun eine neue Sektion mit dem Add-on **Finanzanalyse**.

---

## Schritt 3 – Add-on installieren

1. Im Store auf die Kachel **Finanzanalyse** klicken.
2. **Installieren** klicken.
3. Beim ersten Mal dauert der Build 5–15 Minuten.

---

## Schritt 4 – Konfiguration

Reiter **Configuration** öffnen, ausfüllen:

| Feld | Wert |
|---|---|
| `llm_provider` | `azure` |
| `azure_openai_endpoint` | dein Endpoint aus Schritt 1 |
| `azure_openai_api_key` | dein Key aus Schritt 1 |
| `azure_openai_deployment` | dein Deployment-Name aus Schritt 1 |
| `azure_openai_api_version` | `2024-10-21` (Default beibehalten) |
| `household_adults` | optional |
| `household_children` | optional |

**Speichern**.

---

## Schritt 5 – Add-on starten

1. Reiter **Info**.
2. **"Beim Hochfahren starten"** und **"Watchdog"** aktivieren.
3. **Starten**.
4. Nach 10–20 s Reiter **Log** prüfen. Erwartete Zeile am Ende:
   `Application startup complete`.

---

## Schritt 6 – Bedienung

In der HA-Sidebar erscheint **Finanzen**.

1. Reiter **Import** → neues Konto anlegen → CSV des Online-Bankings hochladen.
2. Reiter **Transaktionen** → Kategorien prüfen, ggf. korrigieren.
3. Reiter **Dashboard** → Cashflow- und Kategorien-Übersicht.

---

## Externer Zugriff (optional)

Wenn HA von außen erreichbar ist (Nabu Casa, Cloudflare Tunnel, eigene
Reverse-Proxy-Lösung), ist das Add-on automatisch über dieselbe URL erreichbar.
Eine eigene Tunnel-Einrichtung ist nicht Teil dieses Add-ons.

---

## Troubleshooting

| Problem | Vorgehen |
|---|---|
| Add-on erscheint nicht im Store | Browser neu laden, Add-on-Store oben rechts → Repositories prüfen |
| Build schlägt fehl | Reiter **Log** prüfen; meist Speicherplatz oder Internet. Pi neustarten. |
| 500-Fehler beim Import | Reiter **Log** prüfen; meist falsche LLM-Verbindungswerte (Endpoint mit/ohne Slash, Modellname statt Deployment-Name) |
| KI kategorisiert falsch | In der Transaktionsliste korrigieren – das Add-on lernt aus jeder Korrektur |
| Sidebar-Eintrag fehlt | Add-on neu starten, Browser hart aktualisieren (Strg+Shift+R) |
