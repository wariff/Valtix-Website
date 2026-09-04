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

## Bereits veröffentlichte Themen

Vor dem Vorschlag `tools/build_ratgeber.py` öffnen und die Liste `ARTIKEL` lesen.
Stand September 2026 elf Beiträge zu: Zahlungsschwierigkeiten im Handwerk,
Forderungslaufzeit in Agenturen, Ertrag in der Gastronomie, BWA lesen,
13-Wochen-Liquiditätsplanung, Kundenerlebnis im Einzelhandel, Stundensatzkalkulation,
Preiserhöhung durchsetzen, ausgeschöpfter Kontokorrent, Import und Export außerhalb
der EU, Rentabilität in Social-Media-Agenturen.

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

Es gibt keine Anbindung. Beiträge werden als Text geliefert, der Nutzer kopiert sie.
Format: Aufhänger in der ersten Zeile, dann eine konkrete Rechnung, am Ende eine
Frage oder der Verweis auf den Ratgeberbeitrag. Keine Hashtag-Wolken, drei bis vier
reichen. Länge 900 bis 1.300 Zeichen.

## Offene Punkte (regelmäßig prüfen)

- Postfach info@valtixfm.de bei IONOS anlegen
- www.valtixfm.de muss ein CNAME auf wariff.github.io sein, nicht A-Records
- Brevo-Formularadresse fehlt, deshalb ist der Newsletter-Baustein deaktiviert
  (`BREVO_FORM_URL` in `tools/build_ratgeber.py`)
- Registergericht, Registernummer und USt-IdNr. im Impressum offen
- graue Hinweiskästen im Impressum vor dem endgültigen Livegang entfernen
