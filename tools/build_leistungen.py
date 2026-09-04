#!/usr/bin/env python3
"""Erzeugt die Leistungsseiten mit FAQ-Auszeichnung."""
import os, json, html, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys_path = os.path.join(ROOT, 'ratgeber')

# Gemeinsames CSS und Bausteine aus dem Ratgeber-Generator uebernehmen
import importlib.util
spec = importlib.util.spec_from_file_location(
    "rg", "/tmp/claude-0/-home-user-intro/faeb7073-b3db-556d-81bd-c942bd78d164/scratchpad/build_ratgeber.py")

# Nur die Konstanten lesen, ohne das Skript auszufuehren
src = open("/tmp/claude-0/-home-user-intro/faeb7073-b3db-556d-81bd-c942bd78d164/scratchpad/build_ratgeber.py").read()
SHARED_CSS = re.search(r"SHARED_CSS = '''(.*?)'''", src, re.S).group(1)
HEADER = re.search(r"HEADER = '''(.*?)'''", src, re.S).group(1)
FOOTER = re.search(r"FOOTER = '''(.*?)'''", src, re.S).group(1)

EXTRA_CSS = '''
  main{max-width:760px;margin-inline:auto;padding:48px 24px 24px}
  .crumb{font-size:.86rem;color:var(--ink-soft);margin-bottom:26px}
  .crumb a{text-decoration:none}
  .crumb a:hover{text-decoration:underline;text-underline-offset:3px}
  .tag{display:inline-block;font-size:.74rem;font-weight:700;letter-spacing:.1em;
       text-transform:uppercase;color:var(--gold-deep);background:rgba(166,129,63,.13);
       padding:5px 13px;border-radius:var(--r-pill);margin-bottom:18px}
  h1{font-size:clamp(2rem,4.6vw,2.9rem);line-height:1.08;margin-bottom:16px}
  .lede{font-size:1.14rem;color:var(--ink-soft);margin-bottom:14px}
  .hero-cta{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0 8px;
            padding-bottom:34px;border-bottom:1px solid var(--hairline)}
  h2{font-size:1.5rem;margin:42px 0 12px}
  h3{font-size:1.12rem;margin:26px 0 7px}
  p{margin-bottom:16px}
  ul,ol{margin:0 0 18px 22px}
  li{margin-bottom:9px}
  strong{font-weight:600}
  .facts{list-style:none;margin:24px 0 0;padding:0;display:grid;
         grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}
  .facts li{margin:0;padding:18px 20px;border-radius:16px;
            background:rgba(255,255,255,.62);border:1px solid var(--glass-border);
            backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)}
  .facts b{display:block;font-size:1.5rem;font-weight:800;letter-spacing:-.03em;margin-bottom:3px}
  .facts span{font-size:.88rem;color:var(--ink-soft)}
  .faq{margin-top:16px}
  .faq details{border-bottom:1px solid var(--hairline);padding:4px 0}
  .faq summary{cursor:pointer;padding:15px 0;font-weight:600;font-size:1.02rem;
               list-style:none;display:flex;justify-content:space-between;align-items:center;gap:16px}
  .faq summary::-webkit-details-marker{display:none}
  .faq summary::after{content:"+";font-size:1.4rem;font-weight:400;color:var(--gold-deep);flex:none;line-height:1}
  .faq details[open] summary::after{content:"–"}
  .faq details p{margin:0 0 16px;color:var(--ink-soft);font-size:.97rem}
  .cta-box{margin:48px 0 0;padding:34px 32px;border-radius:var(--r-lg);color:#fff;
           background:linear-gradient(152deg,#2E3552 0%,#1A1F33 100%);
           box-shadow:0 24px 60px rgba(23,27,44,.28)}
  .cta-box h2{font-size:1.42rem;margin:0 0 10px;color:#fff}
  .cta-box p{color:rgba(255,255,255,.78);font-size:.98rem;margin-bottom:24px}
  .more{margin:52px 0 0;padding-top:26px;border-top:1px solid var(--hairline)}
  .more h2{font-size:1.15rem;margin:0 0 14px}
  .more ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
  .more a{text-decoration:none;font-weight:600;font-size:.97rem}
  .more a:hover{color:var(--gold-deep)}
  .more span{display:block;font-weight:400;font-size:.88rem;color:var(--ink-soft)}
'''

