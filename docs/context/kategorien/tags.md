# Tags

Tags sind **orthogonale Dimensionen** zu Haupt-/Unterkategorie. Pro Buchung
beliebig viele Tags erlaubt. Format: `familie:wert`.

Phase-1-Tag-Familien (sofort einführen): `person`, `vertrag`, `steuer`,
`bedarf`, `cashflow`, `kosten-typ`, `umbuchung-typ`, `lifecycle`, `mngmt`,
`aktion`, `quelle`, `kontext`, `frequenz`, `anlass`, `markt`, `qualitaet`.

> Familien mit **anwender-spezifischen Werten** (`person`, `vertrag`,
> `quelle`, `kontext`) sind hier nur **strukturell** dokumentiert. Die
> konkreten Wert-Belegungen liegen in `private/` und werden zur Laufzeit
> geseedet.

---

## person:

Wer ist wirtschaftlich Begünstigter / Anlassgeber der Buchung.

Strukturelle Werte (Slots):

| Wert | Verwendung |
|---|---|
| `person:elternteil-a` | erster Elternteil im Haushalt |
| `person:elternteil-b` | zweiter Elternteil im Haushalt |
| `person:kind-1` … `person:kind-n` | Kinder im Haushalt |
| `person:familie` | ganzer Haushalt |
| `person:eltern` | beide Elternteile |
| `person:kinder` | alle Kinder |
| `person:extern` | Begünstigter außerhalb des Haushalts |

Die **lesbaren Namen** werden im UI aus `private/familie.md` gemappt.
Mehrfachverwendung erlaubt (`person:elternteil-a,person:elternteil-b` für
Eltern-Aktivität).

---

## vertrag:

Verknüpft eine Buchung mit einer Vertragsdatei in `vertraege/<slug>.md` bzw.
mit einem `Contract`-Datensatz in der DB. Pflicht bei wiederkehrenden
Posten.

Slug-Konvention: `<typ>-<kurzbezeichnung>`, z. B.:

- `vertrag:miete-hauptwohnsitz`
- `vertrag:mobilfunk-elternteil-a`
- `vertrag:musikschule-kind-1`
- `vertrag:streaming-bundle-haushalt`

Konkrete Vertragsdaten (Anbieter-Klarnamen, Beträge, Vertragsnummern)
liegen in `private/contracts/` bzw. werden über das Admin-UI gepflegt.

---

## steuer:

Steuerrelevanz nach deutschem Steuerrecht. Erlaubt Selektion für
Steuererklärung und Anlagen-Vorbereitung.

| Wert | Was rein gehört |
|---|---|
| `steuer:sonderausgabe` | Spenden, Schulgeld (Privatschule), Kirchensteuer |
| `steuer:vorsorgeaufwand` | Kranken-, Pflege-, BU-, RLV-, Renten-Versicherungsbeiträge |
| `steuer:werbungskosten` | beruflich verauslagt: Pendeln, Arbeitsmittel, Fortbildung, Berufsverband |
| `steuer:haushaltsnah` | Schornsteinfeger, Reinigung, Garten, Handwerker (Lohnanteil) |
| `steuer:aussergew-belastung` | Krankheitskosten Eigenanteile, Pflege, Beerdigung |
| `steuer:spende-zuwendung` | speziell für Spenden mit Quittung |
| `steuer:kapitalertrag` | Zinsen, Dividenden, Kursgewinne (Anlage KAP) |
| `steuer:vermietung` | Anlage V |
| `steuer:nicht-abzugsfaehig` | bewusst gesetzt für Klarheit |

---

## bedarf:

Bedarfs-Klassifizierung – ermöglicht „Existenzminimum vs. Lifestyle"-Analyse.

| Wert | Beispiele |
|---|---|
| `bedarf:existenziell` | Miete, Strom-Grundbedarf, Wasser, Lebensmittel-Grundbedarf, Pflichtversicherungen, BU/Krankenversicherung, Mobilität-zur-Arbeit |
| `bedarf:notwendig` | Standard-Bekleidung, Standard-Telekommunikation, Schul-Beiträge der Kinder, Apothekenkosten, Routine-Gesundheit |
| `bedarf:lebensqualitaet` | Hobbys mit Maß, Vereinsbeiträge, Restaurant gelegentlich, Bücher/Streaming Standard |
| `bedarf:luxus` | Premium-Tarife wo Standard reichen würde, hochpreisige Geschenke, exklusive Reisen, mehrfache redundante Abos |

