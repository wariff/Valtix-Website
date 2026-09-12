# Indexierung: was behoben ist und was noch fehlt

Stand: September 2026.

## Im Repo behoben

**Zwei Adressen für die Startseite.** Impressum, Datenschutzerklärung,
404-Seite, Newsletter-Bestätigung und die Portalseite verlinkten die
Startseite als `index.html`, kanonisch ist aber `https://valtixfm.de/`.
Alle 24 Verweise zeigen jetzt auf `/`.

**noindex, das nie gelesen wurde.** Impressum, Datenschutz,
Newsletter-Bestätigung und die beiden Portalseiten tragen ein `noindex` im
Kopf und standen zugleich auf `Disallow` in der robots.txt. Ein noindex
wirkt nur, wenn die Seite gelesen werden darf. Die Disallow-Regeln sind
weg, der Grund steht als Kommentar in der Datei.

## Geprüft und in Ordnung

- Alle 21 Adressen der sitemap.xml sind kanonisch und tragen kein noindex.
- Keine Verweise mehr auf `index.html`, keine auf `http://`, keine auf
  `www.valtixfm.de`, keine auf die github.io-Adresse.
- `og:url` stimmt auf jeder Seite mit dem Canonical überein, ebenso die
  Adressen in den JSON-LD-Blöcken und in der feed.xml.

## Was der Coverage-Export vom 12.09.2026 sagt

Die Datei enthält nur die Zusammenfassung, keine Adressliste. Stand der
Zahlen ist der 04.09.2026, also vor den Korrekturen oben.

| Grund | Quelle | Seiten |
|---|---|---|
| Seite mit Weiterleitung | Website | 1 |
| Gefunden – zurzeit nicht indexiert | Google-Systeme | 4 |
| Gecrawlt – zurzeit nicht indexiert | Google-Systeme | 1 |

Dazu 11 indexierte und 6 nicht indexierte Seiten bei 17 Google bekannten
Adressen. Die sitemap.xml nennt 21, vier davon kennt Google also noch nicht.

**Es ist genau eine Seite mit Weiterleitung, nicht zwanzig.** Das ändert die
Lage: im Quellcode gibt es keine einzige Weiterleitung, kein
`meta http-equiv="refresh"` und kein `location.href`. Die Weiterleitung kommt
also vom Server, und GitHub Pages leitet nur in vier Fällen um: bei
`/index.html` auf `/`, bei `http://` auf `https://`, von der
github.io-Adresse auf die eigene Domain und, falls ein CNAME für www
gesetzt ist, von www auf die Domain ohne www.

Bis heute verlinkten fünf Seiten die Startseite als `index.html`. Das ist
die einzige dieser vier Adressen, die überhaupt intern verlinkt war, und die
Anzahl passt: eine. Sehr wahrscheinlich ist die gemeldete Seite also
`https://valtixfm.de/index.html`. Bewiesen ist das nicht, dazu braucht es
die Adressliste. Die Ursache ist mit der Umstellung aller Verweise auf `/`
in jedem Fall weg.

**Die anderen beiden Gründe sind keine Fehler.** „Gefunden – zurzeit nicht
indexiert" heißt: Google kennt die Adresse, hat sie aber noch nicht gelesen.
„Gecrawlt – zurzeit nicht indexiert" heißt: gelesen, aber noch nicht
aufgenommen. Beides ist bei einer Domain, die seit Ende August Daten
liefert, der Normalfall und lässt sich nicht erzwingen. Eine verwaiste Seite
als Ursache fällt aus: jede der 21 Sitemap-Adressen ist von mindestens zwei
anderen Seiten verlinkt, am schwächsten
`ratgeber/kundenerlebnis-schuhgeschaeft.html` und
`ratgeber/kontokorrent-dauerhaft-ausgeschoepft.html` mit je zwei.

## So kommt die Adressliste zustande

Der Export der Übersichtsseite enthält sie nicht. In der Search Console
unter Seitenindexierung die Zeile „Seite mit Weiterleitung" anklicken, dann
erscheint die Tabelle mit den Beispieladressen, und dort gibt es einen
eigenen Export. Alternativ die Adresse
`https://valtixfm.de/index.html` in die URL-Prüfung eingeben; steht dort
„Seite mit Weiterleitung", ist die Vermutung bestätigt.

Danach die Validierung starten. Im Export steht sie auf „Nicht gestartet".

## Was von hier aus nicht zu prüfen ist

Diese Arbeitsumgebung kommt weder an valtixfm.de noch an die
Search-Console-Tabelle. Beides läuft über eine Netzsperre. Die Liste der
betroffenen Adressen muss also von außen kommen.

## Die üblichen Ursachen für „Seite mit Weiterleitung"

Für den Fall, dass die Liste nachgereicht wird, in der Reihenfolge der
Wahrscheinlichkeit:

1. **`http://`-Adressen.** GitHub Pages leitet mit „Enforce HTTPS" jede
   http-Adresse auf https um. Wer solche Adressen im Bericht sieht, sieht
   eine gewollte Weiterleitung. Handlungsbedarf besteht nicht, die Meldung
   verschwindet von allein, sobald Google die https-Form indexiert hat.
2. **Die github.io-Adresse.** `wariff.github.io/Valtix-Website/` leitet auf
   die eigene Domain um. Auch das ist gewollt. Falls diese Adressen im
   Bericht stehen, wurden sie irgendwo verlinkt.
3. **`www.`-Adressen.** Nur ein Thema, wenn beim Anbieter ein
   CNAME für www gesetzt ist. Dann ist die Weiterleitung auf die Domain
   ohne www gewollt.
4. **Adressen mit `index.html`.** Das war der echte Fehler und ist behoben.
   Google braucht einige Wochen, bis diese Adressen aus dem Bericht fallen.

## Nächster Schritt

Die betroffenen Adressen aus der Search Console hierher geben, dann lässt
sich Fall für Fall sagen, ob die Weiterleitung gewollt ist oder ein Fehler.
Eine erneute Prüfung in der Search Console ist erst sinnvoll, wenn die
Änderungen live sind; das sind sie seit dem Deploy vom 12. September 2026.