SEITEN = [
{
 "slug": "unternehmensberatung-leipzig",
 "kategorie": "Standort Leipzig",
 "titel": "Unternehmensberatung in Leipzig",
 "h1": "Unternehmensberatung in Leipzig",
 "beschreibung": "Betriebswirtschaftliche Beratung für Leipziger Unternehmen: Kennzahlenanalyse, Liquidität und Wachstum. Persönlich vor Ort, kostenloses Erstgespräch.",
 "lede": "Wir beraten inhabergeführte Unternehmen in Leipzig und Umgebung bei allem, was mit Zahlen zu tun hat: Wo steht der Betrieb, wo geht Geld verloren, und was ist als Nächstes zu tun.",
 "service": "Betriebswirtschaftliche Unternehmensberatung",
 "inhalt": '''
<h2>Für wen wir arbeiten</h2>
<p>Unsere Mandanten sind Betriebe zwischen etwa fünf und fünfzig Mitarbeitern: Handwerksbetriebe, Gastronomie, Einzelhandel, Agenturen und Dienstleister. Was sie verbindet, ist selten ein Mangel an Arbeit. Meistens fehlt der Überblick darüber, ob sich diese Arbeit tatsächlich rechnet.</p>
<p>Für Konzernstrukturen und Restrukturierungen im großen Stil sind wir nicht die richtigen Ansprechpartner. Wir arbeiten dort, wo die Geschäftsführung noch selbst im Betrieb steht und Entscheidungen ohne Gremien getroffen werden.</p>

<h2>Warum Leipzig</h2>
<p>Wir sitzen in Leipzig und arbeiten überwiegend im mitteldeutschen Raum. Das hat einen praktischen Grund: Bei einer Kennzahlenanalyse hilft es, den Betrieb einmal gesehen zu haben. Wer die Werkstatt kennt, versteht die Zahlen zum Wareneinsatz anders als jemand, der nur die Buchhaltung vorliegen hat.</p>
<p>Termine finden bei Ihnen im Betrieb statt oder digital, je nachdem was besser passt. Für Mandanten außerhalb der Region arbeiten wir vollständig digital.</p>

<h2>Was wir konkret tun</h2>
<p>Der Einstieg ist immer derselbe: der <a href="/financial-health-check.html">Financial Health Check</a>. Wir sichten BWA, Bilanz und offene Posten, erheben die entscheidenden Kennzahlen und stellen Ihnen das Ergebnis in verständlicher Sprache vor.</p>
<p>Daraus ergibt sich, woran gearbeitet wird. Häufige Schwerpunkte sind:</p>
<ul>
  <li><a href="/liquiditaetsberatung.html">Liquidität</a>: gebundenes Kapital freisetzen, Zahlungsziele ordnen, Reichweite planen</li>
  <li>Ertrag: Kostenstruktur prüfen, Preise und Margen nachrechnen</li>
  <li>Wachstum: prüfen, ob und wie der Betrieb den nächsten Schritt finanziell trägt</li>
  <li>Steuerung: ein schlankes Reporting aufsetzen, mit dem die Geschäftsführung monatlich arbeiten kann</li>
</ul>

<h2>Was wir nicht tun</h2>
<p>Wir sind Betriebswirte, keine Steuerberater und keine Rechtsanwälte. Steuerliche Gestaltung, Jahresabschlüsse und rechtliche Bewertungen gehören nicht zu unserem Leistungsumfang; dafür arbeiten wir mit Ihrem Steuerberater zusammen oder vermitteln bei Bedarf. Anlageberatung oder Finanzprodukte bieten wir nicht an.</p>
''',
 "faq": [
   ("Was kostet eine Beratung bei Valtix?",
    "Das hängt vom Umfang ab. Der Financial Health Check als einmalige Analyse hat einen festen Preis, den wir im Erstgespräch nennen. Für die laufende Betreuung gibt es monatliche Pakete. Das Erstgespräch selbst ist kostenlos und unverbindlich."),
   ("Wie lange dauert es, bis ich ein Ergebnis sehe?",
    "Nach Vorliegen der Unterlagen erhalten Sie den Ergebnisbericht innerhalb von zwei Wochen. Erste Sofortmaßnahmen besprechen wir oft schon im Analysegespräch."),
   ("Welche Unterlagen brauchen Sie von mir?",
    "In der Regel die BWA der letzten zwölf Monate, den letzten Jahresabschluss und eine Liste der offenen Posten. Alles Weitere klären wir im Gespräch."),
   ("Arbeiten Sie auch mit meinem Steuerberater zusammen?",
    "Ja, das ist der Normalfall. Der Steuerberater kennt die Zahlen, wir arbeiten mit ihnen. Eine Zusammenarbeit spart Ihnen Zeit und vermeidet Doppelarbeit."),
 ],
 "verwandt": [("/financial-health-check.html","Financial Health Check","Der Einstieg: Analyse und Maßnahmenplan"),
              ("/liquiditaetsberatung.html","Liquiditätsberatung","Wenn Geld im Betrieb gebunden ist"),
              ("/ratgeber.html","Ratgeber","Beiträge aus der Praxis")],
},
{
 "slug": "unternehmensberatung-ulm",
 "kategorie": "Standort Ulm",
 "titel": "Unternehmensberatung in Ulm",
 "h1": "Unternehmensberatung in Ulm",
 "beschreibung": "Betriebswirtschaftliche Beratung für Unternehmen in Ulm und Neu-Ulm: Kennzahlen, Liquidität und Ertrag. Termine vor Ort, Erstgespräch kostenlos.",
 "lede": "Wir arbeiten regelmäßig im Raum Ulm und beraten dort inhabergeführte Betriebe bei allem, was mit Zahlen zu tun hat: Wo steht das Unternehmen, wo geht Geld verloren, und was ist als Nächstes zu tun.",
 "service": "Betriebswirtschaftliche Unternehmensberatung",
 "gebiet": "Ulm",
 "inhalt": '''
<h2>Für wen wir in Ulm arbeiten</h2>
<p>Unsere Mandanten sind Betriebe zwischen etwa fünf und fünfzig Mitarbeitern. Im Raum Ulm sind das vor allem Handwerksbetriebe, Zulieferer für den Maschinenbau, Logistiker, Einzelhändler, Gastronomie und Dienstleister. Was sie verbindet, ist selten ein Mangel an Arbeit. Meistens fehlt der Überblick darüber, ob sich diese Arbeit tatsächlich rechnet.</p>
<p>Für Konzernstrukturen und große Restrukturierungen sind wir nicht die richtigen Ansprechpartner. Wir arbeiten dort, wo die Geschäftsführung noch selbst im Betrieb steht und Entscheidungen ohne Gremien getroffen werden.</p>

<h2>Wie die Zusammenarbeit vor Ort abläuft</h2>
<p>Unser Sitz ist Leipzig, im Raum Ulm arbeiten wir mit Terminen beim Mandanten. Das hat einen praktischen Grund: Bei einer Kennzahlenanalyse hilft es, den Betrieb einmal gesehen zu haben. Wer die Werkstatt, das Lager oder den Verkaufsraum kennt, liest Zahlen zum Wareneinsatz anders als jemand, dem nur die Buchhaltung vorliegt.</p>
<p>Der Ablauf ist deshalb meist so: ein Vor-Ort-Termin für Aufnahme und Betriebsrundgang, die Auswertung machen wir anschließend, und die Ergebnisbesprechung findet je nach Wunsch wieder vor Ort oder digital statt. Für die laufende Betreuung reichen in der Regel digitale Termine, ergänzt um einen Besuch im Quartal.</p>
<p>Das Einzugsgebiet umfasst Ulm, Neu-Ulm, den Alb-Donau-Kreis und den angrenzenden Donau-Iller-Raum.</p>

<h2>Was wir konkret tun</h2>
<p>Der Einstieg ist immer derselbe: der <a href="/financial-health-check.html">Financial Health Check</a>. Wir sichten BWA, Bilanz und offene Posten, erheben die entscheidenden Kennzahlen und stellen Ihnen das Ergebnis in verständlicher Sprache vor.</p>
<p>Daraus ergibt sich, woran gearbeitet wird. Häufige Schwerpunkte sind:</p>
<ul>
  <li><a href="/liquiditaetsberatung.html">Liquidität</a>: gebundenes Kapital freisetzen, Zahlungsziele ordnen, Reichweite planen</li>
  <li>Ertrag: Kostenstruktur prüfen, Preise und <a href="/ratgeber/stundensatz-richtig-kalkulieren.html">Stundensätze</a> nachrechnen</li>
  <li>Wachstum: prüfen, ob und wie der Betrieb den nächsten Schritt finanziell trägt</li>
  <li>Steuerung: ein schlankes Reporting aufsetzen, mit dem die Geschäftsführung monatlich arbeiten kann</li>
</ul>

<h2>Was wir nicht tun</h2>
<p>Wir sind Betriebswirte, keine Steuerberater und keine Rechtsanwälte. Steuerliche Gestaltung, Jahresabschlüsse und rechtliche Bewertungen gehören nicht zu unserem Leistungsumfang; dafür arbeiten wir mit Ihrem Steuerberater zusammen. Anlageberatung oder Finanzprodukte bieten wir nicht an.</p>
''',
 "faq": [
   ("Haben Sie ein Büro in Ulm?",
    "Unser Sitz ist Leipzig. Im Raum Ulm arbeiten wir mit Terminen direkt beim Mandanten im Betrieb, ergänzt um digitale Termine. Für die Beratung selbst macht das keinen Unterschied, die Anfahrt ist in unseren Konditionen bereits berücksichtigt."),
   ("Was kostet eine Beratung bei Valtix?",
    "Das hängt vom Umfang ab. Der Financial Health Check als einmalige Analyse hat einen festen Preis, den wir im Erstgespräch nennen. Für die laufende Betreuung gibt es monatliche Pakete. Das Erstgespräch selbst ist kostenlos und unverbindlich."),
   ("Wie lange dauert es, bis ich ein Ergebnis sehe?",
    "Nach Vorliegen der Unterlagen erhalten Sie den Ergebnisbericht innerhalb von zwei Wochen. Erste Sofortmaßnahmen besprechen wir oft schon im Analysegespräch."),
   ("Arbeiten Sie auch mit meinem Steuerberater zusammen?",
    "Ja, das ist der Normalfall. Der Steuerberater kennt die Zahlen, wir arbeiten mit ihnen. Eine Zusammenarbeit spart Ihnen Zeit und vermeidet Doppelarbeit."),
 ],
 "verwandt": [("/financial-health-check.html","Financial Health Check","Der Einstieg: Analyse und Maßnahmenplan"),
              ("/unternehmensberatung-mannheim.html","Unternehmensberatung Mannheim","Beratung im Rhein-Neckar-Raum"),
              ("/unternehmensberatung-leipzig.html","Unternehmensberatung Leipzig","Unser Sitz in Mitteldeutschland")],
},
{
 "slug": "unternehmensberatung-mannheim",
 "kategorie": "Standort Mannheim",
 "titel": "Unternehmensberatung in Mannheim",
 "h1": "Unternehmensberatung in Mannheim",
 "beschreibung": "Beratung für Unternehmen in Mannheim und der Rhein-Neckar-Region: Kennzahlen, Liquidität und Ertrag. Termine vor Ort, Erstgespräch kostenlos.",
 "lede": "Wir arbeiten regelmäßig in der Rhein-Neckar-Region und beraten dort inhabergeführte Unternehmen bei der Frage, woran es in den Zahlen hakt und was sich am schnellsten ändern lässt.",
 "service": "Betriebswirtschaftliche Unternehmensberatung",
 "gebiet": "Mannheim",
 "inhalt": '''
<h2>Für wen wir in Mannheim arbeiten</h2>
<p>Unsere Mandanten sind Betriebe zwischen etwa fünf und fünfzig Mitarbeitern. In der Rhein-Neckar-Region sind das häufig Handel und Großhandel, Logistik und Spedition, Handwerk, Gastronomie sowie Agenturen und technische Dienstleister. Die Ausgangslage ähnelt sich: Der Betrieb läuft, aber am Monatsende bleibt weniger übrig als erwartet, oder das Konto ist knapper, als es die Auftragslage vermuten lässt.</p>
<p>Für Konzernstrukturen und große Restrukturierungen sind wir nicht die richtigen Ansprechpartner. Wir arbeiten dort, wo die Geschäftsführung noch selbst im Betrieb steht.</p>

<h2>Wie die Zusammenarbeit vor Ort abläuft</h2>
<p>Unser Sitz ist Leipzig, in der Region Mannheim arbeiten wir mit Terminen beim Mandanten. Der erste Termin findet im Betrieb statt, weil sich viele Fragen zum Wareneinsatz, zum Lager oder zur Auslastung vor Ort in zehn Minuten klären lassen und am Telefon in einer Stunde nicht.</p>
<p>Die Auswertung erfolgt anschließend bei uns, die Ergebnisbesprechung wieder vor Ort oder digital. Für die laufende Betreuung genügen meist digitale Termine mit einem Besuch im Quartal.</p>
<p>Das Einzugsgebiet umfasst Mannheim, Ludwigshafen, Heidelberg, Speyer, Worms und die angrenzende Metropolregion Rhein-Neckar.</p>

<h2>Was wir konkret tun</h2>
<p>Der Einstieg ist der <a href="/financial-health-check.html">Financial Health Check</a>: BWA, Bilanz und offene Posten werden gesichtet, die entscheidenden Kennzahlen erhoben und das Ergebnis in verständlicher Sprache vorgestellt.</p>
<p>Typische Schwerpunkte danach:</p>
<ul>
  <li><a href="/liquiditaetsberatung.html">Liquidität</a>: Working Capital senken, Zahlungsziele ordnen, Cash-Reichweite planen</li>
  <li>Ertrag: Margen je Produktgruppe rechnen, <a href="/ratgeber/preiserhoehung-durchsetzen.html">Preise anpassen</a>, Kostenstruktur prüfen</li>
  <li>Handel und Import: <a href="/ratgeber/import-export-ausserhalb-eu.html">Landed Cost und Kapitalbindung</a> sauber kalkulieren</li>
  <li>Steuerung: ein monatliches Reporting, mit dem die Geschäftsführung tatsächlich arbeitet</li>
</ul>

<h2>Was wir nicht tun</h2>
<p>Wir sind Betriebswirte, keine Steuerberater und keine Rechtsanwälte. Steuerliche Gestaltung, Jahresabschlüsse und rechtliche Bewertungen gehören nicht zu unserem Leistungsumfang. Anlageberatung oder Finanzprodukte bieten wir nicht an.</p>
''',
 "faq": [
   ("Haben Sie ein Büro in Mannheim?",
    "Unser Sitz ist Leipzig. In der Region Mannheim arbeiten wir mit Terminen direkt beim Mandanten im Betrieb, ergänzt um digitale Termine. Die Anfahrt ist in unseren Konditionen bereits berücksichtigt."),
   ("Beraten Sie auch Unternehmen in Ludwigshafen und Heidelberg?",
    "Ja. Das Einzugsgebiet umfasst die gesamte Metropolregion Rhein-Neckar, also unter anderem Ludwigshafen, Heidelberg, Speyer und Worms."),
   ("Wie lange dauert es, bis ich ein Ergebnis sehe?",
    "Nach Vorliegen der Unterlagen erhalten Sie den Ergebnisbericht innerhalb von zwei Wochen. Erste Sofortmaßnahmen besprechen wir oft schon im Analysegespräch."),
   ("Welche Unterlagen brauchen Sie von mir?",
    "In der Regel die BWA der letzten zwölf Monate, den letzten Jahresabschluss und eine Liste der offenen Posten. Alles Weitere klären wir im Gespräch."),
 ],
 "verwandt": [("/financial-health-check.html","Financial Health Check","Der Einstieg: Analyse und Maßnahmenplan"),
              ("/unternehmensberatung-ulm.html","Unternehmensberatung Ulm","Beratung im Raum Ulm und Neu-Ulm"),
              ("/hilfe-bei-zahlungsschwierigkeiten.html","Hilfe bei Zahlungsschwierigkeiten","Wenn es bereits eng ist")],
},
{
 "slug": "financial-health-check",
 "kategorie": "Leistung",
 "titel": "Financial Health Check",
 "h1": "Der Financial Health Check",
 "beschreibung": "Kennzahlenanalyse für den Mittelstand: Wo steht Ihr Unternehmen, wo liegen Risiken, wo Potenziale. Ergebnisbericht mit Maßnahmenplan in 14 Tagen.",
 "lede": "Eine strukturierte Bestandsaufnahme Ihrer Zahlen. Sie erfahren, wie es um Ihren Betrieb steht, woran das liegt und was zuerst zu tun ist.",
 "service": "Financial Health Check",
 "inhalt": '''
<ul class="facts">
  <li><b>20+</b><span>geprüfte Kennzahlen</span></li>
  <li><b>14 Tage</b><span>bis zum Bericht</span></li>
  <li><b>3</b><span>Schritte bis zum Plan</span></li>
</ul>

<h2>Warum eine Analyse überhaupt nötig ist</h2>
<p>Die meisten Geschäftsführer wissen ungefähr, wie es läuft. Ungefähr reicht aber nicht, wenn es um die Frage geht, ob der Betrieb in acht Monaten noch zahlungsfähig ist oder ob eine Investition tragbar wäre.</p>
<p>Die Zahlen dafür liegen fast immer schon vor. Sie stehen in der BWA, im Jahresabschluss und in der offenen Postenliste. Nur werden sie selten so ausgewertet, dass eine Entscheidung daraus folgt.</p>

<h2>Was geprüft wird</h2>
<p>Wir erheben Kennzahlen aus vier Bereichen und setzen sie zueinander ins Verhältnis:</p>
<ul>
  <li><strong>Liquidität</strong>: Liquiditätsgrade, Cash-Reichweite, Working Capital, Debitoren- und Kreditorenlaufzeit</li>
  <li><strong>Rentabilität</strong>: Umsatzrendite, Rohertragsquote, Materialquote, Personalquote</li>
  <li><strong>Stabilität</strong>: Eigenkapitalquote, Verschuldungsgrad, Anlagendeckung</li>
  <li><strong>Entwicklung</strong>: Verlauf über die letzten zwölf Monate und Vergleich mit branchenüblichen Werten</li>
</ul>

<h2>Der Ablauf</h2>
<h3>1. Analyse</h3>
<p>Sie stellen uns BWA, Jahresabschluss und offene Posten zur Verfügung. Wir werten aus und melden uns bei Rückfragen. Ihr Aufwand beschränkt sich auf das Zusammenstellen der Unterlagen.</p>
<h3>2. Diagnose</h3>
<p>Sie erhalten einen schriftlichen Ergebnisbericht: wo der Betrieb steht, welche Kennzahlen auffällig sind, was die wahrscheinliche Ursache ist. Dazu ein Vergleich mit Ihrer Branche.</p>
<h3>3. Maßnahmenplan</h3>
<p>Im Abschlussgespräch gehen wir den Bericht gemeinsam durch. Sie bekommen eine priorisierte Liste: was zuerst angegangen wird, was danach, und woran sich der Erfolg messen lässt.</p>

<h2>Was Sie am Ende haben</h2>
<p>Einen Bericht, den Sie auch Ihrer Bank vorlegen können, eine klare Rangfolge der Baustellen und eine Handvoll Kennzahlen, die Sie künftig selbst im Blick behalten. Ob Sie danach allein weiterarbeiten oder uns dabeihaben wollen, entscheiden Sie.</p>
''',
 "faq": [
   ("Ist der Health Check auch sinnvoll, wenn es gut läuft?",
    "Gerade dann. In Wachstumsphasen entstehen Liquiditätslücken besonders leicht, weil jeder neue Auftrag zuerst Geld bindet. Wer die Zahlen kennt, wächst kontrollierter."),
   ("Erfährt mein Steuerberater davon?",
    "Nur wenn Sie es wollen. Viele Mandanten binden ihn ein, weil er die Unterlagen ohnehin hat. Verpflichtend ist das nicht."),
   ("Wie vertraulich ist das Ganze?",
    "Alle Unterlagen und Ergebnisse bleiben zwischen uns. Auf Wunsch schließen wir vorab eine Vertraulichkeitsvereinbarung."),
   ("Was passiert nach dem Health Check?",
    "Sie entscheiden. Viele setzen die Maßnahmen selbst um und melden sich nach einem Jahr wieder. Andere nehmen die monatliche Betreuung, damit jemand dranbleibt."),
 ],
 "verwandt": [("/liquiditaetsberatung.html","Liquiditätsberatung","Der häufigste Schwerpunkt nach der Analyse"),
              ("/ratgeber/bwa-richtig-lesen.html","Die BWA richtig lesen","Was in der Auswertung steht und was fehlt"),
              ("/ratgeber/liquiditaetsplanung-13-wochen.html","Liquiditätsplanung über 13 Wochen","Anleitung zum Selbstaufbau")],
},
{
 "slug": "liquiditaetsberatung",
 "kategorie": "Leistung",
 "titel": "Liquiditätsberatung",
 "h1": "Liquiditätsberatung für den Mittelstand",
 "beschreibung": "Working Capital, Zahlungsziele und Cash-Reichweite: Wie Sie gebundenes Kapital freisetzen und Zahlungsengpässe vermeiden, bevor sie entstehen.",
 "lede": "Liquidität entscheidet, ob ein Unternehmen handlungsfähig bleibt. Sie hängt weniger vom Gewinn ab als davon, wie schnell Geld hereinkommt und wie langsam es abfließt.",
 "service": "Liquiditätsberatung und Working-Capital-Optimierung",
 "inhalt": '''
<h2>Gewinn und Liquidität sind zwei verschiedene Dinge</h2>
<p>Ein Betrieb kann einen Jahresgewinn von 80.000 Euro ausweisen und trotzdem im Februar die Löhne nicht zahlen können. Der Gewinn steht in der Erfolgsrechnung, das Geld steckt aber in unbezahlten Kundenrechnungen, im Lager und in angefangenen Arbeiten.</p>
<p>Diese Unterscheidung ist der Ausgangspunkt jeder Liquiditätsberatung. Wer sie nicht macht, sucht die Ursache an der falschen Stelle.</p>

<h2>Woran es typischerweise liegt</h2>
<p><strong>Zu lange Debitorenlaufzeit.</strong> Zwischen Leistung und Zahlungseingang vergehen 40, 50 oder mehr Tage. Jeder Tag bindet Geld, das dem Betrieb fehlt.</p>
<p><strong>Zu hoher Lagerbestand.</strong> Material, das eingekauft, aber nicht verbaut oder verkauft ist, ist gebundenes Kapital. Häufig liegt dort mehr, als der Betrieb vermutet.</p>
<p><strong>Ungenutzte Zahlungsziele auf der Einkaufsseite.</strong> Wer Lieferantenrechnungen sofort begleicht, obwohl 30 Tage vereinbart sind, verschenkt Spielraum.</p>
<p><strong>Fehlende Vorschau.</strong> Ohne Planung fällt ein Engpass erst auf, wenn er da ist. Dann bleiben nur teure Lösungen.</p>

<h2>Wie wir vorgehen</h2>
<ol>
  <li><strong>Messen.</strong> Wir berechnen Debitoren- und Kreditorenlaufzeit, Lagerreichweite und daraus den Geldumschlag: wie viele Tage Ihr Kapital gebunden ist, bevor es zurückkommt.</li>
  <li><strong>Vergleichen.</strong> Diese Werte setzen wir gegen branchenübliche Größen. Daraus ergibt sich, wo der größte Hebel liegt.</li>
  <li><strong>Umsetzen.</strong> Mahnwesen ordnen, Zahlungsziele neu verhandeln, Abschlagsrechnungen einführen, Lagerbestände abbauen. Meist reichen zwei bis drei Maßnahmen für einen spürbaren Effekt.</li>
  <li><strong>Planen.</strong> Zum Schluss steht eine rollierende Vorschau über 13 Wochen, mit der Sie Engpässe zwei Monate im Voraus sehen.</li>
</ol>

<h2>Was das bringt</h2>
<p>Ein Rechenbeispiel: Bei 600.000 Euro Jahresumsatz und einer Verkürzung der Debitorenlaufzeit von 45 auf 30 Tage bleiben rund 25.000 Euro dauerhaft im Betrieb. Ohne einen zusätzlichen Auftrag, ohne Kredit und ohne Preiserhöhung.</p>
''',
 "faq": [
   ("Ist das nicht Aufgabe meiner Bank?",
    "Die Bank stellt Kredite bereit, das kostet Zinsen. Wir setzen zuerst dort an, wo eigenes Geld im Betrieb gebunden ist. Erst wenn das ausgeschöpft ist, wird Fremdkapital zum Thema."),
   ("Wir haben schon ein Mahnwesen. Bringt das trotzdem etwas?",
    "Meistens ja. Entscheidend ist nicht, ob es ein Mahnwesen gibt, sondern ob es konsequent und zu festen Zeitpunkten läuft. Genau daran scheitert es im Alltag häufig."),
   ("Wie schnell wirken die Maßnahmen?",
    "Ein geordnetes Mahnwesen und schnellere Rechnungsstellung wirken innerhalb weniger Wochen. Lagerabbau und neu verhandelte Zahlungsziele brauchen ein bis zwei Quartale."),
   ("Verschlechtert das mein Verhältnis zu Kunden?",
    "Nach unserer Erfahrung nicht. Verlässliche Abläufe werden im Geschäftsverkehr als professionell wahrgenommen. Problematisch wird es eher, wenn Betriebe unregelmäßig und dann plötzlich hart mahnen."),
 ],
 "verwandt": [("/hilfe-bei-zahlungsschwierigkeiten.html","Hilfe bei Zahlungsschwierigkeiten","Wenn es bereits eng ist"),
              ("/ratgeber/liquiditaetsplanung-13-wochen.html","Liquiditätsplanung über 13 Wochen","So bauen Sie die Vorschau auf"),
              ("/ratgeber/agentur-geld-schneller-einnehmen.html","Geld schneller hereinbekommen","Beispiel Agenturgeschäft")],
},
{
 "slug": "hilfe-bei-zahlungsschwierigkeiten",
 "kategorie": "Leistung",
 "titel": "Hilfe bei Zahlungsschwierigkeiten",
 "h1": "Hilfe bei Zahlungsschwierigkeiten",
 "beschreibung": "Wenn im Unternehmen das Geld knapp wird: Sofortmaßnahmen, Bankgespräch und Liquiditätsplanung. Schnelle Erstberatung aus Leipzig.",
 "lede": "Wenn Rechnungen liegen bleiben und der Kontokorrent ausgereizt ist, zählt die Reihenfolge der Schritte. Wir verschaffen Ihnen zuerst Übersicht und dann Spielraum.",
 "service": "Beratung bei Liquiditätsengpässen",
 "inhalt": '''
<h2>Zuerst das Wichtigste</h2>
<p>Zwei Dinge sind keine Verhandlungssache, sondern gesetzlich geregelt.</p>
<p><strong>Sozialversicherungsbeiträge</strong> für Arbeitnehmer müssen abgeführt werden. Wer sie einbehält, macht sich nach § 266a StGB persönlich strafbar, unabhängig von der Rechtsform. Das ist der letzte Posten, an dem gespart werden darf.</p>
<p><strong>Die Insolvenzantragspflicht</strong> gilt für Kapitalgesellschaften: Bei Zahlungsunfähigkeit oder Überschuldung ist ohne schuldhaftes Zögern Antrag zu stellen, spätestens nach drei Wochen. Die Frist läuft ab Eintritt, nicht ab Kenntnis.</p>
<p>Wenn Sie in diesem Bereich unsicher sind, sprechen Sie mit einer Fachanwältin oder einem Fachanwalt für Insolvenzrecht. Wir sind Betriebswirte; unsere Arbeit endet dort, wo die rechtliche Bewertung beginnt. Vermitteln können wir den Kontakt.</p>

<h2>Was in den ersten Tagen zu tun ist</h2>
<ol>
  <li><strong>Überblick herstellen.</strong> Alle offenen Forderungen und Verbindlichkeiten mit Fälligkeit auflisten. Ohne diese Liste ist jede Entscheidung Raten.</li>
  <li><strong>Forderungen eintreiben.</strong> Die größten offenen Posten zuerst, telefonisch statt schriftlich. Erfahrungsgemäß steckt der Großteil des fehlenden Geldes in wenigen Rechnungen.</li>
  <li><strong>Alles Abrechenbare abrechnen.</strong> Fertige Leistungen sofort in Rechnung stellen, bei laufenden Projekten Abschläge prüfen.</li>
  <li><strong>Mit Gläubigern sprechen.</strong> Lieferanten und Vermieter reagieren auf ein offenes Gespräch fast immer besser als auf eine geplatzte Lastschrift.</li>
  <li><strong>Das Bankgespräch vorbereiten.</strong> Mit Liquiditätsplan und Auftragsbestand verhandeln Sie anders als ohne.</li>
</ol>

<h2>Wie wir dabei helfen</h2>
<p>Wir erstellen mit Ihnen kurzfristig eine Liquiditätsvorschau über 13 Wochen. Sie zeigt, wann es eng wird und wie groß die Lücke tatsächlich ist. Das ist die Grundlage für alles Weitere: für Priorisierung, für Verhandlungen und für das Gespräch mit der Bank.</p>
<p>Parallel prüfen wir, wo im Betrieb kurzfristig Geld freigesetzt werden kann. In den meisten Fällen findet sich mehr, als der Betrieb selbst vermutet.</p>
<p>Wenn sich abzeichnet, dass betriebswirtschaftliche Maßnahmen nicht ausreichen, sagen wir das deutlich und früh. Ein Sanierungsberater oder Fachanwalt gehört dann eingebunden, nicht erst in drei Monaten.</p>

<h2>Was Sie mitbringen sollten</h2>
<p>Für ein erstes Gespräch reichen die aktuelle BWA, eine Liste der offenen Posten und der Kontostand samt Kreditrahmen. Wenn diese Unterlagen nicht vollständig vorliegen, ist das kein Hindernis. Wir fangen mit dem an, was da ist.</p>
''',
 "faq": [
   ("Wie schnell können Sie reagieren?",
    "Bei akuten Engpässen bieten wir kurzfristige Termine an. Melden Sie sich telefonisch, dann finden wir meist innerhalb weniger Tage einen Termin."),
   ("Sind Sie eine Sanierungsberatung?",
    "Nein. Wir arbeiten betriebswirtschaftlich: Analyse, Liquiditätsplanung, Maßnahmen. Für Sanierungsgutachten und insolvenzrechtliche Fragen arbeiten wir mit spezialisierten Kanzleien zusammen."),
   ("Was kostet die Erstberatung?",
    "Das Erstgespräch ist kostenlos. Erst wenn Sie sich für eine Zusammenarbeit entscheiden, sprechen wir über Konditionen."),
   ("Erfährt meine Bank davon?",
    "Nur durch Sie. Wir treten nach außen nicht in Erscheinung, es sei denn, Sie wünschen ausdrücklich, dass wir Sie zu einem Bankgespräch begleiten."),
 ],
 "verwandt": [("/ratgeber/zahlungsschwierigkeiten-handwerk.html","Zahlungsschwierigkeiten im Handwerk","Die ersten Schritte im Detail"),
              ("/liquiditaetsberatung.html","Liquiditätsberatung","Damit es dauerhaft nicht wieder eng wird"),
              ("/financial-health-check.html","Financial Health Check","Die vollständige Bestandsaufnahme")],
},
]

