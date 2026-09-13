# Pakete im Portal

Stand: September 2026.

## Die Pakete heißen Analyse, Betreuung, Intensiv

So stehen sie auf der Website, so heißen sie im Code. Ein Paket „Basis" gibt
es nicht.

| Paket | Portal öffnet |
|---|---|
| Analyse | Unterlagen hochladen, der Bericht zum Health Check |
| Betreuung | zusätzlich den Verlauf über alle Monate und den Maßnahmenplan |
| Intensiv | dasselbe wie Betreuung |

Zwischen Betreuung und Intensiv liegt im Portal kein Unterschied. Der liegt
in der Taktung der Pitches, also außerhalb der Software. Das ist Absicht und
keine Lücke. Wer das ändern will, ändert `PAKETE` in `portal/pakete.py`, sonst
nichts.

## Wer hochladen darf

Nur angelegte Mandanten. Valtix legt den Mandanten an, wählt das Paket und
verschickt einen einmaligen Einladungslink. Ohne Vertrag kein Zugang und
damit auch keine fremden Finanzdaten in der Ablage und keine Kosten für das
Auslesen.

## Die Freischaltung, nach der gefragt wurde

Die gibt es schon, sie heißt nur anders. Der Mandant lädt hoch und reicht
ein, die Periode geht auf `eingereicht`, Valtix prüft und gibt frei, erst
dann steht der Bericht beim Mandanten. Das ist die Statuskette in
`portal/perioden.py`, kein zweites Programm.

Neu ist allein die Staffelung: welches Paket welche Ansicht öffnet.

## Der Maßnahmenplan

Angelegt wird eine Maßnahme von Valtix, denn sie folgt aus dem Health Check.
Status und Notizen setzen danach beide Seiten, und jede Änderung meldet sich
bei der anderen. Der Plan hängt am Mandanten, nicht am Monat, weil eine
Maßnahme über mehrere Berichte läuft und man ihr das ansehen soll. Gelöscht
wird nichts, auch Erledigtes bleibt stehen.

Wer das Paket nicht hat, kommt weder über die Oberfläche noch über die
Adresse heran. Beides ist getestet.

## Was noch offen ist

Ein Mandant, der von Betreuung auf Analyse zurückgestuft wird, verliert den
Zugang zum Maßnahmenplan, die Daten bleiben aber stehen. Ob das so bleiben
soll oder ob er seine Historie behalten darf, ist eine kaufmännische
Entscheidung und keine technische.
