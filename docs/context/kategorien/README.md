# Kategorien

Strukturelle Definition der Kategorien-Hierarchie und der Tag-Familien.

## Erwartete Dateien

| Datei | Inhalt | Status |
|---|---|---|
| `katalog.md` | Hauptkategorie → Unterkategorie-Hierarchie, generische Namen | offen |
| `tags.md` | Tag-Familien, deren Werte, Multi-Select-Eigenschaft | offen |
| `anker-und-mehrdeutigkeiten.md` | **Bleibt im privaten Context-Repo / `private/`** – enthält reale Empfänger-Strings | n. a. |

## Format-Konvention

Markdown mit Listen-Hierarchie. Erste Ebene = Hauptkategorie, zweite =
Unterkategorie. Für die Migration relevant: jede Zeile auf zweiter Ebene
wird zu einem `Category`-Datensatz mit gesetztem `parent_id`.

Beispiel-Layout (Platzhalter, ersetzt durch Inhalte aus dem Context-Repo):

```markdown
- Lebenshaltung
  - Lebensmittel
  - Drogerie
  - Haushalt
- Wohnen
  - Miete
  - Nebenkosten
  - Instandhaltung
```

Personenbezogene Beispiele (Klarnamen, Beträge) gehören **nicht** in
dieses Verzeichnis.
