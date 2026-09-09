# Berichtsgenerator

Liest die ausgefüllte Eingabevorlage und rechnet das Modell durch.

    python3 tools/bericht/modell.py tools/bericht/beispiel_lueftungstechnik.xlsx

## Dateien

| Datei | Zweck |
|---|---|
| `VALTIX_Eingabevorlage.xlsx` | leere Vorlage, wie sie an Mandanten geht |
| `beispiel_erzeugen.py` | füllt die Vorlage mit dem Prüfdatensatz |
| `beispiel_lueftungstechnik.xlsx` | Prüfdatensatz, erzeugt aus dem obigen Skript |
| `modell.py` | liest die Datei und berechnet alle Kennzahlen |

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
