# Berichtsgenerator

Liest die ausgefüllte Eingabevorlage und rechnet das Modell durch.

    # Bericht erzeugen
    python3 tools/bericht/rendern.py <ausgefuellte_vorlage.xlsx>

    # nur die Kennzahlen auf der Konsole
    python3 tools/bericht/modell.py tools/bericht/beispiel_lueftungstechnik.xlsx

    # Abgleich gegen den veroeffentlichten Bericht
    python3 tools/bericht/test_abgleich.py

## Dateien

| Datei | Zweck |
|---|---|
| `VALTIX_Eingabevorlage.xlsx` | leere Vorlage, wie sie an Mandanten geht |
| `beispiel_erzeugen.py` | füllt die Vorlage mit dem Prüfdatensatz |
| `beispiel_lueftungstechnik.xlsx` | Prüfdatensatz, erzeugt aus dem obigen Skript |
| `modell.py` | liest die Datei und berechnet alle Kennzahlen |
| `diagramme.py` | Ergebnisbrücke, Kostenstruktur, Verlauf, Break-even als Inline-SVG |
| `rendern.py` | baut daraus den Bericht als HTML im Valtix-Design |
| `test_abgleich.py` | prüft 20 Größen gegen den Word-Bericht |

## Warum nicht die Excel-Formeln gelesen werden

Die Vorlage enthält Summenformeln. Deren Ergebnis steht in der Datei aber nur,
wenn Excel sie einmal berechnet und gespeichert hat. Bei einer Datei, die
jemand nur ausfüllt und zurückschickt, ist das nicht verlässlich. `modell.py`
liest deshalb ausschließlich die gelben Eingabefelder und rechnet alles selbst.

## Prüfstand

Der Prüfdatensatz stammt aus dem bestehenden Word-Bericht der Lüftungstechnik
GmbH. Juli ist eins zu eins übernommen, Januar bis Juni so aufgeteilt, dass die
dort veröffentlichten Monatsaggregate exakt herauskommen. Damit lässt sich das
Ergebnis des Generators gegen bekannte Werte prüfen.

Stand: alle Größen des Juli stimmen mit dem Bericht überein.

| Größe | Bericht | Generator |
|---|---|---|
| Deckungsbeitrag | 224.499,81 € | 224.499,81 € |
| DB-Quote | 61,1 % | 61,10 % |
| EBITDA | 42.894,16 € | 42.894,16 € |
| EBT | 33.645,81 € | 33.645,81 € |
| EBT-Marge | 9,2 % | 9,22 % |
| Auslastung | 81,6 % | 81,60 % |
| DSO | 48 Tage | 48,00 Tage |
| Eigenkapitalquote | 35,8 % | 35,81 % |
| DB je Monteurstunde | 79,05 € | 79,05 € |
| Gewinnschwelle | 2.381,87 Std. | 2.381,87 Std. |
| Sicherheitsabstand | 428,43 Std. (15,2 %) | 428,43 Std. (15,2 %) |

## Methodischer Hinweis zur Gewinnschwelle

Der Deckungsbeitrag je Leistungseinheit wird ohne die sonstigen betrieblichen
Erträge gerechnet. Diese hängen nicht an der Leistungsmenge und dürfen die
Gewinnschwelle deshalb nicht verschieben. Der ausgewiesene Deckungsbeitrag in
der GuV enthält sie dagegen, weil er sich auf die Gesamtleistung bezieht. Ohne
diese Unterscheidung läge die Gewinnschwelle rund 25 Stunden zu niedrig.

## Farbwahl in den Diagrammen

Geprüft mit dem Validator der Datenvisualisierungs-Vorlage gegen den Seitengrund
`#FBF8F2`. Das Markennavy `#232941` liegt mit OKLCH L=0,287 unterhalb des
zulässigen Helligkeitsbandes von 0,43 bis 0,77, und sowohl Navy als auch Gold
unterschreiten die Chroma-Grenze von 0,10. Beide sind als Datenfarben also nicht
zulässig.

Für Flächen und Linien werden deshalb zwei aufgehellte Nachbarn in denselben
Farbtönen verwendet:

| Rolle | Wert | Farbton |
|---|---|---|
| Reihe A, Zwischen- und Endgrößen, Erlöslinie | `#404D97` | H 273°, wie das Markennavy |
| Reihe B, Zu- und Abgänge, Kostenlinie | `#B0842A` | H 80°, wie das Markengold |

Das Paar besteht alle sechs Prüfungen: Helligkeitsband, Chroma, Farbfehlsichtigkeit
(schlechtestes Paar ΔE 26,2), Normalsicht (ΔE 30,4) und Kontrast gegen den Grund.
Navy und Gold der Marke bleiben Text- und Strukturfarben.

Die Ampel nutzt die reservierten Statusfarben. Gelb liegt auf hellem Grund unter
3:1 Kontrast; das ist zulässig, weil in derselben Zeile immer der Wortlaut
(„Grün", „Gelb", „Rot") sowie Ist- und Zielwert stehen. Die Farbe trägt die
Aussage nie allein.

## Bewusste Festlegungen

- **Kein Dunkelmodus.** Der Bericht ist ein Dokument in Markenfarben, das auch
  gedruckt und als PDF weitergegeben wird. Alle Farben sind ausdrücklich gesetzt.
- **Diagramme scrollen auf schmalen Bildschirmen** in ihrem eigenen Rahmen,
  statt unlesbar zu schrumpfen. Die Seite selbst läuft nie quer.
- **Keine Zahl an jedem Punkt.** Im Monatsverlauf sind nur erster, letzter,
  höchster und niedrigster Wert beschriftet.
- **Werte im Diagramm zusätzlich als Tabelle.** GuV, Monatsverlauf,
  Vormonatsvergleich und Break-even stehen vollständig als Tabelle im Bericht.
