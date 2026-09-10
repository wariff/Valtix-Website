# Mandantenportal: Bestandsaufnahme und Umsetzungsplan

Antwort auf `docs/spec-mandantenportal.md`, Schritt 1 nach §1 der Spezifikation.
Stand: 10.09.2026. Noch nichts implementiert.

---

## 1 Bestandsaufnahme

### 1.1 Framework, Routing, Deployment

Es gibt kein Framework. Die Website ist eine Sammlung statischer HTML-Dateien,
die von Python-Skripten in `tools/` erzeugt werden. Routing ist der Dateipfad.

| Was | Stand |
|---|---|
| Framework | keines, statisches HTML |
| Generator | `tools/build_ratgeber.py`, `tools/build_leistungen.py`, `tools/build_portal_vorschau.py` |
| Auslieferung | GitHub Pages, Branch `gh-pages` |
| Auslöser | Push auf `main`, Workflow `.github/workflows/pages.yml`, `peaceiris/actions-gh-pages@v4` |
| Domain | valtixfm.de, CNAME im Repo |
| Nicht veröffentlicht | `.github`, `tools`, `docs`, `PLATZHALTER.md`, `README.md` |
| Prüfung | `node tools/check.mjs` (Überlauf, Konsolenfehler, tote Links), `tools/seo_audit.py` |

**Folge:** GitHub Pages liefert nur Dateien aus. Es gibt keinen Serverprozess,
keine Datenbank, keinen Dateispeicher, keine Sitzungen. Alles, was §3 bis §7
verlangt, braucht einen Unterbau, den es heute nicht gibt.

### 1.2 Das bestehende Interface

`portal-vorschau.html`, 66 KB, eine einzige Datei, erzeugt von
`tools/build_portal_vorschau.py` (1333 Zeilen).

- **Anmeldung ist eine Attrappe.** Das Passwort wird im Browser verglichen,
  es gibt keinen Server dahinter. Der Adminzugang führt bewusst nicht durch
  das Formular; die Verwaltungsansichten sind nur über die Adresse erreichbar
  (`#ansicht-mandanten`, `#ansicht-zugaenge`, `#ansicht-protokoll`).
- **Die Zahlen liegen als JSON-Block in der Seite** (`window.__valtix`),
  beim Bauen aus der Excel-Vorlage gelesen. Gezeichnet wird im Browser mit
  reinem JavaScript, ohne Bibliothek.
- **Aufbau:** Kopfzeile mit Monatswechsler, zwei Reiter (Überblick, Zahlen im
  Detail), Beraterkommentar, drei Kennzahlkacheln, Kennzahlen nach Ampelstatus
  gruppiert, Umsatzverlauf, Kuchendiagramm der Aufwendungen, Berichtskarte,
  Ergebnisrechnung mit aufklappbaren Blöcken.
- **Ansicht und Daten sind bereits getrennt.** Die Zeichenlogik kennt nur die
  Struktur `window.__valtix`. Wer diese Struktur später von einem Server
  liefert statt beim Bauen einzusetzen, kann die gesamte Ansicht unverändert
  weiterverwenden. Das ist der Hebel für §0 „kein Rewrite".

### 1.3 Auth, DB, Storage

Im Betrieb: nichts davon vorhanden.

Im Repo liegt ein **nicht ausgerollter Prototyp** unter `portal/` (FastAPI,
430 + 182 + 24 Zeilen):

- Anmeldung mit Argon2id, signierte Sitzungscookies (HttpOnly, SameSite,
  Secure), CSRF-Token auf allen verändernden Formularen, Bremse gegen
  Durchprobieren (5 Versuche / 5 Minuten / IP), gleiche Antwortzeit bei
  unbekannter Adresse, Sicherheitskopfzeilen.
- Rollentrennung `admin` / `mandant`, Rechteprüfung bei jedem Bericht.
- Zugänge werden angelegt, nicht registriert: einmaliger Einladungslink,
  die Person setzt ihr Passwort selbst, Valtix kennt es nie.
