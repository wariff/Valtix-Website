# Briefing: wöchentliche Inhalte für Valtix

Diese Datei ist die Arbeitsgrundlage für den wöchentlichen Termin. Sie wird nicht
mit veröffentlicht (siehe `exclude_assets` im Deploy-Workflow).

## Das Unternehmen

Valtix Financial Management, Leipzig. Rechtlich "Luca Sparhuber und Sharif Ibrahim GbR",
im Marketing "Valtix Financial Management". Betriebswirtschaftliche Beratung für
inhabergeführte Betriebe zwischen etwa fünf und fünfzig Mitarbeitern: Kennzahlen,
Liquidität, Ertrag. Einsatzgebiete Leipzig, Ulm, Mannheim. Sitz ist Leipzig, in Ulm
und Mannheim wird beim Mandanten vor Ort gearbeitet, es gibt dort **keine Büros**.

Angebot: Financial Health Check als Einstieg, danach monatliche Betreuung (Hauptprodukt)
oder Intensivbetreuung mit zwei Terminen im Monat.

**Grenze der Tätigkeit:** erlaubnisfreies Gewerbe. Keine Rechts-, Steuer- oder
Anlageberatung. Das gehört bei rechtsnahen Themen in jeden Beitrag.

## Tonfall, verbindlich

- **Keine Gedankenstriche im Fließtext.** Punkt, Komma oder Doppelpunkt.
- Keine Werbefloskeln, keine Superlative, keine Ausrufezeichen.
- Konkrete Zahlen statt Adjektiven. Nicht "deutliche Ersparnis", sondern "rund 25.000 Euro".
- Rechenbeispiele durchrechnen und die Zahlen mit Python gegenprüfen, bevor sie
  in den Text kommen. Die bisherigen Beiträge sind alle nachgerechnet.
- Kurze Sätze, aktiv, Siezen.
- Fachbegriffe beim ersten Auftreten in einem Halbsatz erklären.
- Keine erfundenen Referenzen, Mandanten, Zahlen oder Zertifikate.

## Rechtliche Leitplanke für Beiträge

Valtix betreibt ein erlaubnisfreies Gewerbe und erbringt weder Rechtsdienstleistungen
nach dem RDG noch Hilfeleistung in Steuersachen nach dem StBerG. Das steht so im
Impressum und muss in den Beiträgen durchgehalten werden.

**Erlaubt** ist allgemeine, betriebswirtschaftliche Information: Kennzahlen erklären,
Zusammenhänge darstellen, Rechenwege zeigen, Größenordnungen benennen. Gesetzesnormen
dürfen als Kontext genannt werden, wenn sie unstrittig und korrekt zitiert sind
(z. B. § 252 Abs. 1 Nr. 2 HGB zur Fortführungsannahme).

**Nicht erlaubt** ist alles, was wie eine rechtliche Subsumtion im Einzelfall wirkt:
ob Zahlungsunfähigkeit oder Überschuldung vorliegt, welche Antragsfristen gelten, wie
eine insolvenzrechtliche Fortbestehensprognose zu erstellen ist, steuerliche Gestaltung,
Vertragsauslegung. Solche Themen dürfen erwähnt, aber nicht angeleitet werden.

**Pflicht bei jedem rechtsnahen Beitrag:** ein eigener Schlussabschnitt, der die Grenze
benennt und an Fachanwältin, Steuerberater oder Abschlussprüfer verweist. Vorbild ist
der Abschnitt "Wo unsere Arbeit endet" im Beitrag zu den Frühwarnsignalen.

**Quellenangaben:** Normen und Prüfungsstandards nur nennen, wenn die Fundstelle
gesichert ist. Keine Paragrafen, Randziffern oder Anlagennummern aus dem Gedächtnis
zitieren. Im Zweifel den Standard beim Namen nennen und auf die genaue Fundstelle
verzichten. Eine falsche Fundstelle richtet mehr Schaden an als gar keine.

**Zahlen:** keine Branchenstatistiken erfinden. Übliche Erfahrungsbandbreiten sind
zulässig, müssen aber als solche gekennzeichnet sein. Eigene Rechenbeispiele immer
mit Python nachrechnen.

## Bereits veröffentlichte Themen