def seite(s):
    url = f"https://valtixfm.de/{s['slug']}.html"
    graph = [
      {"@type":"Service","name":s["service"],"description":s["beschreibung"],
       "provider":{"@type":"ProfessionalService","name":"Valtix Financial Management",
                   "address":{"@type":"PostalAddress","streetAddress":"Straße des 18. Oktober 11",
                              "postalCode":"04103","addressLocality":"Leipzig","addressCountry":"DE"}},
       "areaServed":({"@type":"City","name":s["gebiet"]} if s.get("gebiet")
                     else {"@type":"Country","name":"Deutschland"}),"url":url},
      {"@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in s["faq"]]},
      {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Start","item":"https://valtixfm.de/"},
        {"@type":"ListItem","position":2,"name":s["titel"],"item":url}]},
    ]
    ld = {"@context":"https://schema.org","@graph":graph}
    faq_html = "\n".join(
      f'          <details>\n            <summary>{html.escape(q)}</summary>\n'
      f'            <p>{html.escape(a)}</p>\n          </details>' for q,a in s["faq"])
    verwandt_html = "\n".join(
      f'        <li><a href="{u}">{html.escape(t)}<span>{html.escape(d)}</span></a></li>'
      for u,t,d in s["verwandt"])
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(s["titel"])} | Valtix Financial Management</title>
<meta name="description" content="{html.escape(s["beschreibung"])}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#FBF8F2">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:title" content="{html.escape(s["titel"])} | Valtix Financial Management">
<meta property="og:description" content="{html.escape(s["beschreibung"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://valtixfm.de/assets/valtix-logo.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
<style>{SHARED_CSS}{EXTRA_CSS}</style>
</head>
<body>
{HEADER}

