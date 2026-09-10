# M1 gebaut: Perioden, Unterlagen, Einreichen

Stand 10.09.2026. Lokal lauffähig, getestet, noch nicht ausgerollt.

## Entscheidungen, die ich getroffen habe

Sie haben mir die offenen Punkte überlassen. So habe ich entschieden, jeweils
mit dem Grund.

**W1 Design.** Der bestehende Look bleibt, mit Glasflächen und den Farbwerten
der Website (`#232941`, `#F5EBD0`, Gold `#A6813F`). §6 der Spezifikation
verlangt das Gegenteil, aber Sie haben den Look vor zwei Tagen ausdrücklich
angefordert, er ist live und §6 sagt im selben Absatz „bestehende Komponenten
wiederverwenden". Zwei Farbwelten nebeneinander wären schlimmer als eine
Abweichung von der Vorgabe. Die Portalseiten von M1 nutzen weiterhin das
schlichtere Stylesheet aus `portal/app.py`; das Angleichen an die Website
gehört in M5.

**W2 Eingabeblatt.** Maßgeblich ist die Vorlage im Repo
(`tools/bericht/VALTIX_Eingabevorlage.xlsx`), sechs Blätter, Positionen in
Zeilen, Monate in Spalten. Der Berichtsgenerator ist gegen sie geprüft, 20 von
20 Werten stimmen mit Ihrem Word-Bericht überein. Das Blatt `Eingabe_Rohdaten`
aus §0 gibt es hier nicht. Der Export in M4 zielt auf die Vorlage im Repo.

**W3 Cockpit.** Der Generator bleibt, wie er ist. §8 verbietet den Umbau des
Cockpit-Layouts, deshalb stellt das Portal den fertigen Bericht nur ein und
gibt ihn zurück. Halbjahresreview, Maßnahmen und Glossar baue ich nicht dazu.

**W4 Umfang.** Kein Redesign der Ansicht, aber ein neuer Unterbau, weil es
keinen gab.

**Stack.** FastAPI, weil der Prototyp und der gesamte Berichtsgenerator Python
sind. Datenbank vorerst SQLite, alle Abfragen in reinem SQL ohne
SQLite-Eigenheiten, damit der Wechsel auf PostgreSQL in M0 eine Frage des
Treibers ist. Die Dateiablage spricht nur über drei Funktionen mit dem Rest
(`portal/speicher.py`); für einen Objektspeicher wird diese eine Datei ersetzt.

## Was gebaut ist

| Datei | Aufgabe |
|---|---|
| `portal/datenbank.py` | Schema erweitert: `periode`, `checkliste_slot`, `dokument`, `slot_entfaellt`, `meldung`; Protokoll um vorher/nachher |
| `portal/speicher.py` | Dateiablage, Typprüfung, Größenlimit, Prüfsumme, Schutz gegen Pfadausbruch |
| `portal/perioden.py` | Perioden, Checkliste, Dokumente mit Versionierung, „entfällt", Einreichen, Nachtrag, Matrix, ZIP |
| `portal/benachrichtigung.py` | Meldungen im Portal und per E-Mail, ohne eingerichteten Server nur Protokoll |
| `portal/app.py` | Seiten für Mandant und Verwaltung |
| `portal/tests/test_m1.py` | 14 Tests |
| `portal/demo_daten.py` | Demo-Mandant mit zwei Monaten |

**Erfüllte Anforderungen:** F1 Statusblock, F2 Periodenlogik mit rückwirkenden
Monaten und Ampel je Monat, F3 Upload mit Mehrfachauswahl, Typprüfung,
Größenlimit, Prüfsumme gegen Doppelte und Versionierung, F4 Checkliste je
Mandant mit „entfällt" plus Begründung, F5 Einreichen als eigener Schritt mit
Sperre und Nachtrag, F6 Eingangsmeldung an Valtix und Bestätigung an den
Mandanten, F7 in Teilen (Matrix, Filter, ZIP, Notiz).

## Was bewusst fehlt

- **Virenscan.** Braucht einen Dienst, den es ohne M0 nicht gibt. Bis dahin
  gilt: Whitelist der Dateitypen, Größenlimit, nichts wird serverseitig
  ausgeführt, Dateien liegen außerhalb des Web-Verzeichnisses.
- **Signierte kurzlebige URLs.** Heute läuft jeder Zugriff durch die Anwendung,
  die vorher die Rechte prüft. Mit dem Objektspeicher in M0 kommen signierte
  URLs dazu.
- **Mandantentrennung auf Datenbankebene.** Sie wird heute in `perioden.py`
  durchgesetzt und ist getestet. Row-Level-Security braucht PostgreSQL.
- **Drag & Drop und Fortschrittsanzeige.** Das Formular nimmt Mehrfachauswahl
  und die Handykamera an. Die Oberfläche dafür gehört in M5.
- **Erinnerungen zum Stichtag** (M2), Extraktion (M3, M4), Rücklauf (M5).
- **2FA für den Administrator.** Gehört zu M0, sobald klar ist, wie angemeldet
  wird.

## Prüfen

```
python3 -m pytest portal/tests -q
```

14 Tests: Upload, Ablehnung falscher Typen, Doppelte, Versionierung, „entfällt",
Mandantentrennung auf drei Ebenen, Pfadausbruch, Einreichen, Sperre, Nachtrag,
Protokollierung der Statuswechsel, ZIP.

## Lokal starten

```
export VALTIX_DB=demo.sqlite3
export VALTIX_ABLAGE=demo-ablage
export VALTIX_SECRET=$(python3 -c "import secrets;print(secrets.token_urlsafe(48))")
export VALTIX_HTTPS=0
python3 portal/demo_daten.py            # Demo-Mandant, gibt zwei Einladungslinks aus
cd portal && uvicorn app:app --port 8000
```

Keine Zugangsdaten im Code. Ohne `VALTIX_SMTP_HOST` wird keine Mail versendet,
der Versand steht dann nur im Protokoll.

## Nächster Schritt

M0, und der braucht Ihre Entscheidungen: Anbieter für Hosting und Datenbank,
Subdomain, Mailversand, OCR-Anbieter für später, AVV. Ohne die kann M1 nicht
online gehen.