Vor dem Vorschlag `tools/build_ratgeber.py` öffnen und die Liste `ARTIKEL` lesen.
Stand September 2026 dreizehn Beiträge zu: Zahlungsschwierigkeiten im Handwerk,
Forderungslaufzeit in Agenturen, Ertrag in der Gastronomie, BWA lesen,
13-Wochen-Liquiditätsplanung, Kundenerlebnis im Einzelhandel, Stundensatzkalkulation,
Preiserhöhung durchsetzen, ausgeschöpfter Kontokorrent, Import und Export außerhalb
der EU, Rentabilität in Social-Media-Agenturen, Benchmarking von Kennzahlen, Frühwarnsignale einer Unternehmenskrise.

## Ablauf des wöchentlichen Termins

1. **Vorschlagen, nicht veröffentlichen.** Drei Themenvorschläge für den Ratgeber,
   jeweils mit Titel, Zielgruppe, Suchbegriff, Kernaussage und der Rechnung oder
   Kennzahl, die den Beitrag trägt. Dazu zwei bis drei LinkedIn-Beiträge, fertig
   zum Kopieren.
2. **Auf Freigabe warten.** Der Nutzer wählt aus. Ohne Freigabe wird nichts gebaut
   und nichts gepusht.
3. **Nach Freigabe:** Beitrag schreiben, in `ARTIKEL` in `tools/build_ratgeber.py`
   eintragen mit den Feldern slug, datum (heutiges Datum), branche, titel,
   seo_titel (nur falls titel plus " | Valtix" über 60 Zeichen kommt),
   beschreibung (140 bis 160 Zeichen), anriss, lesezeit, inhalt.
4. **Bauen und prüfen** (siehe unten), dann committen und pushen.
5. **Zusammenfassung liefern:** Thema, Inhalt, Länge, wo verlinkt.

## Bauen und prüfen

```
python3 tools/build_ratgeber.py     # Artikel, Übersicht, feed.xml
python3 tools/build_leistungen.py   # Leistungsseiten, vollständige sitemap.xml
python3 tools/build_portal_vorschau.py     # Attrappe portal-vorschau.html
                                    # braucht die Beispieldatei, Pfad in VALTIX_DEMO
python3 tools/seo_audit.py          # Titel, Description, H1, Schema, Bilder
npm i playwright && node tools/check.mjs   # Überlauf, Konsole, tote Links
```

`build_leistungen.py` muss **nach** `build_ratgeber.py` laufen, sonst enthält die
Sitemap nur die Ratgeberseiten. Erwartet werden derzeit 19 Adressen.

Ergebnis von `check.mjs` muss "ALLES OK" sein. Der SEO-Audit meldet bei einigen
Beiträgen "unter der Zielmarke 900 Wörter". Das ist bekannt und akzeptiert,
Texte werden nicht zum Erreichen einer Wortzahl aufgebläht.

## Veröffentlichen

Branch `main`, der Workflow spiegelt nach `gh-pages`. Zusätzlich auf
`claude/ui-ux-pro-max-skill-2spmd3` pushen.

## LinkedIn

Unternehmensseite: https://www.linkedin.com/company/valtix-financial-management
Sie ist in der Fusszeile aller Seiten verlinkt und als sameAs in den
strukturierten Daten der Startseite hinterlegt.

Es gibt keine Anbindung. Beiträge werden als Text geliefert, der Nutzer kopiert sie.
Format: Aufhänger in der ersten Zeile, dann eine konkrete Rechnung, am Ende eine
Frage oder der Verweis auf den Ratgeberbeitrag. Keine Hashtag-Wolken, drei bis vier
reichen. Länge 900 bis 1.300 Zeichen.

## Themenpipeline

Vorgeprüfte Ideen für kommende Beiträge, in absteigender Priorität. Vor der Ausarbeitung
gegen die ARTIKEL-Liste prüfen, ob sich inzwischen etwas überschneidet.

1. **Working Capital: fünf Stellschrauben für mehr Liquidität ohne neues Kapital.**
   Vorräte, Debitoren, Kreditoren, Anzahlungen, Durchlaufzeit. Trägt eine durchgerechnete
   Gesamtwirkung: was die fünf Hebel zusammen an gebundenem Kapital freisetzen.
   Anschluss an den Beitrag zur 13-Wochen-Planung und an die Leistungsseite Liquiditätsberatung.

2. **Break-even: wie viele Aufträge Sie wirklich brauchen.** Fixkosten, Deckungsbeitrag
   je Auftrag, Break-even-Menge, Sicherheitsstrecke. Zielgruppe Handwerk und
   Dienstleistung. Baut auf dem Stundensatz-Beitrag auf, ohne ihn zu wiederholen.

