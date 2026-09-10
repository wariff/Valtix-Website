# Claude-Code-Prompt: Valtix Mandantenportal (Upload → Extraktion → Cockpit)

> Zum Einfügen in Claude Code. Kann zusätzlich als `docs/spec-mandantenportal.md` im Repo abgelegt werden.

---

## 0. Kontext

Valtix Financial Management (valtixfm.de) liefert Mandanten monatlich ein Management Cockpit
(Word/PDF, ~14 Seiten, Kapitel: Dashboard, Halbjahresreview, Monatsauswertung, KPI-Ampel,
Break-Even, Maßnahmen, Glossar). Datenbasis ist eine Excel-Vorlage („Basismodell") mit dem
Eingabeblatt `Eingabe_Rohdaten` (4 Blöcke à 12 Monatszeilen: GuV-Positionen, operative
Kennzahlen, Bilanzdaten, Break-Even-Parameter).

Auf der Website existiert bereits ein Interface inkl. Dashboard mit Kennzahlen.
**Dieses Interface bleibt erhalten und wird erweitert – kein Rewrite, kein Redesign.**

## 1. Erster Schritt: Bestandsaufnahme, dann Plan – noch nicht bauen

1. Repo analysieren und knapp dokumentieren: Framework, Routing, Auth, DB/Storage, Deployment,
   Aufbau des bestehenden Dashboards, vorhandene Datenmodelle.
2. Auf dieser Basis einen Umsetzungsplan mit Meilensteinen (siehe §9) und Datenmodellvorschlag
   vorlegen.
3. Offene Punkte aus §11 als konkrete Fragen stellen.
4. **Erst nach meiner Freigabe implementieren**, danach Meilenstein für Meilenstein – jeder
   Meilenstein für sich lauffähig und testbar.

## 2. Zielbild

Ein Mandantenportal, in dem der Mandant pro Monat seine Unterlagen hochlädt und einreicht.
Valtix erhält eine Eingangsmeldung, die Dateien werden automatisch ausgelesen, in das
Basismodell-Schema gemappt, von Valtix freigegeben und fließen ins Cockpit. Der fertige Report
kommt über dasselbe Portal zurück.

Referenz für Bedienlogik und Reduziertheit: **Finban**. Nicht kopieren – Orientierung für
Klarheit, wenige Klicks, verständliche Sprache für Nicht-Kaufleute.

## 3. Funktionale Anforderungen

**F1 – Dashboard (Bestand):** bleibt unverändert Startseite. Ergänzung nur um einen
Statusblock „Unterlagen aktueller Monat" (offen / hochgeladen / eingereicht / in Bearbeitung /
freigegeben).

**F2 – Periodenlogik:** Jede Monatsperiode (`YYYY-MM`) je Mandant ist ein eigener Datensatz mit
Status. Rückwirkende Uploads für frühere Monate sind jederzeit möglich (Monatsauswahl über
Dropdown/Liste mit Ampel je Monat: vollständig / unvollständig / fehlt).

**F3 – Upload:** Drag & Drop, Mehrfachauswahl, Mobile-Kamera-Upload, Fortschrittsanzeige,
Wiederaufnahme bei Abbruch. Erlaubt: PDF, JPG/PNG, XLSX/CSV, DATEV-Exportformate.
Limits, MIME-Prüfung, Duplikatserkennung per Hash, Versionierung (korrigierte Datei ersetzt
alte, alte bleibt archiviert).

**F4 – Dokumenten-Checkliste je Monat:** konfigurierbar je Mandant, Default:
BWA, Summen- und Saldenliste, OPOS Debitoren, OPOS Kreditoren, Kontensaldenliste/Kontoauszüge,
Bestandsliste, Lohnjournal, Investitionsliste. Jeder Slot zeigt an, ob befüllt.
Nicht Zutreffendes kann der Mandant mit Begründung auf „entfällt" setzen.