Auswertung: „Was würde im Notfall wegfallen?" = alles außer
`existenziell`/`notwendig`.

---

## cashflow:

Buchhalterisch saubere Cashflow-Klassifizierung (in Anlehnung an GuV).

| Wert | Bedeutung |
|---|---|
| `cashflow:operativ` | laufender Lebensbedarf (Kategorien 01–19) |
| `cashflow:investiv` | Sparen, Vermögensaufbau, große Werte mit Werterhalt (20) |
| `cashflow:finanzierung` | Kreditaufnahme, Tilgung, Zinsen (18) |
| `cashflow:transitorisch` | Umbuchungen zwischen eigenen Konten (21) |
| `cashflow:steuer` | Steuerbewegungen (22) |
| `cashflow:einkommen` | Einnahmen-Buchungen (30–35) |

---

## kosten-typ:

Plan- und Steuerbarkeit des Postens.

| Wert | Bedeutung |
|---|---|
| `kosten-typ:fix` | vertraglich gebunden, monatlich/jährlich planbar |
| `kosten-typ:variabel` | laufender Verbrauch, Höhe schwankt |
| `kosten-typ:einmalig-gross` | Sonderlage / größere Einzelanschaffung |

---

## umbuchung-typ:

Bei Buchungen mit Hauptkategorie 21 detaillieren, was es genau ist.

| Wert |
|---|
| `umbuchung-typ:eigene-konten` |
| `umbuchung-typ:sparbudget` |
| `umbuchung-typ:wechselgeld` |
| `umbuchung-typ:cc-ausgleich` |
| `umbuchung-typ:paypal-aufladung` |
| `umbuchung-typ:zwischen-personen` |

---

## lifecycle:

Lebenszyklus eines Postens.

| Wert |
|---|
| `lifecycle:abo-aktiv` |
| `lifecycle:abo-beendet` |
| `lifecycle:abo-probezeit` |
| `lifecycle:saisonal` |
| `lifecycle:einmalig` |
| `lifecycle:projekt-laufend` |

---

## mngmt:

Vertrags-/Posten-Management-Hinweis (was ist mit dem Posten vorgesehen).

| Wert |
|---|
| `mngmt:kuendigungs-kandidat` |
| `mngmt:tarifwechsel-faellig` |
| `mngmt:review-noetig` |
| `mngmt:bewusst-behalten` |

---

## aktion:

Konkrete Beratungs-Maßnahme, die noch offen ist.

| Wert | Typischer Anlass |
|---|---|
| `aktion:kuendigen` | nicht mehr benötigter Vertrag |
| `aktion:hoeherstufen` | Versicherungssumme zu niedrig |
| `aktion:tarifwechsel` | Strom-/Gas-/Mobilfunk-Wechsel anstehend |
| `aktion:vergleich-noetig` | Marktcheck überfällig |
| `aktion:dokumentieren` | Vertragsdetails unklar, Unterlagen suchen |
| `aktion:steueranlage` | in Steuererklärung angeben |
| `aktion:nichts-tun` | bewusst geprüft, ist ok |

---

## quelle:

Bezahlweg/Quellkonto. Hilft bei Doppelbuchungs-Erkennung
(z. B. PayPal-Buchung vs. Giro-Lastschrift derselben Transaktion).

Strukturelle Werte:

| Wert | Bedeutung |
|---|---|
| `quelle:giro` | Hauptkonto-Lastschrift / -Überweisung |
| `quelle:visa-debit-<inhaber-slot>` | Kartenzahlung, pro Karteninhaber instanziert |
| `quelle:paypal-<inhaber-slot>` | PayPal, pro Account instanziert |
| `quelle:bargeld` | Barzahlung |
| `quelle:dauerauftrag` | wiederkehrender Auftrag |
| `quelle:sepa-lastschrift` | Einzugsermächtigung |
| `quelle:ueberweisung` | Einmal-Überweisung |
| `quelle:kartenzahlung` | generisch, wenn Karte nicht differenzierbar |

Konkrete Karten-/Account-Inhaber werden aus `private/konten.md` geseedet.

---

## kontext:

Freie Episoden-Klammerung für „Total Cost of Event"-Auswertungen.
Format: `kontext:<freier-slug>-<jahr>`.

