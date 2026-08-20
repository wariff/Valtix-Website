# Platzhalter in den Rechtsseiten

Alle firmenspezifischen Angaben in `impressum.html` und `datenschutz.html` sind als
`{{PLATZHALTER}}` gesetzt und müssen vor dem Livegang durch echte Werte ersetzt werden.
Es wurden bewusst keine Beispiel- oder Fantasiewerte eingetragen.

## Bereits eingesetzt

| Angabe | Wert |
|---|---|
| Firma und Rechtsform | Valtix Financial Management GbR |
| Vertretungsberechtigte Gesellschafter | Luca Sparhuber, Sharif Ibrahim |
| Verantwortlich für Inhalte nach § 18 Abs. 2 MStV | Sharif Ibrahim |

## Offene Platzhalter

| Platzhalter | Bedeutung | Beispielformat | Vorkommen (Datei:Zeile) | Pflicht/Optional |
|---|---|---|---|---|
| `{{STRASSE_HAUSNUMMER}}` | Ladungsfähige Anschrift, Straße und Hausnummer (kein Postfach) | Musterstraße 1 | impressum.html:80, impressum.html:106, datenschutz.html:82 | Pflicht |
| `{{PLZ}}` | Postleitzahl | 04109 | impressum.html:81, impressum.html:107, datenschutz.html:83 | Pflicht |
| `{{ORT}}` | Ort | Leipzig | impressum.html:81, impressum.html:107, datenschutz.html:83 | Pflicht |
| `{{TELEFONNUMMER}}` | Telefonnummer | +49 341 0000000 | impressum.html:88, datenschutz.html:84 | Pflicht |
| `{{EMAIL_ADRESSE}}` | E-Mail-Adresse (sollte mit der Kontakt-Mail auf der Startseite übereinstimmen) | hallo@valtix.de | impressum.html:89, datenschutz.html:85 | Pflicht |
| `{{REGISTERGERICHT}}` | Registergericht | Amtsgericht Leipzig | impressum.html:94 | Optional, nur bei eingetragener GbR (eGbR) |
| `{{REGISTERNUMMER}}` | Registernummer | GsR 1234 | impressum.html:95 | Optional, nur bei eingetragener GbR (eGbR) |
| `{{UST_IDNR}}` | Umsatzsteuer-Identifikationsnummer nach § 27a UStG | DE123456789 | impressum.html:100 | Optional, nur falls vergeben |
| `{{BERUFSBEZEICHNUNG}}` | Berufsbezeichnung, falls reguliert | z. B. Finanzanlagenvermittler | impressum.html:111 | Optional, nur bei erlaubnispflichtiger Tätigkeit |
| `{{ERLAUBNISNORM}}` | Norm der Erlaubnis | z. B. § 34c GewO oder § 34f GewO | impressum.html:112 | Optional, nur bei erlaubnispflichtiger Tätigkeit |
| `{{AUFSICHTSBEHOERDE_NAME}}` | Zuständige Aufsichtsbehörde/Kammer | z. B. IHK zu Leipzig | impressum.html:115 | Optional, nur bei erlaubnispflichtiger Tätigkeit |
| `{{AUFSICHTSBEHOERDE_ANSCHRIFT}}` | Anschrift der Aufsichtsbehörde | Straße, PLZ Ort | impressum.html:116 | Optional, nur bei erlaubnispflichtiger Tätigkeit |
| `{{BERUFSRECHTLICHE_REGELUNGEN}}` | Einschlägige berufsrechtliche Regelungen mit Fundstelle | z. B. GewO, FinVermV, abrufbar unter gesetze-im-internet.de | impressum.html:118 | Optional, nur bei erlaubnispflichtiger Tätigkeit |
| `{{BERUFSHAFTPFLICHT_VERSICHERER}}` | Name des Berufshaftpflichtversicherers | Versicherung AG | impressum.html:121 | Optional, nur falls vorhanden/vorgeschrieben |
| `{{BERUFSHAFTPFLICHT_ANSCHRIFT}}` | Anschrift des Versicherers | Straße, PLZ Ort | impressum.html:122 | Optional, nur falls vorhanden/vorgeschrieben |
| `{{BERUFSHAFTPFLICHT_GELTUNGSRAUM}}` | Räumlicher Geltungsbereich der Versicherung | Deutschland / EU | impressum.html:123 | Optional, nur falls vorhanden/vorgeschrieben |
| `{{DATENSCHUTZ_AUFSICHTSBEHOERDE_NAME}}` | Zuständige Landesdatenschutzbehörde (richtet sich nach dem Sitz) | Bei Sitz in Sachsen: Sächsische Datenschutz- und Transparenzbeauftragte | datenschutz.html:138 | Pflicht |
| `{{DATENSCHUTZ_AUFSICHTSBEHOERDE_ANSCHRIFT}}` | Anschrift der Datenschutzbehörde | Straße, PLZ Ort | datenschutz.html:139 | Pflicht |
| `{{STAND_DATUM}}` | Datum des Rechtsstands der Seite | 20.08.2026 | impressum.html:131, datenschutz.html:145 | Pflicht |

## Zusätzlich zu prüfen (keine Platzhalter, aber Entscheidungen/Fakten)

- **Anschrift:** Die ladungsfähige Anschrift ist nach § 5 DDG zwingend. Ohne sie darf die
  Seite nicht öffentlich betrieben werden.
- **GbR und Registereintrag:** Eine klassische GbR hat keinen Registereintrag; der Abschnitt
  "Registereintrag" entfällt dann ersatzlos. Seit dem MoPeG (2024) kann eine GbR freiwillig
  als eingetragene GbR (eGbR) im Gesellschaftsregister eingetragen sein. In diesem Fall
  müssen Registergericht und Registernummer angegeben werden.
- **Verbraucherstreitbeilegung (impressum.html):** Eingetragen ist die übliche Erklärung,
  *nicht* an Schlichtungsverfahren nach § 36 VSBG teilzunehmen. Falls doch eine Teilnahme
  gewollt oder verpflichtend ist, muss der Text angepasst werden.
- **Datenschutzbeauftragter (datenschutz.html, Abschnitt 1):** Eingetragen ist, dass kein
  Datenschutzbeauftragter bestellt ist. Prüfen, ob das zutrifft.
- **Berufsrechtlicher Abschnitt (impressum.html):** Komplett löschen, falls die Tätigkeit
  keiner Erlaubnispflicht/Kammeraufsicht unterliegt.
- **Hinweiskästen:** Die grauen Kästen (`class="note"`) im Impressum sind Arbeitshilfen und
  sollten vor dem Livegang entfernt werden.
- **GitHub Pages / Data Privacy Framework (datenschutz.html, Abschnitt 2):** Die Zertifizierung
  von GitHub unter dem EU-US Data Privacy Framework vor Livegang im DPF-Register gegenprüfen.

## Hinweis

Die Texte sind sorgfältig erstellte Vorlagen, ersetzen aber keine Rechtsberatung.
Vor dem Livegang von einer Anwältin oder einem Anwalt prüfen lassen.