**F5 – Einreichen:** eigener, bewusster Schritt („Unterlagen einreichen"), inkl. Hinweis auf
Vollständigkeit. Danach ist die Periode für den Mandanten gesperrt (Nachreichen nur über
Button „Nachtrag" → neue Version, Admin wird erneut informiert).

**F6 – Benachrichtigungen:** bei Einreichung E-Mail + In-App-Meldung an den Admin-Account
(„Mandant XY hat Unterlagen für 08/2026 eingereicht – 6 Dateien"). Zusätzlich:
automatische Erinnerung an den Mandanten bei fehlenden Unterlagen (konfigurierbarer Stichtag,
z. B. 10. des Folgemonats), Bestätigungsmail an den Mandanten.

**F7 – Admin-Bereich:** Übersicht aller Mandanten × Monate als Matrix mit Statusfarben,
Filter (offen / eingereicht / in Prüfung), Sammel-Download als ZIP, Notizfeld je Periode.

**F8 – Rücklauf:** fertiges Cockpit-PDF wird je Periode ins Portal gestellt, Mandant erhält
Benachrichtigung, Archiv aller bisherigen Reports mit Download.

## 4. Extraktions-Pipeline (statt „einfach OCR")

Reihenfolge zwingend – OCR ist Fallback, nicht Standardweg:

1. **Strukturierte Formate zuerst:** XLSX/CSV und DATEV-Exporte direkt parsen. Diese Route
   aktiv anbieten („Ihr Steuerberater kann das exportieren") – höchste Genauigkeit, null OCR-Risiko.
2. **PDF mit Textlayer:** Text- und Tabellenextraktion (z. B. `pdfplumber`/`pdftotext -layout`).
   Die meisten BWAs/SuSa aus DATEV sind digital erzeugt und brauchen kein OCR.
3. **OCR nur bei Scans/Fotos:** Erkennung über fehlenden Textlayer. Provider mit EU-Hosting und
   AV-Vertrag, tabellenfähig (Azure Document Intelligence / Google Document AI / AWS Textract).
   Tesseract nur als Notlösung – bei Tabellen unzuverlässig.
4. **Mapping:** Kontenrahmen (SKR03/SKR04) bzw. BWA-Zeilen → Valtix-Positionen. Mapping-Tabelle
   je Mandant persistieren und beim Folgemonat wiederverwenden; unbekannte Positionen landen in
   einer Klärliste.
5. **Review & Freigabe (Pflicht):** Extrahierte Werte werden **nie** automatisch produktiv.
   Prüf-Ansicht mit Wert, Herkunft (Datei + Seite), Konfidenz; auffällige Werte markiert
   (Vorzeichen, Bilanzsumme ≠ Aktiva/Passiva, Abweichung > x % zum Vormonat, fehlende Pflichtfelder).
   Freigabe durch Valtix per Klick, Korrekturen werden protokolliert.
6. **Übergabe:** Freigegebene Periode als JSON **und** als XLSX exportierbar, spaltengleich zum
   Blatt `Eingabe_Rohdaten` des Basismodells. Achtung: Zellinhalte, die mit `=` oder `+`
   beginnen, werden von Excel als Formel interpretiert – nie als Label schreiben.
7. **Verarbeitung asynchron** in einer Queue mit Retry und sichtbarem Job-Status, nicht im Request.

## 5. Datenmodell (Vorschlag, bitte prüfen)

`mandant` · `user` (Rollen: admin, mandant, optional gast/steuerberater lesend) ·
`periode` (mandant_id, jahr_monat, status, eingereicht_am) ·
`dokument` (periode_id, typ, dateiname, hash, version, storage_key, hochgeladen_von) ·
`extraktion` (dokument_id, engine, rohtext/tabellen, konfidenz, status) ·
`kennzahl_wert` (periode_id, feldschluessel, wert, quelle_dokument_id, freigegeben_von) ·
`mapping_regel` (mandant_id, quellbezeichnung, zielfeld) ·
`report` (periode_id, datei, veroeffentlicht_am) · `audit_log` (wer, was, wann, vorher/nachher).

## 6. UX-Vorgaben

- Zielgruppe: Geschäftsführer kleiner Unternehmen, keine Controlling-Kenntnisse. Keine
  Fachbegriffe ohne Erklärung (Fachbegriff kursiv + Klartext daneben).
- Maximal 3 Klicks von Login bis abgeschickter Upload. Ein primärer Call-to-Action je Seite.
- Klare Zustände: leer / lädt / Fehler / erfolgreich. Fehlermeldungen sagen, was zu tun ist.
- Vollständig mobil bedienbar; Upload per Handyfoto muss sauber funktionieren.
- Design-Standard verbindlich: **Navy #222A44 / Cream #F6EBCE, Amber-Akzente.** Kein Glas-/
  Blur-Look, keine neue Farbwelt, bestehende Komponenten wiederverwenden.
- Barrierefreiheit: Tastaturbedienung, Kontraste, Labels.

## 7. Sicherheit & Recht

- Storage privat, Zugriff nur über signierte, kurzlebige URLs; Row-Level-Security bzw.
  Mandantentrennung auf DB-Ebene, gegen Fremdzugriff testen (ein Mandant darf fremde
  Perioden weder lesen noch erraten können).
- Virenscan beim Upload, Dateityp-Whitelist, Größenlimit, keine Ausführung serverseitig.
- Hosting und alle Subprozessoren in der EU; Liste der Subprozessoren pflegen (relevant für AVV
  und Anlage 1 Datenschutzhinweise).
- Vollständiges Audit-Log (Upload, Einreichung, Freigabe, Korrektur, Download).
- Lösch- und Aufbewahrungskonzept je Mandant, Export aller eigenen Daten auf Anforderung.
- 2FA für den Admin-Account, sichere Session-Behandlung, Rate Limiting an Login und Upload.

## 8. Nicht-Ziele (bewusst außen vor)

Keine Buchführung, keine Steuerberatung, keine Bankanbindung, kein Rechnungsschreiben,
keine Änderung des bestehenden KPI-Sets, kein Umbau des Cockpit-Layouts.

## 9. Meilensteine

- **M1** Datenmodell, Periodenlogik, Upload, Checkliste, Einreichen, Admin-Benachrichtigung (ohne Extraktion)
- **M2** Admin-Übersicht (Matrix, Filter, ZIP-Download), Erinnerungen
- **M3** Extraktion: strukturierte Formate + PDF-Textlayer, Job-Queue
- **M4** OCR-Fallback, Mapping-Regeln, Review-/Freigabe-Ansicht, Export ins Basismodell-Schema
- **M5** Report-Rücklauf, Archiv, Feinschliff UX

## 10. Definition of Done je Meilenstein

Lauffähig lokal; Tests für Upload, Mandantentrennung, Statuswechsel und Parser (mit
anonymisierten Beispieldateien); Demo-Mandant mit Testdaten; kurze Notiz im Repo, was gebaut
wurde und was offen ist; keine Secrets im Code.

## 11. Bitte vorab klären

Stack/Hosting und DB · OCR-Provider (EU) · ob DATEV-Export als Hauptweg gesetzt wird ·
wer freigibt (nur Valtix oder Bestätigung durch Mandant) · Mandantenanzahl und erwartetes
Dateivolumen · bestehende Auth-Lösung.
