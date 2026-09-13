# Gescannte Belege maschinell lesen

Stand: September 2026. Gebaut und getestet, aber noch nicht gegen die echte
Schnittstelle gelaufen. Wer das einschaltet, prüft die ersten Ergebnisse
Zeile für Zeile gegen den Papierauszug.

## Was es macht

Bisher endete ein eingescannter Kontoauszug bei „braucht OCR" und blieb
liegen. Jetzt bekommt er einen zweiten Anlauf: das PDF geht als Ganzes an
Claude, zurück kommt eine feste Struktur mit Anfangs- und Endsaldo, Zeitraum,
IBAN und den einzelnen Posten. Daraus wird eine Extraktion wie jede andere,
die in derselben Prüfansicht landet.

Ein eigener OCR-Anbieter wird dafür nicht gebraucht, das Modell liest das PDF
direkt.

## Was sich am Vertrauensmodell nicht ändert

Nichts. Das Ergebnis ist ein Vorschlag mit einer Konfidenz von höchstens 0,5,
also immer unter dem, was eine gelesene Tabelle bekommt. Freigegeben wird von
Hand, jede Korrektur steht im Protokoll und wird für den Folgemonat gelernt.
Der Endsaldo kommt als eigene Zeile auf Konto 1800, damit die Übernahme ihn
wie jeden anderen Posten behandelt und die Prüfliste ihn gegen den Vormonat
hält.

## Ohne Zugang passiert nichts

Fehlt `ANTHROPIC_API_KEY` oder das Paket `anthropic`, wird gar keine Aufgabe
eingereiht. Der Scan bleibt auf „braucht OCR" stehen, mit Hinweis. Das Portal
läuft vollständig ohne diesen Dienst.

    ANTHROPIC_API_KEY   Zugang. Fehlt er, ist die Erkennung aus.
    VALTIX_KI_MODELL    Modell, sonst claude-opus-5
    VALTIX_KI_REGION    Verarbeitungsregion, sonst die des Kontos

## Was vor dem Einschalten zu klären ist

**Auftragsverarbeitungsvertrag.** Mandantenunterlagen gehen an einen
Auftragsverarbeiter. Ohne AVV wird das nicht eingeschaltet.

**Verarbeitungsregion.** `VALTIX_KI_REGION` reicht den Wert durch, den die
Schnittstelle als Region entgegennimmt. In der Dokumentation, die mir vorlag,
waren das `us` und `global`. Ob eine Verarbeitung in der EU möglich ist, muss
vor dem Einschalten direkt beim Anbieter geklärt werden. Nicht annehmen.

**Datenschutzerklärung.** Der Dienst gehört hinein, sobald er wirklich
eingeschaltet ist. Vorher nicht.

## Kosten

Bei rund 19.000 Token Eingabe und 3.000 Ausgabe je Mandant und Monat, also
einem achtseitigen Scan plus Klärfällen:

| Modell | je Mandant | 15 Mandanten |
|---|---|---|
| Haiku 4.5 | 0,03 $ | 0,51 $ |
| Sonnet 5 | 0,07 $ | 1,02 $ |
| Opus 5 | 0,17 $ | 2,55 $ |

Voreingestellt ist Opus 5. Wer sparen will, setzt `VALTIX_KI_MODELL`, sollte
die Trefferquote aber an echten Auszügen messen, bevor er umstellt.

## Was noch nicht geprüft ist

Die Anfrage selbst. Diese Umgebung hat keinen Zugang, also ist alles um den
Aufruf herum getestet, der Aufruf aber nicht: dass ohne Schlüssel nichts
passiert, dass die Anfrage das PDF und das Schema richtig enthält, dass eine
Ablehnung als Fehler ankommt statt als geratenes Ergebnis, dass aus dem
Gelesenen eine für die Übernahme lesbare Extraktion wird, und dass die
Warteschlange den zweiten Anlauf nur dann einreiht, wenn die Erkennung
eingerichtet ist. Vierzehn Tests.

Der erste echte Lauf gehört gegen einen Auszug, dessen Zahlen ihr kennt.