- SQLite mit vier Tabellen: `mandant`, `benutzer`, `bericht`, `protokoll`.
- Upload einer ausgefüllten Eingabevorlage erzeugt den Bericht über den
  vorhandenen Generator.

Das ist eine brauchbare Grundlage für M1, aber SQLite und lokale Dateien
tragen die Anforderungen aus §7 nicht (Mandantentrennung auf DB-Ebene,
signierte URLs, Virenscan, Aufbewahrung).

### 1.4 Datenmodell der Zahlen

`tools/bericht/` ist der belastbarste Teil des Repos.

| Datei | Aufgabe |
|---|---|
| `modell.py` | rechnet einen Berichtsmonat durch |
| `matrix.py` | liest die Vorlage als Monatsraster, alle Positionen über alle Monate, samt Zielwerten |
| `diagramme.py` | SVG-Diagramme für den Bericht |
| `rendern.py` | baut den Bericht als HTML |
| `test_abgleich.py` | vergleicht 20 Größen gegen den bestehenden Word-Bericht, derzeit 20/20 |

Zwei Entwurfsentscheidungen, die weiterhin gelten sollten: **es werden nur
Eingabefelder gelesen**, alle Summen werden selbst gerechnet, weil eine nie
geöffnete Excel-Datei keine Formelergebnisse gespeichert hat. Und
**Beschriftungen kommen aus der Datei**, damit umbenannte Zeilen ihren Namen
behalten.

---

## 2 Vier Widersprüche, die vor dem Bauen zu klären sind

### W1 Design: Glas ja oder nein

§6 verlangt „kein Glas-/Blur-Look". Genau dieser Look ist gestern auf
ausdrücklichen Wunsch eingebaut worden, weil die Oberfläche vorher „plump und
nicht mehrdimensional" wirkte. Er stammt aus `index.html` und wird dort seit
Beginn verwendet (`.glass`, Aurora-Hintergrund).

Auch die Farbwerte weichen ab:

| Rolle | Website heute | Spezifikation §6 |
|---|---|---|
| Navy | `#232941` | `#222A44` |
| Cream | `#F5EBD0` | `#F6EBCE` |
| Akzent | Gold `#A6813F` / `#7A6238` | „Amber" |

Die Unterschiede sind klein, aber nebeneinander sichtbar. **Was gilt?**

### W2 Eingabeblatt

§0 beschreibt ein Blatt `Eingabe_Rohdaten` mit „4 Blöcken à 12 Monatszeilen".
Die Vorlage im Repo (`tools/bericht/VALTIX_Eingabevorlage.xlsx`) hat sechs
Blätter (`0 Anleitung` bis `6 Prüfung`), **Positionen in Zeilen und Monate in
Spalten**, also genau andersherum. Gibt es eine zweite Vorlage, oder ist die
Beschreibung veraltet? Davon hängt §4.6 ab (Export spaltengleich zum
Eingabeblatt).

### W3 Cockpit

§0 nennt Word/PDF mit rund 14 Seiten und den Kapiteln Dashboard,
Halbjahresreview, Monatsauswertung, KPI-Ampel, Break-Even, Maßnahmen, Glossar.
Der Generator im Repo erzeugt HTML mit fünf Kapiteln: Cockpit, Verlauf,
Vormonatsvergleich, Ampel, Gewinnschwelle. Halbjahresreview, Maßnahmen und
Glossar fehlen.

Soll der Generator um diese Kapitel und eine PDF-Ausgabe erweitert werden,
oder bleibt Word der Weg und das Portal stellt nur die fertige Datei ein?
§8 verbietet den Umbau des Cockpit-Layouts, was für den zweiten Weg spricht.

### W4 „Kein Rewrite"

Die Vorgabe ist richtig für die **Ansicht**: das Dashboard bleibt, wie es ist,
und bekommt nur den Statusblock aus F1. Für den **Unterbau** gibt es nichts,
was erhalten bleiben könnte, weil es ihn nicht gibt. Der Prototyp unter
`portal/` ist der Ausgangspunkt, muss aber auf eine richtige Datenbank und
einen richtigen Dateispeicher umziehen.