<main id="main">
  <p class="crumb"><a href="/">Start</a> › {html.escape(s["titel"])}</p>
  <article>
    <span class="tag">{html.escape(s["kategorie"])}</span>
    <h1>{html.escape(s["h1"])}</h1>
    <p class="lede">{html.escape(s["lede"])}</p>
    <div class="hero-cta">
      <a class="btn btn-primary btn-lg" href="/#kontakt">Kostenloses Erstgespräch
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
      </a>
      <a class="btn btn-glass btn-lg" href="tel:+4917622930394">+49 176 22930394</a>
    </div>

{s["inhalt"].strip()}

    <h2>Häufige Fragen</h2>
    <div class="faq">
{faq_html}
    </div>

    <div class="cta-box">
      <h2>Sprechen wir darüber</h2>
      <p>Im kostenlosen Erstgespräch klären wir in 30 Minuten, ob und wie wir Ihrem Unternehmen helfen können. Unverbindlich und vertraulich.</p>
      <a class="btn btn-cream btn-lg" href="/#kontakt">Erstgespräch vereinbaren
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
      </a>
    </div>

    <nav class="more" aria-label="Weiterführende Seiten">
      <h2>Passend dazu</h2>
      <ul>
{verwandt_html}
      </ul>
    </nav>
  </article>
