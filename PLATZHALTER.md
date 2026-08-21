# Platzhalter in den Rechtsseiten

Firmenspezifische Angaben in `impressum.html` und `datenschutz.html`, die noch fehlen, sind als
`{{PLATZHALTER}}` gesetzt. Es wurden bewusst keine Beispiel- oder Fantasiewerte eingetragen.

## Bereits eingesetzt

| Angabe | Wert |
|---|---|
| Rechtliche Bezeichnung | Luca Sparhuber und Sharif Ibrahim GbR |
| Geschäftsbezeichnung (Marke) | Valtix Financial Management |
| Gesellschafter, gemeinschaftlich vertretungsberechtigt | Luca Sparhuber, Sharif Ibrahim |
| Verantwortlich für Inhalte nach § 18 Abs. 2 MStV | Sharif Ibrahim |
| Anschrift | Straße des 18. Oktober 11, 04103 Leipzig |
| Telefon | +49 176 22930394 |
| E-Mail | info@valtixfm.de (auch auf der Startseite eingesetzt) |
| Zuständige Datenschutz-Aufsichtsbehörde | Sächsische Datenschutz- und Transparenzbeauftragte, Maternistraße 17, 01067 Dresden |
| Berufsrechtliche Angaben | Entfallen: erlaubnisfreies Gewerbe. Ersetzt durch den Abschnitt "Tätigkeit und Umfang der Beratung" |
| Stand-Datum | 20.08.2026 |
| Formularversand | Web3Forms, Zustellung an sharifibr@icloud.com |

## Offene Platzhalter

Alle Pflichtangaben sind eingesetzt. Offen sind nur noch optionale Felder aus Block 3
(Register und Steuern), die je nach Situation entweder befüllt oder samt Abschnitt
gelöscht werden.

| Platzhalter | Bedeutung | Beispielformat | Vorkommen (Datei:Zeile) | Pflicht/Optional |
|---|---|---|---|---|
| `{{REGISTERGERICHT}}` | Registergericht | Amtsgericht Leipzig | impressum.html:100 | Optional, nur bei eingetragener GbR (eGbR) |
| `{{REGISTERNUMMER}}` | Registernummer | GsR 1234 | impressum.html:101 | Optional, nur bei eingetragener GbR (eGbR) |
| `{{UST_IDNR}}` | Umsatzsteuer-Identifikationsnummer nach § 27a UStG | DE123456789 | impressum.html:106 | Optional, nur falls vergeben |

## Zusätzlich zu prüfen (keine Platzhalter, aber Entscheidungen/Fakten)

- **Name der GbR und Geschäftsbezeichnung:** Eine nicht eingetragene GbR führt keine Firma im
  handelsrechtlichen Sinn. Ihr Name setzt sich aus den Namen der Gesellschafter und dem
  Rechtsformzusatz zusammen ("Luca Sparhuber und Sharif Ibrahim GbR"). "Valtix Financial
  Management" wird daneben als Geschäftsbezeichnung geführt und darf im Marketing, auf der
  Website, in E-Mails und auf Rechnungen verwendet werden. Im Impressum, in Verträgen und im
  Rechtsverkehr muss zusätzlich die rechtliche Bezeichnung mit beiden Gesellschaftern erscheinen.
- **Registereintrag / eGbR:** Seit dem MoPeG (2024) kann sich eine GbR freiwillig als
  eingetragene GbR (eGbR) im Gesellschaftsregister eintragen lassen. Eine eGbR darf einen
  Fantasienamen als offiziellen Namen führen, dann wäre "Valtix Financial Management eGbR"
  möglich. In diesem Fall müssen Registergericht und Registernummer im Impressum stehen und der
  Abschnitt "Diensteanbieter" ist auf den eingetragenen Namen umzustellen. Ohne Eintragung
  entfällt der Abschnitt "Registereintrag" samt Hinweiskasten ersatzlos.
- **Umsatzsteuer:** Bei Kleinunternehmerregelung nach § 19 UStG gibt es keine USt-IdNr.; der
  Abschnitt entfällt dann ersatzlos. Die Steuernummer des Finanzamts gehört nicht ins Impressum.
- **Tätigkeitsbeschreibung (impressum.html):** Der Abschnitt "Tätigkeit und Umfang der Beratung"
  stellt klar, dass es sich um ein erlaubnisfreies Gewerbe handelt und keine Rechts-, Steuer-
  oder Anlageberatung erbracht wird. Inhaltlich gegenprüfen, ob das die Tätigkeit vollständig
  trifft. Sobald Finanzanlagen vermittelt oder empfohlen werden, kann eine Erlaubnis nach
  § 34f GewO erforderlich werden; dann muss der Abschnitt überarbeitet werden.
- **Verbraucherstreitbeilegung (impressum.html):** Eingetragen ist die übliche Erklärung,
  *nicht* an Schlichtungsverfahren nach § 36 VSBG teilzunehmen.
- **Datenschutzbeauftragter (datenschutz.html, Abschnitt 1):** Eingetragen ist, dass kein
  Datenschutzbeauftragter bestellt ist. Prüfen, ob das zutrifft.
- **Hinweiskästen:** Die grauen Kästen (`class="note"`) im Impressum sind Arbeitshilfen und
  sollten vor dem Livegang entfernt werden.
- **GitHub Pages / Data Privacy Framework (datenschutz.html, Abschnitt 2):** Die Zertifizierung
  von GitHub unter dem EU-US Data Privacy Framework vor Livegang im DPF-Register gegenprüfen.
- **Auftragsverarbeitung für das Kontaktformular:** Abschnitt 7 der Datenschutzerklärung nennt
  einen Vertrag zur Auftragsverarbeitung nach Art. 28 DSGVO mit dem Formulardienst. Dieser
  Vertrag muss mit dem Anbieter tatsächlich abgeschlossen werden, sonst ist die Angabe unzutreffend.

## Hinweis

Die Texte sind sorgfältig erstellte Vorlagen, ersetzen aber keine Rechtsberatung.
Vor dem Livegang von einer Anwältin oder einem Anwalt prüfen lassen.