Meine Lesart: kein Redesign, aber ein neuer Unterbau. Bitte bestätigen.

---

## 3 Umsetzungsplan

Vorbedingung für alles: die Entscheidungen aus §11, insbesondere Hosting und
Datenbank. Ohne die lässt sich M1 nicht anfangen.

### M0 Grundlage (neu, in §9 nicht enthalten)

Ohne diesen Schritt hängt jeder folgende in der Luft.

- Hosting und Datenbank aufsetzen, EU-Region, Sicherung eingerichtet
- Subdomain (Vorschlag `portal.valtixfm.de`), TLS, Zertifikat automatisch
- Prototyp von SQLite auf PostgreSQL umstellen, Mandantentrennung auf DB-Ebene
- Geheimnisse in die Umgebung, nichts im Code
- Mailversand einrichten und zustellbar machen (SPF, DKIM, DMARC)
- AVV mit jedem Auftragsverarbeiter, Liste der Subprozessoren anlegen

*Aufwand grob: 2 bis 4 Tage, stark abhängig vom gewählten Anbieter.*

### M1 Periodenlogik, Upload, Einreichen

- Datenmodell nach §5 (siehe Abschnitt 4)
- Periode je Mandant und Monat mit Status, rückwirkende Monate möglich
- Upload mit Drag & Drop, Mehrfachauswahl, Kamera auf dem Telefon,
  Fortschritt, Wiederaufnahme, Hash gegen Doppelte, Versionierung
- Dokumenten-Checkliste je Mandant, Standardliste aus F4, „entfällt" mit Grund
- Einreichen als eigener Schritt, danach gesperrt, Nachtrag über Knopf
- Statusblock im bestehenden Dashboard (F1), sonst keine Änderung daran
- Benachrichtigung an Valtix per E-Mail und in der Anwendung

*Aufwand grob: 5 bis 8 Tage.*

### M2 Adminbereich und Erinnerungen

- Matrix Mandanten × Monate mit Statusfarben, Filter, Notizfeld je Periode
- Sammel-Download als ZIP
- Erinnerung an den Mandanten zum konfigurierbaren Stichtag
- Bestätigungsmail an den Mandanten

*Aufwand grob: 3 bis 4 Tage.*

### M3 Extraktion der strukturierten Formate

- Warteschlange mit Wiederholung und sichtbarem Status, nicht im Request
- XLSX und CSV direkt lesen, DATEV-Export lesen
- PDF mit Textebene über `pdfplumber` oder `pdftotext -layout`
- Erkennung, ob eine Textebene vorhanden ist

*Aufwand grob: 5 bis 8 Tage, abhängig davon, wie einheitlich die DATEV-Exporte sind.*

### M4 OCR, Mapping, Freigabe

- OCR nur bei fehlender Textebene, Anbieter mit EU-Hosting und AVV
- Mapping SKR03/SKR04 und BWA-Zeilen auf die Valtix-Positionen,
  Regeln je Mandant speichern und im Folgemonat wiederverwenden
- Klärliste für unbekannte Positionen
- Prüfansicht mit Wert, Herkunft (Datei und Seite), Konfidenz
- Auffälligkeiten markieren: Vorzeichen, Bilanzsumme ungleich Aktiva/Passiva,
  Abweichung über x Prozent zum Vormonat, fehlende Pflichtfelder
- Freigabe durch Valtix, Korrekturen protokolliert
- Export der freigegebenen Periode als JSON und als XLSX, spaltengleich zum
  Eingabeblatt. Achtung: Zellinhalte, die mit `=`, `+`, `-` oder `@` beginnen,
  interpretiert Excel als Formel. Beim Schreiben mit einem Apostroph
  entschärfen.

*Aufwand grob: 8 bis 12 Tage. Das Mapping ist der unsicherste Posten,
weil es von den echten Dateien abhängt.*