</main>

{FOOTER}
</body>
</html>
'''

for s in SEITEN:
    with open(os.path.join(ROOT, s["slug"] + '.html'), 'w') as f:
        f.write(seite(s))
    print('Leistungsseite:', s["slug"])

# Sitemap komplett neu aufbauen
# Slugs direkt aus build_ratgeber.py lesen, damit die Liste nicht auseinanderlaeuft
_rg = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_ratgeber.py')).read()
_start = _rg.index('ARTIKEL = [')
_end = _rg.index('# ============================ TEMPLATES')
# Slug und Datum paarweise lesen, damit lastmod je Beitrag stimmt
# Je Beitrag den Block ab "slug" bis zum naechsten "slug" betrachten, damit
# Felder wie seo_titel zwischen slug und datum stehen duerfen
_bloecke = re.split(r'(?=\s"slug":)', _rg[_start:_end])
ratgeber = []
for _b in _bloecke:
    _s = re.search(r'"slug":\s*"([^"]+)"', _b)
    _d = re.search(r'"datum":\s*"([^"]+)"', _b)
    if _s and _d:
        ratgeber.append((_s.group(1), _d.group(1)))
assert ratgeber, 'Keine Ratgeber-Slugs mit Datum gefunden' 
# Der neueste Beitrag bestimmt, wann Startseite und Uebersicht zuletzt geaendert wurden
neuestes = max(d for _, d in ratgeber)
STAND = '2026-08-23'          # letzte inhaltliche Aenderung der Leistungsseiten
urls  = [('https://valtixfm.de/', '1.0', neuestes)]
urls += [(f'https://valtixfm.de/{s["slug"]}.html', '0.9', STAND) for s in SEITEN]
urls += [('https://valtixfm.de/ratgeber.html', '0.8', neuestes)]
urls += [(f'https://valtixfm.de/ratgeber/{r}.html', '0.7', d) for r, d in ratgeber]
entries = "\n".join(
    f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{lm}</lastmod>\n'
    f'    <changefreq>monthly</changefreq>\n    <priority>{p}</priority>\n  </url>'
    for u, p, lm in urls)
with open(os.path.join(ROOT,'sitemap.xml'),'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n')
print('Sitemap:', len(urls), 'Eintraege')
