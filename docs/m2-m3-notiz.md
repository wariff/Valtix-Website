# M2 und M3 gebaut: Erinnerungen, Auslesen, Warteschlange

Stand 11.09.2026. Lokal lauffähig, 31 Tests grün, nicht ausgerollt.

## M2 fertig

Die Matrix, die Filter, der ZIP-Download und das Notizfeld kamen schon in M1.
Neu sind die Erinnerungen.

`portal/erinnerungen.py` findet Mandanten, bei denen für den Vormonat noch
Pflichtunterlagen fehlen, und schreibt ihnen. Stichtag ist standardmäßig der
10. des Folgemonats, global über die Einstellung `erinnerung_tag` und je
Mandant über `mandant.erinnerung_tag`. Erinnert wird höchstens einmal je
Mandant und Monat; nachgesehen wird im Protokoll, nicht in einem Merker, der
verlorengehen kann.

    python3 portal/erinnerungen.py --probe    zeigt, wer heute drankäme
    python3 portal/erinnerungen.py            versendet

Gedacht für einen täglichen Zeitplan auf dem Server.

## M3 fertig

**Warteschlange.** Beim Hochladen wird nur eine Aufgabe eingereiht, gelesen
wird außerhalb der Anfrage. Fällt etwas um, wird bis zu dreimal wiederholt,
danach steht der Fehler in der Aufgabe und in der Verwaltung. Eine große Datei
blockiert damit nie eine Anfrage.

    python3 portal/arbeiter.py            einmal abarbeiten
    python3 portal/arbeiter.py --dauer    laufen lassen

**Leser.** Die Reihenfolge aus der Spezifikation, strukturierte Formate zuerst:

| Format | Weg | Ergebnis |
|---|---|---|
| XLSX, XLS | `openpyxl` | Blätter mit Zeilen |
| CSV | Trennzeichen und Kodierung werden erkannt | Zeilen |
| DATEV-Export | Kennung `EXTF` in der ersten Zeile | Kopfdaten und Buchungen |
| PDF mit Textebene | `pdfplumber` | Text und erkannte Tabellen |
| PDF ohne Textebene | erkannt, nicht geraten | Vermerk „braucht OCR" |
| JPG, PNG | erkannt | Vermerk „braucht OCR" |
| ZIP | abgelehnt | Bitte einzeln hochladen |

Ob ein PDF eine Textebene hat, wird an der Textmenge je Seite gemessen. Unter
60 Zeichen je Seite gilt es als Scan. Geraten wird nichts: ohne Textebene gibt
es keinen Wert, sondern einen Vermerk.

**Deutsche Zahlen.** `leser._zahl` liest `1.234,56`, `-1.234,56`, `(89,10)`,
`12,5 €` und `1.234.567`. Ein Punkt ohne Komma ist nur dann Tausendertrenner,
wenn danach genau drei Ziffern stehen. Sonst wäre aus `1234.56` die Zahl
`123456` geworden, bei Beträgen ein Faktor hundert. Das ist getestet.

**Nichts wird produktiv.** Das Ergebnis landet als Rohmaterial in der Tabelle
`extraktion` mit Weg, Seitenzahl, Konfidenz und Hinweis. Die Verwaltung sieht
je Periode, was gelesen wurde und was OCR braucht. Das Zuordnen auf die
Valtix-Positionen und die Freigabe sind M4.

## Beispieldateien

`portal/tests/beispiele/erzeugen.py` baut fünf anonymisierte Dateien: eine
BWA als Excel, eine Summen- und Saldenliste als CSV in Windows-1252, einen
DATEV-Buchungsstapel, ein PDF mit Textebene und einen Scan ohne. Keine echten
Mandantendaten. Das PDF wird von Hand gebaut, damit die Tests keine weitere
Bibliothek brauchen.

## Prüfen

    python3 -m pytest portal/tests -q      31 Tests

M1: Upload, Ablehnung falscher Typen, Doppelte, Versionierung, „entfällt",
Mandantentrennung auf drei Ebenen, Pfadausbruch, Einreichen, Sperre, Nachtrag,
Protokollierung, ZIP, HTTP-Zugriff.
M2 und M3: deutsche Zahlen, fünf Leser, Erkennung fehlender Textebene,
Warteschlange mit Wiederholung, doppeltes Einreihen, Erinnerung ab Stichtag,
keine zweite Erinnerung, eigener Stichtag je Mandant.

## Lokal starten

    export VALTIX_DB=demo.sqlite3 VALTIX_ABLAGE=demo-ablage VALTIX_HTTPS=0
    export VALTIX_SECRET=$(python3 -c "import secrets;print(secrets.token_urlsafe(48))")
    pip install -r portal/requirements.txt
    python3 portal/demo_daten.py       # Demo-Mandant, zwei Monate, Einladungslinks
    python3 portal/arbeiter.py         # liest die Dateien aus
    cd portal && uvicorn app:app --port 8000

## Offen

**M4** Mapping SKR03/SKR04 und BWA-Zeilen auf die Valtix-Positionen,
Klärliste, Prüfansicht mit Herkunft und Konfidenz, Freigabe, Export ins
Schema der Eingabevorlage. OCR braucht einen Anbieter und einen AVV.

**M5** Rücklauf des Berichts, Archiv, Drag und Drop, Fortschrittsanzeige,
Angleichen der Portalseiten an das Aussehen der Website.

**M0** Hosting, Datenbank, Objektspeicher, Mailversand, TLS, 2FA, Virenscan.
Ohne diesen Schritt geht nichts online.