Beispiele (Slug-Form, ohne reale Werte):

- `kontext:urlaub-<reiseziel>-<jahr>`
- `kontext:reparatur-<objekt>-<jahr>`
- `kontext:einschulung-<kind-slot>-<jahr>`
- `kontext:geburtstag-<person-slot>-<jahr>`

Konkrete `kontext:`-Slugs entstehen ad hoc beim Einbuchen und werden
nicht zentral verwaltet.

---

## anlass:

Standardisierte Lebensphasen-/Anlass-Tags (eingeschränkter Wertebereich
gegenüber `kontext:`).

| Wert |
|---|
| `anlass:geburt` |
| `anlass:einschulung` |
| `anlass:umzug` |
| `anlass:hochzeit` |
| `anlass:beerdigung` |
| `anlass:krankheit-laengerfristig` |
| `anlass:reise` |
| `anlass:reparatur` |

---

## frequenz:

Wiederholungs-Charakter (kann aus Vertragsdaten abgeleitet werden).

| Wert |
|---|
| `frequenz:monatlich` |
| `frequenz:quartalsweise` |
| `frequenz:halbjaehrlich` |
| `frequenz:jaehrlich` |
| `frequenz:einmalig` |
| `frequenz:saisonal` |
| `frequenz:unregelmaessig` |

---

## markt:

Vertrags-Marktbewertung. Wird beim Vertrags-Audit gepflegt (manuell oder
über Berater).

| Wert |
|---|
| `markt:guenstig` |
| `markt:marktueblich` |
| `markt:teuer` |
| `markt:nicht-vergleichbar` |
| `markt:nicht-bewertet` |

---

## qualitaet:

Datenqualität / Konfidenz der Kategorisierung. Macht die App selbstreflexiv
und liefert Trainingssignal für die KI.

| Wert |
|---|
| `qualitaet:auto-hoch` |
| `qualitaet:auto-mittel` |
| `qualitaet:auto-niedrig` |
| `qualitaet:manuell` |
| `qualitaet:konflikt` |

---

## Standard-Tag-Sets pro Buchungstyp

Damit nicht jede Buchung manuell durchgetaggt werden muss, gelten
Default-Tag-Profile pro Vertrag/Vorgangstyp. Strukturelle Beispiele:

**Miete (Hauptwohnsitz):**
- `vertrag:miete-hauptwohnsitz`, `person:familie`, `bedarf:existenziell`,
  `cashflow:operativ`, `kosten-typ:fix`, `lifecycle:abo-aktiv`,
  `frequenz:monatlich`, `quelle:dauerauftrag`

**ETF-Sparplan Altersvorsorge:**
- `vertrag:etf-sparplan-altersvorsorge`, `person:eltern`,
  `bedarf:notwendig`, `cashflow:investiv`, `kosten-typ:fix`,
  `lifecycle:abo-aktiv`, `frequenz:monatlich`

**Streaming-Bundle Haushalt:**
- `vertrag:streaming-bundle-haushalt`, `person:familie`,
  `bedarf:lebensqualitaet`, `cashflow:operativ`, `kosten-typ:fix`,
  `lifecycle:abo-aktiv`, `frequenz:monatlich`,
  `quelle:visa-debit-elternteil-a`

**Berufsunfähigkeitsversicherung:**
- `vertrag:bu-elternteil-a`, `person:elternteil-a`, `bedarf:existenziell`,
  `cashflow:operativ`, `kosten-typ:fix`, `steuer:vorsorgeaufwand`,
  `lifecycle:abo-aktiv`, `mngmt:review-noetig`, `aktion:hoeherstufen`,
  `frequenz:monatlich`

**Förderverein (Beispiel für Kündigungs-Kandidat):**
- `vertrag:foerderverein-<slug>`, `person:elternteil-a`,
  `bedarf:luxus`, `cashflow:operativ`, `kosten-typ:fix`,
  `steuer:spende-zuwendung`, `lifecycle:abo-aktiv`,
  `mngmt:kuendigungs-kandidat`, `aktion:kuendigen`,
  `frequenz:jaehrlich`

Die anwender-spezifischen Standard-Sets (echte Vertrags-Slugs, reale
Personen-Zuordnungen) liegen in `private/standard-tag-sets.md`.