### M5 Rücklauf und Feinschliff

- Fertiges Cockpit je Periode ins Portal, Benachrichtigung an den Mandanten
- Archiv aller Berichte mit Download
- Feinschliff der Bedienung, Barrierefreiheit, Tests auf dem Telefon

*Aufwand grob: 3 bis 5 Tage.*

**Summe grob: 26 bis 41 Arbeitstage.** Das ist eine Schätzung ohne Kenntnis
der echten DATEV-Dateien; M4 kann deutlich abweichen.

---

## 4 Datenmodell

Der Vorschlag aus §5 trägt. Fünf Anmerkungen dazu:

1. **`periode.status` als ausdrückliche Menge**, nicht als freier Text:
   `offen`, `hochgeladen`, `eingereicht`, `in_pruefung`, `freigegeben`,
   `bericht_gestellt`. F1 nennt fünf, für den Rücklauf braucht es den sechsten.
2. **`dokument.typ` verweist auf die Checkliste**, nicht auf einen freien Text.
   Dafür eine Tabelle `checkliste_slot` (mandant_id, schluessel, bezeichnung,
   pflicht, reihenfolge) und `dokument.slot_id`. Sonst lässt sich F4
   („konfigurierbar je Mandant") nicht abbilden.
3. **`dokument.entfaellt_grund`** für den Fall aus F4, dass der Mandant einen
   Slot begründet auf „entfällt" setzt. Ein Slot ohne Datei und ohne Grund ist
   offen, mit Grund ist er erledigt.
4. **`kennzahl_wert` braucht `periode_id` plus `feldschluessel` als
   eindeutigen Schlüssel** und eine Historie der Korrekturen. Vorschlag:
   der aktuelle Wert in `kennzahl_wert`, jede Änderung zusätzlich im
   `audit_log` mit vorher und nachher.
5. **`report`** sollte den Zeitraum und die Dateiart mitführen, damit ein
   Nachtrag eine neue Fassung erzeugen kann statt die alte zu überschreiben.

Der Feldschlüssel in `kennzahl_wert` sollte genau der Schlüssel sein, den
`tools/bericht/matrix.py` heute schon benutzt (`umsatz`, `variabel`, `fix`,
`liquide`, `dso`, …). Dann füttert die freigegebene Periode den vorhandenen
Generator ohne Übersetzungsschicht.

---

## 5 Was ich vorab wissen muss (§11)

1. **Stack, Hosting und Datenbank.** Vorschlag: Python mit FastAPI, weil der
   Prototyp und der gesamte Berichtsgenerator schon Python sind, dazu
   PostgreSQL und Objektspeicher in der EU. Ein Wechsel auf einen anderen
   Stack würde den Generator zerreißen. Ist das in Ordnung, und bei welchem
   Anbieter?
2. **OCR-Anbieter.** Azure Document Intelligence, Google Document AI oder AWS
   Textract, jeweils EU-Region mit AVV. Gibt es eine Präferenz oder einen
   Ausschluss?
3. **DATEV-Export als Hauptweg?** Wenn ja, wird M4 kleiner und die Genauigkeit
   deutlich besser. Bekommen die Mandanten die Bitte an ihren Steuerberater
   weitergegeben?
4. **Wer gibt frei?** Nur Valtix, oder muss der Mandant die extrahierten Werte
   gegenzeichnen? Das ändert Ansichten und Protokoll.
5. **Wie viele Mandanten und wie viel Datenvolumen** im ersten Jahr? Davon
   hängen Anbieterwahl und Kosten ab.
6. **Bestehende Auth-Lösung.** Es gibt keine im Betrieb. Soll der Prototyp
   (eigene Anmeldung mit Einladungslink) weitergeführt werden, oder ein
   fremder Anbieter?

Dazu die vier Widersprüche aus Abschnitt 2.

---

## 6 Was ich ohne Freigabe nicht tue

Nichts implementieren. Der nächste Schritt ist Ihre Antwort auf Abschnitt 2
und 5, danach M0 und M1.
