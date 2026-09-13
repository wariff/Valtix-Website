# M4: Vom Gelesenen zum geprüften Wert

Stand: September 2026. Was hier steht, ist gebaut und getestet, nicht geplant.

## Der Weg

    Datei  ->  leser.py  ->  extraktion  ->  mapping.py  ->  Vorschlag
                                                 |
                                          Prüfansicht, Klärliste
                                                 |
                                             Freigabe  ->  Export

Kein Wert wird automatisch gültig. Aus einer gelesenen Datei entsteht ein
Vorschlag mit Herkunft und Konfidenz. Erst die Freigabe macht ihn zum Wert,
jede Korrektur steht im Protokoll und gilt ab dem Folgemonat von allein.

## Die Kontenbereiche sind geraten

`portal/mapping.py` ordnet Konten über Nummernbereiche zu, getrennt nach
SKR03 und SKR04. Diese Bereiche sind eine fachliche Schätzung und an echten
Mandantendaten noch nicht geprüft. Der Modulkopf sagt das ausdrücklich, die
Prüfansicht im Portal ebenfalls. Wer mit echten Daten arbeitet, prüft zuerst
die Zuordnung und korrigiert sie in der Klärliste, damit die gelernte Regel
ab dem nächsten Monat greift.

## Zwei Dinge, die schiefgingen und behoben sind

**Doppelte Beträge.** BWA und Summen- und Saldenliste enthalten dieselben
Zahlen. Wurden alle Dateien zusammen addiert, war jedes Feld doppelt.
Jetzt wird innerhalb einer Datei summiert und über Dateien hinweg die
zuverlässigste genommen; weicht eine andere um mehr als ein Prozent ab,
steht das als Warnung in der Prüfansicht.

**Buchungsstapel.** Ein DATEV-Buchungsstapel listet einzelne Buchungen in
einer anderen Spaltenfolge. Die allgemeine Spaltenerkennung hielt Beträge
für Kontonummern und erzeugte unbrauchbare Klärfälle. Buchungsstapel bleiben
deshalb liegen, mit einem Hinweis, welche Datei stattdessen gebraucht wird.

## Auf der Website zu sehen

`portal-vorschau.html` zeigt drei Ansichten, die diese Kette wirklich
durchlaufen haben. `tools/build_portal_vorschau.py` legt beim Bauen eine
Wegwerfdatenbank an, lädt die anonymisierten Beispieldateien aus
`portal/tests/beispiele/` hoch, lässt den Arbeiter lesen und schreibt das
Ergebnis in die Seite:

- **Unterlagen** die Checkliste des Monats und was aus jeder Datei wurde
- **Monatsübersicht** alle Mandanten gegen alle Monate (über die Adresse
  `#ansicht-monatsuebersicht`)
- **Werte prüfen** Vorschläge mit Herkunft und Konfidenz, Klärliste,
  Hinweise (über die Adresse `#ansicht-pruefen`)

Die Vorführung hat keinen Server. Was dort steht, wurde beim Bauen
ausgerechnet und liegt als fertiges HTML auf der Seite.

## Offen

**M5** Rücklauf des Berichts, Archiv, Drag und Drop, Fortschrittsanzeige,
Angleichen der Portalseiten an das Aussehen der Website.

**M0** Hosting, Datenbank, Objektspeicher, Mailversand, TLS, 2FA, Virenscan,
Anbieter für die Texterkennung samt Auftragsverarbeitungsvertrag. Ohne
diesen Schritt geht nichts online.

## Nachtrag: Anmerkungen zu einzelnen Dateien

Zu jeder hochgeladenen Datei gibt es einen Verlauf, in den beide Seiten
schreiben. Der Mandant erklärt damit seinen Upload („der Auszug ist ein
Scan"), wir fragen damit nach. Beide sehen denselben Verlauf an derselben
Datei, und wer schreibt, löst bei der anderen Seite eine Meldung im Portal
und eine Mail aus.

`portal/kommentare.py` prüft dabei dreierlei: die Datei muss zum Zugang
gehören, der Text darf nicht leer und nicht länger als 2000 Zeichen sein.
Ein fremder Mandant bekommt weder den Verlauf zu sehen noch kann er
hineinschreiben. Jede Anmerkung steht im Protokoll.

Der Verlauf hängt an der Datei, nicht am Slot. Lädt jemand eine neue Fassung
hoch, bleibt die Anmerkung an der alten Fassung stehen, wo sie hingehört.

Neu ist außerdem die Meldung beim Hochladen. Bisher erfuhren wir erst beim
Einreichen von neuen Dateien. Jetzt kommt eine Meldung je Vorgang, nicht je
Datei: wer fünf Dateien auf einmal hochlädt, löst eine Meldung aus.

Das Rückziel des Formulars kommt aus einem Formularfeld und wird deshalb
gegen ein Muster geprüft. Nur `/unterlagen/JJJJ-MM` und `/uebersicht/<Zahl>`
sind erlaubt, alles andere landet auf der Startseite der jeweiligen Rolle.