3. **Anlagendeckung und Fristenkongruenz.** Warum langfristiges Vermögen langfristig
   finanziert gehört und woran man erkennt, dass es das nicht ist. Ergänzt den Beitrag
   zu den Frühwarnsignalen um die Bilanzseite. Vorsicht: Überschneidung prüfen.

4. **Kennzahlen-Dashboard statt BI-Werkzeug.** Warum eine Seite mit acht Zahlen mehr
   bewirkt als ein Auswertungssystem, das niemand öffnet. Auswahl der Kennzahlen,
   Schwellenwerte, Rhythmus. Führt inhaltlich direkt zum Betreuungspaket.

5. **Kalkulation im Einzelhandel: Handelsspanne, Aufschlag, Abschriften.** Der Unterschied
   zwischen Aufschlag und Spanne wird regelmäßig verwechselt und kostet Marge.

6. **Wenn die Bank das Rating verschlechtert.** Was in ein Rating einfließt, was der
   Betrieb selbst beeinflussen kann, wie ein Bankgespräch vorbereitet wird. Rechtsnah
   nur am Rand, Schwerpunkt bleibt betriebswirtschaftlich.

Zum verworfenen Vorschlag "Eigenkapitalquote gegen Liquidität": inhaltlich aufgegangen
im Beitrag zu den Frühwarnsignalen, nicht erneut ansetzen.

## Berichtsgenerator

`tools/bericht/` erzeugt aus der ausgefüllten Eingabevorlage den Monatsbericht
als HTML. Aufruf und Aufbau stehen in `tools/bericht/README.md`. Vor jeder
Änderung am Modell `python3 tools/bericht/test_abgleich.py` laufen lassen, der
prüft 20 Größen gegen den bestehenden Word-Bericht.

## Portalvorschau

`portal-vorschau.html` ist eine reine Attrappe zur Ansicht, erzeugt von
`tools/build_portal_vorschau.py`. Kein Server, keine Datenbank, keine
Speicherung. Firma und Zahlen stammen aus der Beispieldatei.

Der Aufbau folgt dem, was Auswertungswerkzeuge wie finban vormachen:
Seitenleiste links, Werkzeugleiste oben, darunter Kennzahlenkacheln, ein
Verlauf über alle Monate und ein aufklappbares Raster mit den Monaten als
Spalten. Die Farben sind die von Valtix, nicht die des Vorbilds. Grün, Gelb
und Rot bleiben der Zielerreichung vorbehalten, Erträge stehen in Navy und
Kosten in Gold.

`tools/bericht/matrix.py` liest die Eingabevorlage als Monatsraster: jede
Position über alle befüllten Monate, dazu die Zielwerte aus Blatt 5. Wie im
Berichtsgenerator werden nur Eingabefelder gelesen, alle Summen hier gerechnet.
Beschriftungen kommen aus der Datei, damit umbenannte Zeilen im Portal so
heißen, wie der Mandant sie nennt. Prüfen mit
`python3 tools/bericht/matrix.py <datei.xlsx>`.

Wichtig zum Stand: die Vorschau zeigt den Entwurf. Das laufende Portal unter
`portal/` hat noch die einfache Listenansicht. Wer die Vorschau als Zusage
liest, irrt.

Beide Vorschauseiten stehen auf `noindex, nofollow`, sind in `robots.txt`
gesperrt und gehören nicht in die Sitemap. Der Punkt "Mandantenlogin" in Kopf-
und Fußzeile zeigt darauf. Sobald ein echtes Portal läuft, muss dieser Link auf
die richtige Adresse zeigen.

## Offene Punkte (regelmäßig prüfen)

- Postfach info@valtixfm.de bei IONOS anlegen
- Entscheidung offen, ob das Mandantenportal auf einem eigenen Server laufen
  soll; bis dahin bleibt "Mandantenlogin" ein Link auf die Attrappe
- www.valtixfm.de muss ein CNAME auf wariff.github.io sein, nicht A-Records
- Brevo-Formularadresse fehlt, deshalb ist der Newsletter-Baustein deaktiviert
  (`BREVO_FORM_URL` in `tools/build_ratgeber.py`)
- Registergericht, Registernummer und USt-IdNr. im Impressum offen
- graue Hinweiskästen im Impressum vor dem endgültigen Livegang entfernen
