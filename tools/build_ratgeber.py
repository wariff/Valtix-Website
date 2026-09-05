#!/usr/bin/env python3
"""Erzeugt die Ratgeber-Uebersicht und die einzelnen Artikelseiten."""
import os, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(ROOT, 'ratgeber'), exist_ok=True)

SHARED_CSS = '''
  @font-face{font-family:"Inter Tight";font-style:normal;font-weight:400;font-display:swap;src:url("/assets/fonts/inter-tight-latin-400-normal.woff2") format("woff2")}
  @font-face{font-family:"Inter Tight";font-style:normal;font-weight:500;font-display:swap;src:url("/assets/fonts/inter-tight-latin-500-normal.woff2") format("woff2")}
  @font-face{font-family:"Inter Tight";font-style:normal;font-weight:600;font-display:swap;src:url("/assets/fonts/inter-tight-latin-600-normal.woff2") format("woff2")}
  @font-face{font-family:"Inter Tight";font-style:normal;font-weight:800;font-display:swap;src:url("/assets/fonts/inter-tight-latin-800-normal.woff2") format("woff2")}
  :root{
    --ink:#232941;--ink-soft:#565D73;--navy:#232941;--navy-deep:#171B2C;
    --gold:#A6813F;--gold-deep:#7A6238;--cream:#F5EBD0;--bg:#FBF8F2;
    --glass:rgba(255,255,255,.62);--glass-border:rgba(255,255,255,.85);
    --glass-shadow:0 18px 50px rgba(35,41,65,.13);--hairline:rgba(35,41,65,.12);
    --font:"Inter Tight",system-ui,-apple-system,"Segoe UI",sans-serif;
    --r-pill:999px;--r-lg:22px;
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth;scroll-padding-top:100px}
  body{font-family:var(--font);background:var(--bg);color:var(--ink);font-size:16px;line-height:1.68;-webkit-font-smoothing:antialiased;overflow-x:hidden}
  img{max-width:100%;display:block}
  a{color:inherit}
  :focus-visible{outline:3px solid var(--navy);outline-offset:3px;border-radius:6px}
  .aurora{position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none}
  .aurora span{position:absolute;border-radius:50%;filter:blur(80px);opacity:.5}
  .a1{width:60vw;height:60vw;max-width:760px;max-height:760px;left:-16vw;top:-20vw;
      background:radial-gradient(circle,#F0E2C2 0%,rgba(240,226,194,0) 70%)}
  .a2{width:50vw;height:50vw;max-width:640px;max-height:640px;right:-14vw;top:-8vw;
      background:radial-gradient(circle,#D3D9E8 0%,rgba(211,217,232,0) 70%)}
  .glass{
    background:var(--glass);
    backdrop-filter:blur(22px) saturate(180%);-webkit-backdrop-filter:blur(22px) saturate(180%);
    border:1px solid var(--glass-border);
    box-shadow:var(--glass-shadow), inset 0 1px 0 rgba(255,255,255,.9);
  }
  @supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){
    .glass{background:rgba(255,255,255,.94)}
  }
  @media(prefers-reduced-transparency:reduce){
    .glass{background:#fff;backdrop-filter:none;-webkit-backdrop-filter:none}
  }
  .skip-link{position:absolute;left:-9999px;top:0;z-index:200;background:var(--navy);color:#fff;padding:12px 20px;font-weight:700;border-radius:0 0 10px 0}
  .skip-link:focus{left:0}
  .container{width:min(1180px,100% - 48px);margin-inline:auto}
  @media(max-width:767px){.container{width:calc(100% - 32px)}}
  .site-header{position:sticky;top:16px;z-index:100;margin-top:16px}
  @media(max-width:767px){.site-header{top:10px;margin-top:10px}}
  .nav{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:10px 10px 10px 22px;border-radius:var(--r-pill)}
  .brand{display:flex;align-items:center;min-height:44px}
  .brand img{height:26px;width:auto}
  .nav-links{display:flex;align-items:center;gap:2px;list-style:none}
  .nav-links a{display:inline-flex;align-items:center;min-height:44px;padding:0 16px;text-decoration:none;color:var(--ink-soft);font-weight:500;font-size:.94rem;border-radius:var(--r-pill);transition:color .2s ease,background .2s ease}
  .nav-links a:hover{color:var(--ink);background:rgba(255,255,255,.6)}
  .nav-links a.btn-primary,.nav-links a.btn-primary:hover{color:#fff;background:linear-gradient(180deg,var(--navy) 0%,var(--navy-deep) 100%)}
  @media(max-width:900px){.nav-links li:not(.nav-cta){display:none}}
  .btn{
    display:inline-flex;align-items:center;justify-content:center;gap:9px;
    min-height:46px;padding:0 22px;border-radius:var(--r-pill);
    font-family:var(--font);font-weight:600;font-size:.96rem;letter-spacing:-.01em;
    text-decoration:none;cursor:pointer;border:1px solid transparent;white-space:nowrap;
    transition:transform .2s ease,box-shadow .2s ease,background .2s ease;
  }
  .btn svg{flex:none}
  .btn-primary{background:linear-gradient(180deg,var(--navy) 0%,var(--navy-deep) 100%);color:#fff;
    box-shadow:0 8px 20px rgba(35,41,65,.32), inset 0 1px 0 rgba(255,255,255,.2)}
  .btn-primary:hover{transform:translateY(-2px)}
  .btn-cream{background:var(--cream);color:var(--navy);box-shadow:0 8px 20px rgba(0,0,0,.18)}
  .btn-cream:hover{transform:translateY(-2px);background:#FAF4E3}
  .btn-lg{min-height:54px;padding:0 30px;font-size:1.02rem}
  h1,h2,h3{font-weight:800;letter-spacing:-.032em;line-height:1.1;overflow-wrap:break-word}
  .site-footer{padding:40px 0 48px;border-top:1px solid var(--hairline);margin-top:40px}
  .footer-inner{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:18px}
  .footer-inner img{height:22px;width:auto;opacity:.85}
  .footer-links{display:flex;gap:4px;list-style:none;flex-wrap:wrap;margin:0}
  .footer-links li{margin:0}
  .footer-links a{display:inline-flex;align-items:center;min-height:44px;padding:0 11px;color:var(--ink-soft);text-decoration:none;font-size:.89rem}
  .footer-links a:hover{color:var(--ink)}
  .footer-standorte{flex-basis:100%;font-size:.84rem;color:var(--ink-soft)}
  .footer-standorte a{color:var(--gold-deep);font-weight:600;text-decoration:none}
  .footer-standorte a:hover{text-decoration:underline;text-underline-offset:3px}
  .footer-copy{font-size:.84rem;color:var(--ink-soft)}
  @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*::before,*::after{transition:none!important;animation:none!important}}
'''

HEADER = '''<a class="skip-link" href="#main">Zum Inhalt springen</a>
<div class="aurora" aria-hidden="true"><span class="a1"></span><span class="a2"></span></div>

<header class="site-header">
  <div class="container">
    <nav class="nav glass" aria-label="Hauptnavigation">
      <a class="brand" href="/" aria-label="Valtix, zur Startseite">
        <img src="/assets/valtix-logo-navy.png" alt="Valtix Financial Management" width="783" height="298">
      </a>
      <ul class="nav-links">
        <li><a href="/#leistungen">Leistungen</a></li>
        <li><a href="/#ablauf">Ablauf</a></li>
        <li><a href="/#pakete">Pakete</a></li>
        <li><a href="/ratgeber.html">Ratgeber</a></li>
        <li class="nav-cta"><a class="btn btn-primary" href="/#kontakt">Erstgespräch →</a></li>
      </ul>
    </nav>
  </div>
</header>'''

FOOTER = '''<footer class="site-footer">
  <div class="container footer-inner">
    <img src="/assets/valtix-logo-navy.png" alt="Valtix Financial Management" width="783" height="298">
    <ul class="footer-links">
      <li><a href="/#leistungen">Leistungen</a></li>
      <li><a href="/#ablauf">Ablauf</a></li>
      <li><a href="/#pakete">Pakete</a></li>
      <li><a href="/ratgeber.html">Ratgeber</a></li>
      <li><a href="/#kontakt">Kontakt</a></li>
      <li><a href="https://www.linkedin.com/company/valtixfm" rel="me noopener" target="_blank">LinkedIn</a></li>
      <li><a href="/impressum.html">Impressum</a></li>
      <li><a href="/datenschutz.html">Datenschutz</a></li>
    </ul>
    <p class="footer-standorte">Beratung vor Ort in <a href="/unternehmensberatung-leipzig.html">Leipzig</a>, <a href="/unternehmensberatung-ulm.html">Ulm</a> und <a href="/unternehmensberatung-mannheim.html">Mannheim</a></p>
    <p class="footer-copy">© 2026 Valtix Financial Management, Leipzig</p>
  </div>
</footer>'''

# Adresse des Brevo-Anmeldeformulars (Brevo: Kontakte > Formulare > Teilen > URL).
# Solange der Wert leer ist, wird der Newsletter-Baustein NICHT ausgegeben.
# Damit steht auf der Seite nie ein Formular, das ins Leere laeuft.
BREVO_FORM_URL = ""

def newsletter(kennung):
    """Anmeldeblock. Reiner Formular-POST, kein fremdes Skript, keine Cookies.
    Brevo uebernimmt Double-Opt-In und leitet danach auf /newsletter-danke.html."""
    if not BREVO_FORM_URL:
        return ""
    return f"""
    <section class="nl glass" aria-labelledby="nl-title-{kennung}">
      <h2 id="nl-title-{kennung}">Neue Beiträge per E-Mail</h2>
      <p class="nl-intro">Ein Beitrag pro Woche zu Kennzahlen, Liquidität und Ertrag im
        Mittelstand. Keine Werbung, keine Weitergabe Ihrer Adresse.</p>
      <form class="nl-form" action="{BREVO_FORM_URL}" method="POST">
        <input type="hidden" name="locale" value="de">
        <p class="nl-row">
          <label class="nl-label" for="nl-mail-{kennung}">E-Mail-Adresse</label>
          <input type="email" id="nl-mail-{kennung}" name="EMAIL" required
                 autocomplete="email" placeholder="ihre@firma.de">
          <button class="btn btn-primary" type="submit">Anmelden
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
          </button>
        </p>
        <label class="nl-consent">
          <input type="checkbox" name="OPT_IN" value="1" required>
          <span>Ich möchte den Valtix-Ratgeber per E-Mail erhalten. Die
            <a href="/datenschutz.html">Hinweise zum Datenschutz</a> habe ich gelesen.
            Die Einwilligung kann ich jederzeit über den Abmeldelink widerrufen.</span>
        </label>
        <input type="email" name="email_address_check" value="" class="gotcha"
               tabindex="-1" autocomplete="off" aria-hidden="true">
      </form>
      <p class="nl-fine">Sie erhalten zuerst eine E-Mail mit einem Bestätigungslink.
        Erst nach dem Klick sind Sie angemeldet.</p>
    </section>"""

NL_CSS = """
  /* ---------- Newsletter ---------- */
  .nl{margin:44px 0 0;padding:30px 28px;border-radius:var(--r-lg)}
  .nl h2{font-size:1.3rem;margin:0 0 8px}
  .nl-intro{color:var(--ink-soft);font-size:.95rem;margin-bottom:20px}
  .nl-row{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:16px}
  .nl-label{flex-basis:100%;font-size:.84rem;font-weight:600;margin-bottom:-2px}
  .nl-row input[type=email]{
    flex:1 1 240px;min-width:0;font-family:var(--font);font-size:.97rem;color:var(--ink);
    background:#fff;border:1px solid rgba(35,41,65,.22);border-radius:12px;
    padding:12px 14px;min-height:48px;transition:border-color .2s ease,box-shadow .2s ease}
  .nl-row input[type=email]:focus{outline:none;border-color:var(--navy);
    box-shadow:0 0 0 3px rgba(35,41,65,.14)}
  .nl-row .btn{flex:0 0 auto;min-height:48px}
  @media(max-width:520px){.nl-row .btn{flex:1 1 100%}}
  .nl-consent{display:flex;gap:11px;align-items:flex-start;
    font-size:.85rem;color:var(--ink-soft);cursor:pointer}
  .nl-consent input{flex:none;width:19px;height:19px;margin-top:2px;
    accent-color:var(--navy);cursor:pointer}
  .nl-consent a{color:var(--gold-deep);font-weight:600}
  .nl-fine{margin-top:16px;font-size:.8rem;color:var(--ink-soft)}
  .gotcha{position:absolute;left:-9999px;width:1px;height:1px;opacity:0}
"""

# ============================ ARTIKEL ============================
ARTIKEL = [
{
 "slug": "zahlungsschwierigkeiten-handwerk",
 "seo_titel": "Zahlungsschwierigkeiten im Handwerk: erste Schritte",
 "datum": "2026-08-21",
 "branche": "Handwerk & Bau",
 "titel": "Zahlungsschwierigkeiten im Handwerksbetrieb: die ersten Schritte",
 "beschreibung": "Wenn im Handwerksbetrieb das Geld knapp wird: welche Ursachen typisch sind, was in den ersten Tagen zu tun ist und wo die rechtlichen Grenzen liegen.",
 "anriss": "Volle Auftragsbücher und trotzdem kein Geld auf dem Konto. Warum das im Handwerk so häufig vorkommt und was sich kurzfristig ändern lässt.",
 "lesezeit": "6 Minuten",
 "inhalt": '''
<p class="lede">Ein Handwerksbetrieb kann ausgelastet sein, ordentliche Preise durchsetzen und trotzdem in Zahlungsschwierigkeiten geraten. Das klingt widersprüchlich, hat aber einen einfachen Grund: Auslastung und Liquidität sind zwei verschiedene Dinge. Wer Material einkauft, Löhne zahlt und erst Wochen später sein Geld sieht, finanziert seine Kunden vor.</p>

<h2>Woran es meistens liegt</h2>
<p>In den Betrieben, deren Zahlen wir sehen, wiederholen sich vier Muster.</p>
<p><strong>Material wird vorfinanziert.</strong> Der Großhandel will nach 14 Tagen sein Geld, der Kunde zahlt nach 30 Tagen ab Rechnung, und die Rechnung geht erst nach Abnahme raus. Zwischen Materialkauf und Zahlungseingang liegen dann schnell zehn Wochen.</p>
<p><strong>Abschlagsrechnungen werden nicht genutzt.</strong> Viele Betriebe schreiben eine Schlussrechnung, obwohl sie bei längeren Bauvorhaben regelmäßig Abschläge verlangen dürften. Das ist gesetzlich vorgesehen und im Baugewerbe üblich, wird aber aus Bequemlichkeit oder falscher Rücksicht oft weggelassen.</p>
<p><strong>Rechnungen gehen zu spät raus.</strong> Wenn die Büroarbeit am Wochenende erledigt wird, vergehen zwischen Fertigstellung und Rechnungsstellung leicht zwei Wochen. Diese Zeit fehlt hinten komplett.</p>
<p><strong>Das Mahnwesen läuft nicht.</strong> Ohne festen Ablauf bleibt die Zahlungserinnerung liegen, solange es irgendwie geht. Kunden merken das und zahlen zuletzt die Rechnungen, bei denen niemand nachfragt.</p>

<h2>Was in den ersten Tagen hilft</h2>
<p>Bei akuter Knappheit zählt Reihenfolge. Diese Schritte wirken am schnellsten:</p>
<ol>
  <li><strong>Offene Posten sortieren.</strong> Alle unbezahlten Rechnungen nach Alter und Betrag auflisten. Meist stecken 60 bis 70 Prozent des fehlenden Geldes in wenigen großen Positionen. Dort zuerst nachfassen, telefonisch, nicht schriftlich.</li>
  <li><strong>Fertige Leistungen sofort abrechnen.</strong> Alles, was abgenommen oder abnahmefähig ist, wird noch diese Woche in Rechnung gestellt. Bei laufenden Projekten prüfen, ob ein Abschlag möglich ist.</li>
  <li><strong>Mit dem Großhandel sprechen.</strong> Längere Zahlungsziele sind verhandelbar, besonders bei langjähriger Kundenbeziehung. Ein offenes Gespräch ist besser als eine geplatzte Lastschrift.</li>
  <li><strong>Bankgespräch vorbereiten, nicht abwarten.</strong> Wer mit einer Liquiditätsplanung und einer Auftragsliste zur Bank geht, verhandelt aus einer anderen Position als jemand, dessen Konto bereits überzogen ist.</li>
</ol>

<h2>Wo die rechtlichen Grenzen liegen</h2>
<p>Zwei Punkte sind keine Frage der Verhandlung, sondern des Gesetzes.</p>
<p>Sozialversicherungsbeiträge für Arbeitnehmer müssen abgeführt werden. Wer sie einbehält, macht sich nach § 266a StGB strafbar, und zwar persönlich, unabhängig von der Rechtsform des Betriebs. Das ist der letzte Posten, an dem gespart werden darf.</p>
<p>Bei Kapitalgesellschaften gilt außerdem die Insolvenzantragspflicht: Wer zahlungsunfähig oder überschuldet ist, muss ohne schuldhaftes Zögern Insolvenz anmelden, spätestens nach drei Wochen. Diese Frist läuft ab dem Zeitpunkt, an dem die Zahlungsunfähigkeit eintritt, nicht ab dem Tag, an dem man es bemerkt.</p>
<p>Wer in diesem Bereich unsicher ist, sollte mit einer Fachanwältin oder einem Fachanwalt für Insolvenzrecht sprechen. Wir sind Betriebswirte und keine Rechtsanwälte; unsere Aufgabe endet dort, wo die rechtliche Bewertung beginnt.</p>

<h2>Was danach kommt</h2>
<p>Die Sofortmaßnahmen verschaffen Luft, lösen aber nicht die Ursache. Nachhaltig wird es erst, wenn der Betrieb weiß, wie viel Geld in den nächsten Wochen ein- und ausgeht. Eine rollierende Planung über 13 Wochen reicht dafür meistens aus. Sie zeigt Engpässe zwei Monate im Voraus, und damit zu einem Zeitpunkt, an dem man noch handeln kann.</p>
'''
},
{
 "slug": "agentur-geld-schneller-einnehmen",
 "datum": "2026-08-21",
 "branche": "Agentur & Dienstleistung",
 "titel": "Agenturen: Wie Sie Ihr Geld schneller hereinbekommen",
 "beschreibung": "Projektgeschäft bindet Liquidität über Monate. Welche Abrechnungsmodelle Agenturen und Dienstleister vor Zahlungslücken schützen.",
 "anriss": "Das Projekt läuft vier Monate, die Rechnung kommt am Ende, die Gehälter jeden Monat. Wie sich diese Lücke schließen lässt.",
 "lesezeit": "5 Minuten",
 "inhalt": '''
<p class="lede">Agenturen und Dienstleister haben ein strukturelles Problem: Die Kosten fallen sofort an, der Umsatz kommt spät. Personal wird monatlich bezahlt, ein Projekt läuft aber über ein Quartal, und die Schlussrechnung wird nochmal 30 Tage später beglichen. Wer wächst, verschärft diese Lücke, weil mehr Projekte mehr Vorfinanzierung bedeuten.</p>

<h2>Der Denkfehler beim Wachstum</h2>
<p>Ein häufiges Missverständnis: Mehr Aufträge lösen das Liquiditätsproblem. Tatsächlich ist das Gegenteil der Fall. Jedes neue Projekt bindet zuerst Geld, bevor es welches bringt. Agenturen, die schnell wachsen, geraten deshalb regelmäßig in Engpässe, obwohl die Auftragslage und die Marge stimmen.</p>

<h2>Vier Stellschrauben</h2>
<p><strong>Anzahlung vereinbaren.</strong> Zwischen 30 und 50 Prozent bei Projektstart sind im Dienstleistungsgeschäft üblich und werden selten abgelehnt, wenn man sie selbstverständlich vorträgt. Wer erst am Ende abrechnet, tut es meist aus Gewohnheit, nicht weil der Markt es verlangt.</p>
<p><strong>Nach Meilensteinen abrechnen.</strong> Statt einer Schlussrechnung drei Teilrechnungen: bei Start, bei Zwischenabnahme, bei Abschluss. Das verkürzt die Vorfinanzierung deutlich und macht bei Streitigkeiten auch den Leistungsstand nachvollziehbar.</p>
<p><strong>Retainer statt Einzelprojekte.</strong> Ein monatlich abgerechnetes Betreuungspaket bringt planbare Einzahlungen und macht die Planung erheblich einfacher. Für Kunden hat es den Vorteil fester Kosten, für Sie den einer stabilen Grundauslastung.</p>
<p><strong>Zahlungsziel verkürzen.</strong> Viele Agenturen schreiben aus Gewohnheit 30 Tage auf die Rechnung. 14 Tage sind ebenso durchsetzbar, wenn sie im Angebot stehen und nicht erst auf der Rechnung auftauchen. Das allein verkürzt den Geldeingang um zwei Wochen.</p>

<h2>Wenn Kunden zu spät zahlen</h2>
<p>Ein festes Mahnwesen ist keine Unhöflichkeit, sondern Teil der Geschäftsbeziehung. Bewährt hat sich: Zahlungserinnerung am Tag nach Fälligkeit, Anruf nach einer Woche, förmliche Mahnung nach zwei Wochen. Entscheidend ist die Regelmäßigkeit. Kunden lernen sehr schnell, bei wem sie sich Verzögerungen erlauben können.</p>
<p>Ab dem Verzug dürfen Sie Verzugszinsen berechnen, im Geschäftsverkehr neun Prozentpunkte über dem Basiszinssatz, dazu eine Pauschale von 40 Euro. Das ist selten der große Hebel, zeigt aber, dass Sie den Vorgang verfolgen.</p>

<h2>Die Kennzahl, auf die es ankommt</h2>
<p>Rechnen Sie einmal aus, wie viele Tage im Schnitt zwischen Leistungserbringung und Zahlungseingang vergehen. Diese Zahl, in der Betriebswirtschaft Debitorenlaufzeit genannt, ist die wichtigste Größe für Ihre Liquidität. Wer sie von 45 auf 30 Tage senkt, hat bei 600.000 Euro Jahresumsatz rund 25.000 Euro mehr auf dem Konto, ohne einen einzigen Auftrag zusätzlich.</p>
'''
},
{
 "slug": "restaurant-ertrag-steigern",
 "datum": "2026-08-21",
 "branche": "Gastronomie",
 "titel": "Mehr verdienen im Restaurant: an welchen Zahlen es liegt",
 "beschreibung": "Wareneinsatz, Personalquote und Deckungsbeitrag je Gericht: die drei Größen, die über den Gewinn eines Restaurants entscheiden.",
 "anriss": "Volles Haus und trotzdem wenig übrig. Woran das liegt und welche drei Kennzahlen den Unterschied machen.",
 "lesezeit": "6 Minuten",
 "inhalt": '''
<p class="lede">In der Gastronomie entscheidet sich der Gewinn an wenigen Prozentpunkten. Zwei Betriebe mit gleichem Umsatz können bei einem am Jahresende 40.000 Euro Gewinn und beim anderen ein Minus ausweisen. Der Unterschied liegt fast immer in denselben drei Größen.</p>

<h2>Wareneinsatz</h2>
<p>Der Wareneinsatz beschreibt, wie viel Prozent des Umsatzes für Lebensmittel und Getränke draufgehen. In der Speisegastronomie liegen 28 bis 35 Prozent im üblichen Rahmen, bei Getränken deutlich darunter. Wer über 40 Prozent kommt, hat in aller Regel eines von drei Problemen: zu große Portionen, zu viel Verderb oder Einkaufspreise, die seit Monaten nicht geprüft wurden.</p>
<p>Rechnen Sie den Wareneinsatz monatlich aus, nicht jährlich. Bei einer jährlichen Betrachtung merken Sie eine Entwicklung erst, wenn ein ganzes Jahr gelaufen ist.</p>

<h2>Personalkosten</h2>
<p>Die zweite große Position liegt üblicherweise zwischen 30 und 35 Prozent vom Umsatz. Kritisch wird es weniger durch die Stundenlöhne als durch die Verteilung: Wenn zur schwachen Zeit dieselbe Besetzung im Haus ist wie zur Stoßzeit, entsteht bezahlte Leerlaufzeit.</p>
<p>Hilfreich ist eine einfache Auswertung, welcher Umsatz je Arbeitsstunde erwirtschaftet wird, getrennt nach Wochentagen und Tageszeiten. Häufig zeigt sich, dass ein Wochentag den Betrieb systematisch Geld kostet. Dann ist die Frage nicht, ob man Personal abbaut, sondern ob dieser Tag in der bisherigen Form Sinn ergibt.</p>

<h2>Deckungsbeitrag je Gericht</h2>
<p>Der wirkungsvollste und am seltensten genutzte Hebel. Rechnen Sie für jedes Gericht auf der Karte aus, was es im Einkauf kostet und was davon nach Abzug bleibt. Sortieren Sie die Karte anschließend in vier Gruppen:</p>
<ul>
  <li><strong>Wird oft bestellt, bringt viel:</strong> Ihre Gewinnbringer. Prominent auf der Karte platzieren.</li>
  <li><strong>Wird oft bestellt, bringt wenig:</strong> Portionsgröße, Rezeptur oder Preis prüfen. Kleine Anpassungen wirken hier am stärksten, weil die Menge stimmt.</li>
  <li><strong>Wird selten bestellt, bringt viel:</strong> Besser beschreiben, empfehlen lassen, hervorheben.</li>
  <li><strong>Wird selten bestellt, bringt wenig:</strong> Von der Karte nehmen. Diese Gerichte kosten Einkauf, Lagerplatz und Aufmerksamkeit in der Küche.</li>
</ul>
<p>Eine gestraffte Karte senkt gleichzeitig den Wareneinsatz, weil weniger Zutaten verderben.</p>

<h2>Was Preiserhöhungen wirklich bringen</h2>
<p>Viele Gastronomen scheuen Preisanpassungen aus Sorge vor Gästeverlust. Rechnen Sie es konkret durch: Bei einem Wareneinsatz von 30 Prozent bringt eine Preiserhöhung von fünf Prozent Ihnen fast den vollen Betrag als zusätzlichen Gewinn. Sie könnten dabei etwa jeden zwanzigsten Gast verlieren und stünden immer noch besser da als vorher.</p>
<p>Wichtig ist die Umsetzung: Nicht die ganze Karte gleichmäßig anheben, sondern gezielt dort, wo der Deckungsbeitrag zu niedrig ist, und bei den Gerichten, deren Preis Gäste am wenigsten im Kopf haben.</p>
'''
},
{
 "slug": "bwa-richtig-lesen",
 "seo_titel": "BWA richtig lesen: worauf Sie zuerst schauen",
 "datum": "2026-08-21",
 "branche": "Grundlagen",
 "titel": "Die BWA richtig lesen: worauf Geschäftsführer zuerst schauen",
 "beschreibung": "Was in der betriebswirtschaftlichen Auswertung steht, was fehlt und welche Positionen wirklich aussagekräftig sind.",
 "anriss": "Jeden Monat kommt sie vom Steuerberater, und meistens wandert sie ungelesen ab. Dabei stehen drei Dinge darin, die man kennen sollte.",
 "lesezeit": "5 Minuten",
 "inhalt": '''
<p class="lede">Die betriebswirtschaftliche Auswertung ist das am häufigsten erstellte und am seltensten gelesene Dokument im Mittelstand. Das liegt weniger am Desinteresse als an der Darstellung: Sie ist für die Buchhaltung gemacht, nicht für Entscheidungen.</p>

<h2>Was oben steht und was es bedeutet</h2>
<p>Die ersten Zeilen zeigen die Umsatzerlöse des Monats und im Vergleich den Wert des Vorjahreszeitraums. Interessant ist selten der absolute Betrag, sondern die Abweichung. Wenn der Umsatz gegenüber dem Vorjahresmonat um zehn Prozent gestiegen ist, die Materialkosten aber um zwanzig, dann arbeitet der Betrieb trotz Wachstum schlechter.</p>
<p>Direkt darunter folgt der Materialaufwand oder Wareneinsatz. Setzen Sie diesen ins Verhältnis zum Umsatz und beobachten Sie diese Quote über mehrere Monate. Eine schleichende Verschlechterung um zwei bis drei Prozentpunkte fällt in absoluten Zahlen kaum auf, kostet über ein Jahr aber erhebliche Beträge.</p>
<p>Der Personalaufwand ist die dritte große Position. Auch hier ist die Quote aussagekräftiger als der Betrag, weil sie mit dem Umsatz mitwandert.</p>

<h2>Das vorläufige Ergebnis richtig einordnen</h2>
<p>Am Ende steht ein Ergebnis, das häufig für den Gewinn gehalten wird. Das ist es nicht. In der unterjährigen BWA fehlen typischerweise:</p>
<ul>
  <li>Abschreibungen, wenn sie nur einmal jährlich gebucht werden</li>
  <li>Bestandsveränderungen bei angefangenen Arbeiten</li>
  <li>Rückstellungen, etwa für Urlaub, Gewährleistung oder Steuernachzahlungen</li>
  <li>periodengerechte Abgrenzungen von Versicherungen oder Wartungsverträgen</li>
</ul>
<p>Deshalb weicht das Jahresergebnis oft deutlich von der Summe der zwölf Monatsauswertungen ab. Wer seine Entnahmen am vorläufigen Ergebnis ausrichtet, erlebt bei der Steuererklärung regelmäßig unangenehme Überraschungen.</p>

<h2>Was die BWA nicht zeigt</h2>
<p>Der wichtigste Punkt zum Schluss: Die BWA ist eine Erfolgsrechnung, keine Liquiditätsrechnung. Sie sagt nichts darüber, ob Sie nächsten Monat Ihre Rechnungen bezahlen können.</p>
<p>Ein Betrieb kann einen Gewinn von 20.000 Euro ausweisen und gleichzeitig zahlungsunfähig sein, weil das Geld in unbezahlten Kundenrechnungen und im Lager steckt. Umgekehrt kann ein Betrieb mit Verlust ausreichend flüssig sein, etwa weil hohe Abschreibungen das Ergebnis drücken, ohne Geld zu kosten.</p>
<p>Für die Frage, ob das Geld reicht, brauchen Sie eine getrennte Liquiditätsplanung. Die BWA beantwortet nur, ob Sie verdienen.</p>

<h2>Drei Fragen für jeden Monat</h2>
<p>Wenn Sie sich zehn Minuten Zeit nehmen wollen, reichen diese drei Fragen:</p>
<ol>
  <li>Wie hat sich meine Materialquote gegenüber den Vormonaten entwickelt?</li>
  <li>Wie meine Personalquote?</li>
  <li>Welche Position weicht am stärksten vom Vorjahr ab, und weiß ich, warum?</li>
</ol>
<p>Wer diese drei Zahlen im Blick behält, erkennt Fehlentwicklungen Monate früher als jemand, der auf den Jahresabschluss wartet.</p>
'''
},
{
 "slug": "liquiditaetsplanung-13-wochen",
 "datum": "2026-08-21",
 "branche": "Grundlagen",
 "titel": "Liquiditätsplanung über 13 Wochen: eine Anleitung",
 "beschreibung": "Wie eine rollierende Liquiditätsplanung aufgebaut wird, warum 13 Wochen der richtige Zeitraum sind und welche Posten hineingehören. Mit Vorlage zum Nachbauen.",
 "anriss": "Das wirksamste Instrument gegen Zahlungsengpässe passt auf eine Tabellenseite. So bauen Sie es auf.",
 "lesezeit": "5 Minuten",
 "inhalt": '''
<p class="lede">Die meisten Liquiditätsengpässe kommen nicht überraschend. Sie kündigen sich Wochen vorher an, nur schaut niemand hin. Eine rollierende Planung über 13 Wochen ist das einfachste Mittel dagegen und kommt mit einer Tabellenkalkulation aus.</p>

<h2>Warum 13 Wochen</h2>
<p>Der Zeitraum entspricht einem Quartal und ist lang genug, um Handlungsspielraum zu lassen. Wer sieht, dass in Woche neun das Konto ins Minus läuft, hat zwei Monate Zeit für Gegenmaßnahmen: Rechnungen früher stellen, mit der Bank sprechen, eine Investition verschieben. Bei einer Vorschau über vier Wochen bleibt für all das keine Zeit mehr.</p>
<p>Gleichzeitig ist der Zeitraum kurz genug, dass die Zahlen belastbar sind. Was in acht Monaten passiert, weiß niemand genau.</p>

<h2>Der Aufbau</h2>
<p>Sie brauchen eine Tabelle mit 13 Spalten, eine je Kalenderwoche. Die Zeilen gliedern sich in drei Blöcke.</p>
<p><strong>Anfangsbestand.</strong> Der tatsächliche Kontostand zu Wochenbeginn, inklusive genutztem Kontokorrentrahmen. Nicht der Wert aus der Buchhaltung, sondern der reale Stand.</p>
<p><strong>Einzahlungen.</strong> Erwartete Zahlungseingänge, aufgeteilt nach Herkunft: Zahlungen aus offenen Rechnungen, Zahlungen aus Aufträgen, die noch abgerechnet werden, sonstige Eingänge wie Steuererstattungen. Wichtig ist das erwartete Zahlungsdatum, nicht das Rechnungsdatum. Wenn ein Kunde erfahrungsgemäß nach 40 Tagen zahlt, planen Sie 40 Tage.</p>
<p><strong>Auszahlungen.</strong> Löhne und Gehälter mit ihren festen Terminen, Sozialversicherung, Lohnsteuer, Umsatzsteuer, Miete, Leasing, Tilgung, Material, Versicherungen. Die meisten dieser Posten sind bekannt und wiederkehrend, was die Planung erheblich vereinfacht.</p>
<p>Am Ende jeder Spalte steht der Endbestand, der zugleich der Anfangsbestand der Folgewoche ist.</p>

<h2>Rollierend heißt: jede Woche fortschreiben</h2>
<p>Einmal aufgestellt und dann liegengelassen bringt eine solche Planung nichts. Der Nutzen entsteht durch die wöchentliche Aktualisierung: Die abgelaufene Woche wird durch die tatsächlichen Zahlen ersetzt, hinten kommt eine neue Woche dazu. Das dauert nach etwas Übung eine Viertelstunde.</p>
<p>Der Vergleich zwischen Plan und Ist ist dabei genauso wichtig wie die Vorschau. Wer merkt, dass die Zahlungseingänge regelmäßig eine Woche später kommen als geplant, kennt seine Kunden danach besser und plant genauer.</p>

<h2>Typische Fehler</h2>
<ul>
  <li><strong>Zu optimistisch bei Eingängen.</strong> Planen Sie mit dem Zahlungsverhalten, das Ihre Kunden tatsächlich zeigen, nicht mit dem vereinbarten Zahlungsziel.</li>
  <li><strong>Umsatzsteuer vergessen.</strong> Sie ist ein durchlaufender Posten, verlässt das Konto aber zu festen Terminen und reißt bei knapper Lage Löcher.</li>
  <li><strong>Nur Summen statt Termine.</strong> Ob eine Zahlung am 3. oder am 28. fällig wird, entscheidet über den Engpass. Monatssummen verdecken genau das.</li>
  <li><strong>Keine Reserve.</strong> Planen Sie einen Puffer ein. Eine defekte Maschine oder ein ausgefallener Kunde gehören zum Geschäft.</li>
</ul>
'''
},
{
 "slug": "kundenerlebnis-schuhgeschaeft",
 "seo_titel": "Kundenerlebnis im Einzelhandel messbar machen",
 "datum": "2026-08-23",
 "branche": "Einzelhandel",
 "titel": "Kundenerlebnis im Schuhgeschäft: was davon in den Zahlen ankommt",
 "beschreibung": "Wie stationäre Schuhhändler mit Beratung gegen den Onlinehandel bestehen und an welchen Kennzahlen sich guter Kundenumgang ablesen lässt.",
 "anriss": "Gegen Preis und Sortiment im Netz kommt kein Laden an. Gegen Beratung im Netz kommt kein Shop an. Wie sich das rechnet.",
 "lesezeit": "7 Minuten",
 "inhalt": '''
<p class="lede">Ein Schuhgeschäft konkurriert mit Anbietern, die größere Auswahl haben, günstiger sind und rund um die Uhr geöffnet. Bei Preis und Sortiment ist dieser Wettbewerb verloren, bevor er beginnt. Es gibt aber etwas, das ein Onlineshop nicht kann: einen Fuß ansehen, ihn vermessen und daraus eine Empfehlung ableiten, die passt.</p>
<p>Genau darin liegt der Hebel. Und er ist messbar, wie jeder andere Geschäftsvorgang auch.</p>

<h2>Die ersten dreißig Sekunden</h2>
<p>Wer einen Laden betritt, entscheidet sehr schnell, ob er bleibt. Der häufigste Fehler ist die Frage „Kann ich Ihnen helfen?“, direkt an der Tür gestellt. Sie erzeugt fast automatisch die Antwort „Ich schaue nur“, und damit ist das Gespräch für die nächste halbe Stunde beendet.</p>
<p>Besser funktioniert eine offene Begrüßung ohne Verkaufsabsicht, ein Nicken oder ein kurzes „Guten Tag“, verbunden mit dem Hinweis, dass man da ist, wenn etwas gebraucht wird. Danach lässt man den Kunden ankommen. Der richtige Zeitpunkt für die Ansprache ist erkennbar: Sobald jemand ein Paar länger in der Hand hält, sich nach der Größe umsieht oder zweimal zum selben Regal zurückkehrt, ist die Frage willkommen. Nicht vorher.</p>
<p>Diese Zurückhaltung ist keine Bequemlichkeit, sondern Handwerk. Sie erhöht die Zahl der Gespräche, die tatsächlich zustande kommen.</p>

<h2>Beratung, die online nicht möglich ist</h2>
<p>Der stärkste Grund, überhaupt in ein Schuhgeschäft zu gehen, ist die Passform. Rund zwei Drittel der Menschen tragen Schuhe in der falschen Größe, oft weil sich der Fuß über die Jahre verändert hat und die alte Zahl im Kopf geblieben ist.</p>
<p>Wer den Fuß tatsächlich vermisst, also Länge und Breite, im Stehen und am besten nachmittags, wenn er etwas geschwollen ist, liefert einen Nutzen, den kein Paketversand ersetzt. Das dauert drei Minuten und verändert das Gespräch grundlegend: Aus einem Verkäufer wird jemand, der etwas weiß.</p>
<p>Dazu gehören die Fragen, die sich aus dem Gebrauch ergeben. Wofür sind die Schuhe? Wie lange wird darin gestanden oder gelaufen? Gibt es Beschwerden, Einlagen, eine bekannte Fehlstellung? Wer das erfragt, empfiehlt anders und verkauft am Ende häufig ein anderes Paar als das, nach dem gefragt wurde. Wenn es passt, kommt der Kunde wieder.</p>

<h2>Zusatzverkauf, der nicht aufdringlich wirkt</h2>
<p>Pflegemittel, Einlagen und passende Socken gehören zu den Positionen mit der höchsten Marge. Verkauft werden sie am besten nicht als Angebot, sondern als Bestandteil der Beratung: Ein Lederschuh, der nicht imprägniert wird, hält eine Saison; mit Pflege hält er drei. Das ist eine sachliche Information, keine Verkaufsmasche, und wird auch so aufgenommen.</p>
<p>Entscheidend ist der Zeitpunkt. Der Hinweis gehört an die Anprobe, während der Kunde den Schuh am Fuß hat, nicht an die Kasse. An der Kasse wirkt dasselbe Argument wie ein Aufschlag.</p>

<h2>Was nach dem Kauf passiert</h2>
<p>Die meisten Geschäfte hören auf, sobald bezahlt wurde. Dabei entscheidet sich hier, ob aus einem Käufer ein Stammkunde wird.</p>
<p>Wirksam und mit wenig Aufwand verbunden sind drei Dinge: eine klare Aussage zum Umtausch, die nicht kleingedruckt ist, sondern ausgesprochen wird. Ein Reparaturservice oder wenigstens die Adresse eines guten Schusters. Und die Bereitschaft, ein Paar zurückzunehmen, das nach zwei Tagen doch drückt, ohne dass daraus eine Diskussion wird.</p>
<p>Der letzte Punkt kostet gelegentlich eine Marge und bringt regelmäßig einen Kunden, der wiederkommt und weitererzählt. Im Einzelhandel ist Weiterempfehlung die günstigste Form der Werbung, die es gibt.</p>

<h2>Woran sich das ablesen lässt</h2>
<p>Kundenerlebnis klingt weich, schlägt sich aber in vier Kennzahlen nieder, die jeder Laden erheben kann.</p>
<p><strong>Abschlussquote.</strong> Wie viele Besucher kaufen tatsächlich? Im Schuheinzelhandel liegen 20 bis 35 Prozent im üblichen Rahmen. Wer die Zahl kennt, erkennt sofort, ob eine Änderung an der Ansprache wirkt. Ein einfacher Zähler an der Tür genügt für den Anfang.</p>
<p><strong>Artikel pro Bon.</strong> Die Zahl der verkauften Teile je Kassenvorgang. Sie zeigt, ob Zusatzverkauf stattfindet. Steigt sie von 1,2 auf 1,5, bedeutet das bei gleicher Kundenzahl deutlich mehr Umsatz, ohne einen zusätzlichen Besucher.</p>
<p><strong>Durchschnittsbon.</strong> Der Umsatz je Kassenvorgang. Er reagiert auf Beratungsqualität, weil gut beratene Kunden eher zum passenden statt zum billigsten Paar greifen.</p>
<p><strong>Wiederkaufrate.</strong> Wie viele Kunden kommen innerhalb eines Jahres erneut? Diese Zahl ist am schwersten zu erheben und am aussagekräftigsten. Schon eine einfache Kundenkarte oder eine Notiz im Kassensystem reicht, um sie näherungsweise zu bestimmen.</p>

<h2>Der Zusammenhang, auf den es ankommt</h2>
<p>Diese vier Größen erklären gemeinsam, warum zwei Läden mit vergleichbarer Lage und Sortiment völlig unterschiedliche Ergebnisse erzielen. Wer die Abschlussquote um fünf Prozentpunkte hebt und gleichzeitig die Artikel pro Bon leicht steigert, verändert den Jahresumsatz erheblich, ohne mehr Miete zu zahlen oder mehr Werbung zu schalten.</p>
<p>Deshalb lohnt es sich, guten Kundenumgang nicht als Frage der Persönlichkeit zu behandeln, sondern als Arbeitsprozess mit messbarem Ergebnis. Was gemessen wird, lässt sich verbessern.</p>
'''
},
{
 "slug": "stundensatz-richtig-kalkulieren",
 "datum": "2026-08-23",
 "branche": "Handwerk & Dienstleistung",
 "titel": "Stundensatz kalkulieren: warum 60 Euro oft nicht reichen",
 "beschreibung": "Wie ein tragfähiger Stundenverrechnungssatz entsteht: Personalkosten, produktive Stunden und Gemeinkostenzuschlag, mit vollem Rechenbeispiel.",
 "anriss": "Die meisten Betriebe rechnen ihren Stundensatz zu niedrig, weil sie mit den falschen Stunden rechnen. Eine Beispielkalkulation Schritt für Schritt.",
 "lesezeit": "7 Minuten",
 "inhalt": '''
<p class="lede">Der Stundensatz ist die meistunterschätzte Zahl im Handwerk und in vielen Dienstleistungsbetrieben. Er wird selten sauber berechnet, sondern am Wettbewerb abgelesen oder über Jahre fortgeschrieben. Das Ergebnis ist ein Betrieb, der ausgelastet ist, jede Rechnung bezahlt bekommt und am Jahresende trotzdem kaum etwas übrig hat.</p>

<h2>Der Denkfehler steckt in den Stunden</h2>
<p>Fast alle Fehlkalkulationen gehen auf denselben Punkt zurück: Es wird mit den bezahlten Stunden gerechnet statt mit den verrechenbaren. Ein Mitarbeiter mit 40-Stunden-Vertrag kostet 52 Wochen im Jahr Geld, steht aber nicht 2.080 Stunden auf der Baustelle. Urlaub, Feiertage, Krankheit, Fahrzeiten, Rüstzeiten, Lagerarbeit und Werkzeugpflege gehen ab. Wer diese Differenz nicht einrechnet, verteilt seine Kosten auf zu viele Stunden und kommt dadurch auf einen zu niedrigen Satz.</p>

<h2>Schritt 1: die echten Personalkosten</h2>
<p>Nehmen wir einen Gesellen mit 3.400 Euro Bruttolohn im Monat.</p>
<ul>
  <li>Bruttolohn: 40.800 Euro im Jahr</li>
  <li>Arbeitgeberanteil zur Sozialversicherung, rund 21 Prozent: 8.570 Euro</li>
  <li>Urlaubs- und Weihnachtsgeld, Berufskleidung, Fortbildung, Berufsgenossenschaft: rund 3.000 Euro</li>
</ul>
<p>Zusammen also etwa <strong>52.400 Euro pro Jahr</strong>. Der Bruttolohn allein unterzeichnet die tatsächlichen Kosten um knapp 30 Prozent.</p>

<h2>Schritt 2: die verrechenbaren Stunden</h2>
<p>Von den 2.080 vertraglichen Stunden bleiben nach Abzug von 30 Urlaubstagen, rund zehn Feiertagen und durchschnittlich zehn Krankheitstagen etwa 1.680 Anwesenheitsstunden übrig.</p>
<p>Davon ist wiederum nicht alles am Kunden verrechenbar. Fahrten zur Baustelle, Materialabholung, Aufräumen, Reparaturen am eigenen Fuhrpark und Absprachen im Betrieb sind notwendig, stehen aber auf keiner Rechnung. Je nach Gewerk sind 70 bis 80 Prozent produktive Zeit realistisch. Bei 75 Prozent bleiben <strong>1.260 verrechenbare Stunden</strong>.</p>
<p>Daraus ergeben sich Personalkosten von 52.400 geteilt durch 1.260, also <strong>41,60 Euro je verrechenbarer Stunde</strong>. Und darin steckt noch kein Cent für Miete, Fahrzeug oder Büro.</p>

<h2>Schritt 3: die Gemeinkosten</h2>
<p>Jetzt kommt alles dazu, was der Betrieb unabhängig vom einzelnen Auftrag kostet. Für einen Betrieb mit vier Gesellen sieht das oft so aus:</p>
<ul>
  <li>Miete Werkstatt und Lager, Nebenkosten: 24.000 Euro</li>
  <li>Fahrzeuge inklusive Leasing, Sprit, Versicherung, Wartung: 32.000 Euro</li>
  <li>Werkzeug, Maschinen, Abschreibungen: 18.000 Euro</li>
  <li>Versicherungen, Beiträge, Software, Telefon: 12.000 Euro</li>
  <li>Buchhaltung, Steuerberatung, Bürokraft: 26.000 Euro</li>
  <li>Unternehmerlohn für die Betriebsleitung: 68.000 Euro</li>
</ul>
<p>In Summe 180.000 Euro. Verteilt auf vier Gesellen mit je 1.260 verrechenbaren Stunden, also 5.040 Stunden, sind das <strong>35,70 Euro je Stunde</strong>.</p>
<p>Der Unternehmerlohn ist dabei kein Luxusposten. Wer selbst mitarbeitet, den Betrieb führt, Angebote schreibt und Kunden betreut, muss davon leben. Wird diese Position weggelassen, sieht die Kalkulation gesund aus, während die Inhaberfamilie faktisch unbezahlt arbeitet.</p>

<h2>Schritt 4: Selbstkosten und Zuschlag</h2>
<p>41,60 Euro Personalkosten plus 35,70 Euro Gemeinkosten ergeben <strong>77,30 Euro Selbstkosten</strong> je verrechenbarer Stunde. Bei diesem Satz macht der Betrieb weder Gewinn noch Verlust.</p>
<p>Darauf gehört ein Zuschlag für Gewinn und Wagnis. Er deckt Gewährleistungsfälle, Forderungsausfälle, Investitionen und die Rücklage für schlechte Jahre. Zehn Prozent sind die Untergrenze, üblich sind zehn bis fünfzehn. Mit zehn Prozent liegt der Stundenverrechnungssatz bei rund <strong>85 Euro netto</strong>.</p>
<p>Wer in diesem Beispiel 60 Euro abrechnet, verkauft jede Stunde mit 17 Euro Verlust. Bei 5.000 verrechneten Stunden im Jahr sind das 85.000 Euro, die im Ergebnis fehlen. Genau das ist der Grund, warum ausgelastete Betriebe in Zahlungsschwierigkeiten geraten.</p>

<h2>Wenn der Marktpreis darunter liegt</h2>
<p>Der häufigste Einwand lautet: Das zahlt hier niemand. Manchmal stimmt das. Dann ist die Kalkulation trotzdem nicht falsch, sondern liefert die Information, dass das Geschäftsmodell in dieser Form nicht trägt. Drei Wege führen aus dieser Lage.</p>
<p><strong>Produktivität erhöhen.</strong> Steigen die verrechenbaren Stunden von 75 auf 80 Prozent, sinken die Selbstkosten im Beispiel um rund fünf Euro. Bessere Tourenplanung, Material am Vorabend kommissioniert und weniger Fahrten zwischen Baustelle und Lager wirken hier unmittelbar.</p>
<p><strong>Gemeinkosten prüfen.</strong> Nicht jeder Posten ist fix. Fuhrpark, Versicherungen und Softwareverträge werden oft jahrelang nicht angefasst.</p>
<p><strong>Aufträge auswählen.</strong> Wer weiß, was ihn eine Stunde kostet, erkennt auch, welche Aufträge sich nicht lohnen. Einen unrentablen Auftrag abzulehnen verbessert das Ergebnis sofort, weil die eigene Zeit dann in besser bezahlte Arbeit fließt.</p>

<h2>Wie oft nachrechnen</h2>
<p>Einmal im Jahr, am besten zusammen mit dem Jahresabschluss, und zusätzlich immer dann, wenn sich Löhne, Miete oder Fahrzeugkosten spürbar verändern. Ein Stundensatz, der drei Jahre unverändert steht, ist bei den Kostensteigerungen der letzten Jahre praktisch sicher zu niedrig.</p>
'''
},
{
 "slug": "preiserhoehung-durchsetzen",
 "datum": "2026-08-23",
 "branche": "Alle Branchen",
 "titel": "Preise erhöhen, ohne Kunden zu verlieren",
 "beschreibung": "Wie viel Umsatz eine Preiserhöhung verkraftet, wann der richtige Zeitpunkt ist und wie die Ankündigung formuliert wird, ohne sich zu rechtfertigen.",
 "anriss": "Die Angst vor der Preiserhöhung kostet mehr Geld als die Preiserhöhung selbst. Eine einfache Rechnung zeigt, wie viel Spielraum tatsächlich da ist.",
 "lesezeit": "6 Minuten",
 "inhalt": '''
<p class="lede">Kaum eine Entscheidung wird so lange aufgeschoben wie die Preiserhöhung. Der Grund ist immer derselbe: die Sorge, Kunden zu verlieren. Was dabei fast nie ausgerechnet wird, ist die andere Seite. Wie viele Kunden dürfte man eigentlich verlieren, bevor sich die Erhöhung nicht mehr lohnt? Diese Zahl ist meist deutlich größer, als alle im Betrieb vermuten.</p>

<h2>Was Warten kostet</h2>
<p>Ein Betrieb mit acht Prozent Umsatzrendite gibt 92 Cent von jedem Euro wieder aus. Steigen die Kosten um drei Prozent und die Preise bleiben gleich, sinkt der Gewinn nicht um drei Prozent, sondern um mehr als ein Drittel. Bei 500.000 Euro Umsatz schrumpft das Ergebnis von 40.000 auf rund 26.000 Euro.</p>
<p>Deshalb wirkt eine verschobene Preisanpassung so unauffällig und richtet trotzdem so viel Schaden an. Der Umsatz bleibt stabil, die Auslastung stimmt, nur unten bleibt immer weniger übrig. In der BWA sieht man das erst nach Monaten.</p>

<h2>Wie viel Umsatz die Erhöhung verkraftet</h2>
<p>Die entscheidende Größe ist die Deckungsbeitragsquote, also der Anteil des Umsatzes, der nach Abzug der variablen Kosten übrig bleibt. Bei einem Handwerksbetrieb mit hohem Materialanteil liegt sie vielleicht bei 40 Prozent, bei einer Beratung oder Agentur eher bei 70.</p>
<p>Die Rechnung dazu ist einfach:</p>
<p><strong>Zulässiger Mengenverlust = Preiserhöhung geteilt durch (Deckungsbeitragsquote plus Preiserhöhung)</strong></p>
<p>Ein Beispiel mit 40 Prozent Deckungsbeitragsquote und fünf Prozent Preiserhöhung: 5 geteilt durch 45 ergibt 11,1 Prozent. Sie könnten also gut ein Zehntel Ihres Absatzes verlieren und stünden beim Gewinn genauso da wie vorher. Bei 70 Prozent Deckungsbeitragsquote sind es immer noch 6,7 Prozent.</p>
<p>In der Praxis verliert kaum ein Betrieb nach einer moderaten, angekündigten Preiserhöhung zehn Prozent seiner Kunden. Üblich sind ein bis drei Prozent, und das sind meist genau die Kunden, die ohnehin am wenigsten Deckungsbeitrag gebracht haben.</p>

<h2>Nicht alle gleich behandeln</h2>
<p>Eine pauschale Erhöhung über alle Kunden und alle Leistungen ist die einfachste, aber selten die beste Lösung. Sortieren Sie vorher.</p>
<p><strong>Alte Verträge zuerst.</strong> Kunden, deren Preis seit drei oder vier Jahren unverändert ist, subventionieren inzwischen alle anderen. Hier ist der Nachholbedarf am größten und die Begründung am leichtesten.</p>
<p><strong>Kleinaufträge stärker anheben.</strong> Der Aufwand für Angebot, Anfahrt und Abrechnung ist bei einem 300-Euro-Auftrag fast derselbe wie bei einem für 3.000 Euro. Eine Mindestpauschale oder ein höherer Satz für Kleinstaufträge korrigiert das, ohne die großen Kunden zu belasten.</p>
<p><strong>Leistungen trennen.</strong> Was heute kostenlos mitläuft, kann ein eigener Posten werden: Anfahrt, Expressbearbeitung, Zusatzschleifen, Wochenendtermine. Das ist psychologisch oft leichter durchzusetzen als ein höherer Grundpreis.</p>

<h2>Die Ankündigung</h2>
<p>Drei Dinge entscheiden darüber, wie die Nachricht ankommt.</p>
<p><strong>Vorlauf geben.</strong> Vier bis acht Wochen vor dem Stichtag, schriftlich, mit klarem Datum. Wer die Erhöhung erst auf der Rechnung entdeckt, reagiert verärgert, und zwar zu Recht.</p>
<p><strong>Kurz begründen, nicht rechtfertigen.</strong> Ein Satz zu gestiegenen Material- und Personalkosten genügt. Lange Erklärungen wirken wie eine Entschuldigung und laden zum Verhandeln ein. Legen Sie keine Kalkulation offen, das führt regelmäßig zu Diskussionen über einzelne Posten.</p>
<p><strong>Nichts gleichzeitig verschlechtern.</strong> Eine Preiserhöhung zusammen mit längeren Lieferzeiten oder gestrichenen Leistungen zu kommunizieren, ist die sicherste Methode, Kunden zu verlieren. Wenn Sie an Leistungen etwas ändern müssen, trennen Sie beides zeitlich.</p>

<h2>Wenn ein großer Kunde ablehnt</h2>
<p>Das kommt vor und ist kein Grund, die gesamte Erhöhung zurückzunehmen. Rechnen Sie den Kunden einzeln durch: Welcher Deckungsbeitrag bleibt zum alten Preis, welche Kapazität bindet er, und was könnten Sie mit dieser Kapazität sonst tun? Ein großer Kunde mit schwachem Deckungsbeitrag sieht in der Umsatzstatistik gut aus und ist im Ergebnis oft der teuerste.</p>
<p>Ein Zwischenweg funktioniert häufig: die Erhöhung für diesen Kunden in zwei Stufen über zwölf Monate, gegen eine längere Vertragsbindung oder ein kürzeres Zahlungsziel. Damit bekommen beide Seiten etwas.</p>

<h2>Danach messen</h2>
<p>Schauen Sie drei Monate später nicht auf den Umsatz, sondern auf den Deckungsbeitrag und die Anzahl der Kunden. Wenn der Umsatz leicht gesunken, der Deckungsbeitrag aber gestiegen ist, war die Erhöhung erfolgreich. Genau dieser Fall wird in Betrieben regelmäßig als Rückschlag missverstanden.</p>
'''
},
{
 "slug": "kontokorrent-dauerhaft-ausgeschoepft",
 "seo_titel": "Kontokorrent dauerhaft ausgeschöpft: was tun?",
 "datum": "2026-08-23",
 "branche": "Finanzierung",
 "titel": "Der Kontokorrent ist dauerhaft ausgeschöpft: was jetzt zu tun ist",
 "beschreibung": "Warum ein dauerhaft ausgereizter Kontokorrentkredit ein Warnsignal ist, was er wirklich kostet und wie sich die Finanzierung wieder in Ordnung bringen lässt.",
 "anriss": "Wenn die Kreditlinie seit Monaten nicht mehr ins Plus kommt, ist das kein Liquiditätsengpass mehr, sondern eine falsch aufgebaute Finanzierung.",
 "lesezeit": "6 Minuten",
 "inhalt": '''
<p class="lede">Der Kontokorrentkredit ist dafür gedacht, Schwankungen zu überbrücken. Material wird eingekauft, drei Wochen später zahlt der Kunde, dazwischen springt die Linie ein. Das Konto soll sich im Laufe eines Monats wieder ausgleichen. Wenn es das seit einem halben Jahr nicht mehr tut, hat sich unbemerkt etwas anderes gebildet: eine Dauerfinanzierung im teuersten verfügbaren Kredit.</p>

<h2>Der Bodensatz</h2>
<p>Banken nennen den Betrag, der die Linie nie verlässt, den Bodensatz. Er entsteht schleichend. Ein größerer Auftrag wird vorfinanziert, eine Steuernachzahlung kommt dazwischen, eine Maschine wird aus dem laufenden Konto bezahlt. Jedes Mal bleibt ein Rest.</p>
<p>Prüfen Sie das an Ihren Kontoauszügen der letzten zwölf Monate: Was war der höchste Kontostand in jedem Monat? Wenn dieser Wert nie über null lag, kennen Sie Ihren Bodensatz und wissen, welcher Teil Ihrer Finanzierung in Wahrheit langfristig ist.</p>

<h2>Was das kostet</h2>
<p>Kontokorrentzinsen liegen je nach Bank und Bonität deutlich über den Sätzen für ein Investitionsdarlehen. Bei einem Bodensatz von 80.000 Euro und einer Differenz von sechs Prozentpunkten sind das rund 4.800 Euro Zinsen pro Jahr, die allein durch die falsche Kreditart entstehen. Bei Überziehung der vereinbarten Linie kommt ein Überziehungszins obendrauf.</p>
<p>Das ist der kleinere Teil des Problems. Der größere ist, dass die Linie im Ernstfall nicht mehr zur Verfügung steht, weil sie bereits verbraucht ist. Genau dann, wenn eine unerwartete Rechnung kommt, ist der Puffer weg.</p>

<h2>Was die Bank sieht</h2>
<p>Die Kontoführung fließt in das Rating ein, und zwar stärker, als die meisten Unternehmer annehmen. Eine dauerhaft ausgeschöpfte Linie, häufige Überziehungen und zurückgegebene Lastschriften verschlechtern die Einstufung unmittelbar. Ein schlechteres Rating bedeutet höhere Zinsen und im nächsten Schritt eine zurückhaltendere Bank.</p>
<p>Wichtig zu wissen: Ein Kontokorrentkredit ist in aller Regel bis auf Weiteres eingeräumt und kann von der Bank gekündigt oder gekürzt werden. Das passiert selten aus heiterem Himmel, aber es passiert, und meist zum ungünstigsten Zeitpunkt. Auf eine Linie, die formal jederzeit widerrufbar ist, sollte keine Dauerfinanzierung aufgebaut sein.</p>

<h2>Drei Wege heraus</h2>
<p><strong>Umschulden.</strong> Der Bodensatz wird in ein Tilgungsdarlehen mit fester Laufzeit überführt, die Kontokorrentlinie bleibt daneben als Puffer bestehen. Das senkt die Zinsen, macht die Belastung planbar und gibt der Linie ihre eigentliche Funktion zurück. Banken sind dafür meist offen, weil ein getilgtes Darlehen für sie besser aussieht als eine ausgereizte Linie. Voraussetzung ist eine nachvollziehbare Planung.</p>
<p><strong>Gebundenes Kapital freisetzen.</strong> Oft steckt das fehlende Geld im eigenen Betrieb. Offene Kundenrechnungen, Lagerbestände und zu früh bezahlte Lieferantenrechnungen binden Liquidität. Wer die Debitorenlaufzeit um zwei Wochen senkt und das Lager um zehn Prozent reduziert, holt sich einen erheblichen Teil des Bodensatzes zurück, ohne mit der Bank zu sprechen.</p>
<p><strong>Die Ursache abstellen.</strong> Ein Bodensatz aus einer einmaligen Investition ist etwas anderes als einer, der jeden Monat wächst. Wächst er, deckt der Kredit laufende Verluste, und dann hilft keine Umschuldung, sondern nur eine Korrektur bei Preisen, Kosten oder Auftragsmix.</p>

<h2>Das Bankgespräch vorbereiten</h2>
<p>Wer mit einem Anliegen zur Bank geht, sollte drei Unterlagen dabei haben: die aktuelle BWA mit Vorjahresvergleich, eine Liquiditätsplanung über die nächsten zwölf Monate und eine kurze schriftliche Darstellung, wodurch der Bodensatz entstanden ist und was sich geändert hat.</p>
<p>Der Unterschied im Gespräch ist erheblich. Ein Unternehmer, der seine Zahlen erklären kann und von sich aus einen Vorschlag macht, verhandelt anders als jemand, der reagiert, nachdem die Bank sich gemeldet hat. Führen Sie das Gespräch, solange Sie noch Spielraum haben, nicht erst bei der ersten zurückgegebenen Lastschrift.</p>

<h2>Wenn es schon eng ist</h2>
<p>Bei akuter Zahlungsunfähigkeit reicht eine Finanzierungsumstellung nicht mehr aus. Dann gelten andere Regeln, insbesondere die Pflicht, Sozialversicherungsbeiträge weiter abzuführen, und bei Kapitalgesellschaften die Insolvenzantragspflicht mit ihren engen Fristen. Das ist eine rechtliche Frage und gehört zu einer Fachanwältin oder einem Fachanwalt für Insolvenzrecht. Wir sind Betriebswirte und bereiten in solchen Fällen die Zahlen auf, treffen aber keine rechtliche Bewertung.</p>
'''
},
{
 "slug": "import-export-ausserhalb-eu",
 "seo_titel": "Import aus Drittländern: Kosten und Liquidität",
 "datum": "2026-08-23",
 "branche": "Handel & Import",
 "titel": "Import und Export außerhalb der EU: was es mit Ihrer Liquidität macht",
 "beschreibung": "Landed Cost, Einfuhrumsatzsteuer, Incoterms und Währungsrisiko: welche Kosten beim Handel mit Drittländern nicht auf der Lieferantenrechnung stehen.",
 "anriss": "Der Einkaufspreis aus Fernost sieht unschlagbar aus. Bis Zoll, Fracht und Einfuhrumsatzsteuer dazukommen und das Geld vier Monate im Container steckt.",
 "lesezeit": "8 Minuten",
 "inhalt": '''
<p class="lede">Wer zum ersten Mal außerhalb der EU einkauft oder verkauft, unterschätzt fast immer dieselbe Sache. Nicht den Papierkram, den erledigt irgendwann ein Spediteur. Sondern die Zeit, in der das Geld weg ist, und die Kosten, die auf keiner Lieferantenrechnung stehen. Innerhalb der EU ist der Warenverkehr frei, es gibt keinen Zoll und die Umsatzsteuer läuft über das Reverse-Charge-Verfahren. Sobald eine Grenze zum Drittland dazwischenliegt, ändert sich beides.</p>

<h2>Die Geldbindung verlängert sich erheblich</h2>
<p>Nehmen wir einen Händler, der Ware in Asien einkauft. Der Ablauf sieht typischerweise so aus:</p>
<ul>
  <li>30 Prozent Anzahlung bei Auftragserteilung</li>
  <li>vier bis sechs Wochen Produktion</li>
  <li>Restzahlung gegen Kopie des Konnossements, also bei Verladung</li>
  <li>fünf bis sieben Wochen Seeweg nach Hamburg oder Rotterdam</li>
  <li>ein bis zwei Wochen Zollabfertigung und Nachlauf ins eigene Lager</li>
  <li>danach erst Verkauf, und der Kunde zahlt nach 30 Tagen</li>
</ul>
<p>Vom ersten Euro bis zum Zahlungseingang vergehen so leicht vier bis fünf Monate. Bei einem Wareneinsatz von 100.000 Euro pro Bestellung und drei Bestellungen im Jahr sind dauerhaft rund 120.000 Euro gebunden, die weder auf dem Konto noch in der Bilanz als Gewinn sichtbar sind.</p>
<p>Genau daran scheitern wachsende Importeure. Das Geschäft trägt sich rechnerisch, das Konto aber nicht. Wer die Bestellmengen erhöht, verschärft die Lücke, weil jede zusätzliche Bestellung zuerst Geld verbraucht.</p>

<h2>Was die Ware wirklich kostet</h2>
<p>Der Einkaufspreis ist selten der Preis. Die Größe, auf die es ankommt, heißt Landed Cost: alle Kosten bis zur eigenen Rampe. Eine Beispielrechnung für eine Sendung mit 4.000 Stück:</p>
<ul>
  <li>Warenwert ab Hafen Verschiffungsland: 40.000 Euro</li>
  <li>Seefracht: 2.800 Euro</li>
  <li>Transportversicherung: 200 Euro</li>
  <li>Zoll, hier 4,7 Prozent auf den Zollwert von 43.000 Euro: 2.020 Euro</li>
  <li>Nachlauf vom Hafen ins Lager: 600 Euro</li>
  <li>Terminalgebühren, Zollanmeldung, Verzollungsdienstleister: 450 Euro</li>
</ul>
<p>Summe: <strong>46.070 Euro</strong>. Der Stückpreis steigt damit von 10,00 auf 11,52 Euro, also um gut 15 Prozent. Wer mit dem reinen Einkaufspreis kalkuliert und darauf seine übliche Marge legt, verkauft die halbe Marge weg, ohne es zu merken.</p>
<p>Der Zollsatz hängt an der Warentarifnummer. Dieselbe Ware kann je nach Einreihung zwischen null und über zehn Prozent kosten. Bei einem Sortiment lohnt es sich, die tatsächlichen Sätze für die wichtigsten Artikel einmal sauber festzuhalten und in die Kalkulation zu übernehmen.</p>

<h2>Die Einfuhrumsatzsteuer ist kein Kostenfaktor, aber ein Liquiditätsfaktor</h2>
<p>Zusätzlich fallen 19 Prozent Einfuhrumsatzsteuer auf den Zollwert zuzüglich Zoll und Beförderungskosten bis zum Bestimmungsort an. Im Beispiel oben sind das rund 8.670 Euro.</p>
<p>Dieses Geld ist für einen vorsteuerabzugsberechtigten Betrieb kein Aufwand, es kommt über die Umsatzsteuervoranmeldung zurück. Bezahlen muss man es trotzdem zuerst, und zwischen Zahlung und Erstattung liegen je nach Meldezeitraum mehrere Wochen. Bei sechs Sendungen im Jahr sind das schnell 50.000 Euro, die permanent unterwegs sind.</p>
<p>Zwei Dinge entschärfen das. Ein Aufschubkonto beim Zoll verschiebt die Fälligkeit, statt bei jeder Abfertigung sofort zu zahlen. Für die Einfuhrumsatzsteuer gilt dabei eine eigene, längere Frist, die den Abstand zur Erstattung deutlich verkürzt. Ob sich das im Einzelfall lohnt und welche Sicherheiten der Zoll verlangt, klärt man mit dem Steuerberater und dem zuständigen Hauptzollamt.</p>

<h2>Incoterms entscheiden, wer wann zahlt</h2>
<p>Die Incoterms regeln, bis wohin der Verkäufer Kosten und Risiko trägt. Sie sind kein Formalismus, sondern verändern den Preis erheblich.</p>
<p><strong>EXW</strong> bedeutet, dass die Ware im Werk des Lieferanten bereitsteht und ab dort alles Ihre Sache ist, inklusive Ausfuhrabfertigung im Herkunftsland.</p>
<p><strong>FOB</strong> heißt, der Lieferant bringt die Ware an Bord des Schiffes, ab da tragen Sie Fracht und Risiko.</p>
<p><strong>CIF</strong> schließt Fracht und Versicherung bis zum Bestimmungshafen ein, aber nicht Zoll und Einfuhrabgaben.</p>
<p><strong>DDP</strong> bedeutet frei Haus verzollt, der Lieferant übernimmt alles.</p>
<p>Der teuerste Fehler beim Einkauf ist, Angebote mit unterschiedlichen Klauseln direkt zu vergleichen. Ein EXW-Preis von 9,20 Euro und ein DDP-Preis von 11,00 Euro sehen nach einer klaren Sache aus, bis die Fracht dazukommt. Verlangen Sie Angebote immer mit derselben Klausel, oder rechnen Sie alles auf Landed Cost um.</p>
<p>Wichtig ist außerdem der Gefahrübergang. Bei FOB liegt das Risiko für einen Wasserschaden auf See bei Ihnen, nicht beim Lieferanten. Ohne eigene Transportversicherung ist das ein offener Posten.</p>

<h2>Währungsrisiko</h2>
<p>Rechnungen in US-Dollar sind im Import die Regel. Zwischen Bestellung und Zahlung liegen oft drei Monate, und in dieser Zeit bewegt sich der Kurs.</p>
<p>Ein Beispiel: Eine Rechnung über 40.000 US-Dollar entspricht bei einem Kurs von 1,10 rund 36.360 Euro. Fällt der Kurs bis zur Zahlung auf 1,04, kostet dieselbe Rechnung 38.460 Euro. Die Differenz von 2.100 Euro ist bei einer Handelsspanne von zwölf Prozent fast die Hälfte des Rohertrags dieser Sendung.</p>
<p>Drei Wege, damit umzugehen. Der einfachste ist, in Euro zu verhandeln; viele Lieferanten machen das mit, verlangen dafür aber einen Aufschlag. Der zweite ist ein Devisentermingeschäft über die Hausbank, das den Kurs für den Zahlungszeitpunkt festschreibt. Der dritte ist eine natürliche Absicherung, wenn Sie selbst in Dollar fakturieren und Ein- und Auszahlungen sich teilweise ausgleichen.</p>
<p>Für kleinere Beträge ist der Aufwand oft nicht gerechtfertigt. Ab einem Volumen, bei dem eine Kursbewegung von fünf Prozent das Jahresergebnis spürbar verändert, gehört das Thema auf den Tisch.</p>

<h2>Export: erst die Zahlung sichern, dann liefern</h2>
<p>Beim Verkauf in Drittländer dreht sich das Problem um. Die Ware ist weg, und eine offene Forderung in einem Land ohne europäisches Mahnverfahren einzutreiben, ist teuer und langwierig.</p>
<p>Üblich sind vier Absicherungen, in absteigender Sicherheit: Vorkasse, Akkreditiv, Exportkreditversicherung und Zahlung gegen Dokumente. Ein Akkreditiv kostet Gebühren und verlangt formal exakte Papiere, gibt aber bei Neukunden in schwierigen Märkten die nötige Sicherheit. Bei wiederkehrenden Kunden mit guter Zahlungshistorie reicht meist eine Kreditversicherung.</p>
<p>Steuerlich ist die Ausfuhrlieferung in ein Drittland umsatzsteuerfrei. Diese Befreiung hängt allerdings am Nachweis, in der Regel am Ausgangsvermerk aus dem elektronischen Ausfuhrverfahren. Fehlt er bei einer Prüfung, wird die Lieferung nachträglich steuerpflichtig, und die Umsatzsteuer wird aus dem vereinbarten Betrag herausgerechnet. Bei einer Rechnung über 100.000 Euro sind das knapp 16.000 Euro, die nachträglich abzuführen sind und die beim Kunden meist nicht mehr einzutreiben sind. Die Ausfuhrnachweise gehören deshalb genauso systematisch abgelegt wie die Rechnungen selbst.</p>

<h2>Was sich in Kalkulation und Planung ändern muss</h2>
<p><strong>Landed Cost statt Einkaufspreis.</strong> Hinterlegen Sie für jeden Artikel den Vollkostensatz bis zur eigenen Rampe, nicht den Rechnungsbetrag des Lieferanten. Ohne das stimmt keine Margenrechnung.</p>
<p><strong>Liquiditätsplanung mit den richtigen Terminen.</strong> Anzahlung, Restzahlung, Zoll und Einfuhrumsatzsteuer fallen zu unterschiedlichen Zeitpunkten an und meist nicht dann, wenn die Buchhaltung sie erwartet. Eine rollierende Planung über 13 Wochen mit diesen Terminen zeigt den Engpass, bevor er entsteht.</p>
<p><strong>Lagerreichweite bewusst steuern.</strong> Lange Lieferzeiten zwingen zu größeren Beständen. Jede Woche zusätzliche Reichweite kostet gebundenes Kapital. Rechnen Sie einmal aus, was ein Monat Lagerbestand in Euro bedeutet, dann wird die Diskussion über Bestellmengen konkreter.</p>
<p><strong>Mindestbestellmengen gegen Kapitalbindung abwägen.</strong> Ein Rabatt von drei Prozent auf die doppelte Menge klingt gut, ist aber teuer, wenn die Ware acht Monate liegt und die Kontokorrentlinie dafür herhalten muss.</p>

<h2>Drei Fragen vor dem ersten Container</h2>
<ol>
  <li>Wie hoch ist die Landed Cost pro Stück, und trägt der geplante Verkaufspreis diese Kalkulation noch?</li>
  <li>Wie viel Geld ist wie lange gebunden, und reicht die vorhandene Liquidität für zwei parallel laufende Bestellungen?</li>
  <li>Was passiert, wenn die Sendung sich um vier Wochen verzögert oder der Kurs um fünf Prozent läuft?</li>
</ol>
<p>Wer diese drei Zahlen kennt, trifft die Entscheidung auf einer belastbaren Grundlage. Wer sie nicht kennt, erfährt sie sechs Monate später aus dem Kontoauszug.</p>

<h2>Wo unsere Arbeit endet</h2>
<p>Wir rechnen die betriebswirtschaftliche Seite: Landed Cost, Kapitalbindung, Liquiditätsplanung, Bestellpolitik und die Frage, ob das Geschäftsmodell die Finanzierung des Warenkreislaufs trägt.</p>
<p>Die zolltarifliche Einreihung einer Ware, Ursprungs- und Präferenzregeln, Ausfuhrgenehmigungen, Sanktions- und Embargofragen sowie die umsatzsteuerliche Beurteilung im Einzelfall gehören zu einer Zollberatung oder zum Steuerberater. Wir sind Betriebswirte und nehmen keine rechtliche Bewertung vor.</p>
'''
},
{
 "slug": "social-media-agentur-rentabilitaet",
 "seo_titel": "Social-Media-Agentur: welcher Kunde rechnet sich?",
 "datum": "2026-08-30",
 "branche": "Marketing & Social Media",
 "titel": "Social-Media-Agentur: welcher Kunde verdient wirklich Geld?",
 "beschreibung": "Auslastung, effektiver Stundensatz je Kunde und die Falle mit dem Mediabudget: die Kennzahlen, die in einer Social-Media-Agentur über den Gewinn entscheiden.",
 "anriss": "Das Team wächst, der Umsatz steigt, der Gewinn nicht. In Agenturen liegt das fast immer an zwei oder drei Kunden, die niemand nachgerechnet hat.",
 "lesezeit": "7 Minuten",
 "inhalt": '''
<p class="lede">Social-Media-Agenturen verkaufen Pakete und liefern Stunden. Im Angebot steht ein Retainer über 2.500 Euro im Monat für zwölf Posts, vier Reels und Community-Management. Was tatsächlich hineinfließt, weiß am Monatsende niemand genau. Genau in dieser Lücke verschwindet der Gewinn.</p>

<h2>Warum Umsatz hier fast nichts aussagt</h2>
<p>In einer Agentur ist Arbeitszeit die einzige nennenswerte Ressource. Ob ein Kunde rentabel ist, hängt deshalb nicht am Retainer, sondern am Verhältnis von Retainer zu geleisteten Stunden. Ein Kunde mit 4.000 Euro im Monat kann teurer sein als einer mit 1.800 Euro, wenn er dreimal so viel Zeit bindet.</p>
<p>Weil das ohne Zeiterfassung nicht sichtbar wird, wachsen viele Agenturen sich in die Verlustzone. Der große Kunde gilt als wichtig, bekommt Vorrang, und die kleinen rentablen Kunden werden nebenbei mitbedient.</p>

<h2>Kennzahl 1: Wie viele Stunden sind überhaupt verkaufbar</h2>
<p>Ein Vollzeitmitarbeiter hat 2.080 Vertragsstunden im Jahr. Nach 30 Urlaubstagen, zehn Feiertagen und durchschnittlich acht Krankheitstagen bleiben rund <strong>1.700 Anwesenheitsstunden</strong>.</p>
<p>Davon geht ab, was nicht auf einer Rechnung landet: interne Abstimmungen, Weiterbildung, Neukundengespräche, Angebote, Recherche, Toolpflege. In Agenturen sind 65 bis 75 Prozent abrechenbare Zeit ein realistischer Wert. Bei 70 Prozent bleiben <strong>1.187 verkaufbare Stunden im Jahr</strong>, also knapp 99 im Monat.</p>
<p>Wer intern mit 160 Stunden pro Monat und Kopf kalkuliert, rechnet also mit dem Sechzigfachen dessen, was tatsächlich zur Verfügung steht. Das ist der häufigste Kalkulationsfehler in der Branche.</p>

<h2>Kennzahl 2: Was eine Stunde kosten muss</h2>
<p>Rechnen wir eine Agentur mit fünf Personen durch.</p>
<ul>
  <li>Vollkosten je Mitarbeiter, also Bruttolohn plus Arbeitgeberanteile und Nebenkosten: 62.000 Euro im Jahr</li>
  <li>bei 1.187 abrechenbaren Stunden ergibt das <strong>52,20 Euro Personalkosten je verkaufbarer Stunde</strong></li>
  <li>Gemeinkosten für Büro, Software, Buchhaltung, Versicherungen und Geschäftsführung: 140.000 Euro im Jahr</li>
  <li>verteilt auf fünf mal 1.187 Stunden sind das weitere <strong>23,60 Euro</strong></li>
</ul>
<p>Die Selbstkosten liegen damit bei <strong>75,80 Euro je Stunde</strong>. Mit einem Zuschlag von 15 Prozent für Gewinn, Ausfälle und Rücklagen ergibt sich ein Zielstundensatz von rund <strong>87 Euro</strong>.</p>
<p>Diese eine Zahl braucht jede Agentur. Ohne sie lässt sich kein Angebot bewerten und keine Retainer-Verhandlung führen.</p>

<h2>Kennzahl 3: Der effektive Stundensatz je Kunde</h2>
<p>Jetzt wird es konkret. Retainer geteilt durch tatsächlich geleistete Stunden, Kunde für Kunde. Eine typische Auswertung sieht so aus:</p>
<div class="tbl-wrap">
<table>
  <thead>
    <tr><th>Kunde</th><th class="num">Retainer</th><th class="num">Stunden</th><th class="num">Effektiv</th><th class="num">Ergebnis im Jahr</th></tr>
  </thead>
  <tbody>
    <tr><td>Kunde A</td><td class="num">4.000 €</td><td class="num">61</td><td class="num">65,57 €</td><td class="num">−15.700 €</td></tr>
    <tr><td>Kunde B</td><td class="num">2.500 €</td><td class="num">24</td><td class="num">104,17 €</td><td class="num">+4.900 €</td></tr>
    <tr><td>Kunde C</td><td class="num">1.800 €</td><td class="num">15</td><td class="num">120,00 €</td><td class="num">+5.900 €</td></tr>
    <tr><td>Kunde D</td><td class="num">3.200 €</td><td class="num">47</td><td class="num">68,09 €</td><td class="num">−10.700 €</td></tr>
    <tr><td>Gesamt</td><td class="num">11.500 €</td><td class="num">147</td><td class="num">78,23 €</td><td class="num">−15.600 €</td></tr>
  </tbody>
</table>
</div>
<p class="tbl-hint">Die Tabelle lässt sich seitlich scrollen.</p>
<p>Die Spalte rechts zeigt, was der Kunde gegenüber dem Zielsatz von 87 Euro einbringt oder kostet. Kunde A, der größte Umsatzkunde, vernichtet fast 16.000 Euro im Jahr. Kunde C, den man wegen des kleinen Retainers kaum wahrnimmt, ist der profitabelste im Portfolio.</p>
<p>Der Durchschnitt liegt bei 78,23 Euro und damit über den Selbstkosten, aber deutlich unter dem Zielsatz. Die Agentur arbeitet also, ohne Rücklagen zu bilden. Das fällt erst auf, wenn ein Kunde abspringt oder eine Nachzahlung kommt.</p>

<h2>Warum Retainer mit der Zeit erodieren</h2>
<p>Kunde A war zu Beginn wahrscheinlich rentabel. Der Verfall passiert schleichend und immer nach demselben Muster.</p>
<p><strong>Die kurze Frage.</strong> Eine Nachricht bei WhatsApp, zehn Minuten Antwort, dazu der Kontextwechsel. Fünfmal die Woche ergibt vier Stunden im Monat, die niemand erfasst.</p>
<p><strong>Die zusätzliche Plattform.</strong> Erst Instagram, dann kam TikTok dazu, dann LinkedIn. Der Retainer blieb, wo er war.</p>
<p><strong>Das Formatwachstum.</strong> Aus Bildposts wurden Reels. Ein Reel kostet ein Vielfaches der Produktionszeit eines Bildposts. Im Vertrag steht weiterhin nur die Anzahl der Beiträge.</p>
<p><strong>Die Korrekturschleifen.</strong> Kunden mit unklaren Freigabeprozessen erzeugen drei bis fünf Runden statt einer. Das kostet mehr Zeit als die eigentliche Produktion.</p>
<p>Keiner dieser Punkte ist für sich groß genug, um darüber zu sprechen. Zusammen kippen sie das Ergebnis.</p>

<h2>Ohne Zeiterfassung geht es nicht</h2>
<p>Der übliche Einwand: Zeiterfassung passt nicht zur Kultur, das Team fühlt sich kontrolliert. Der Einwand ist ernst zu nehmen und lässt sich entkräften, wenn zwei Dinge klar sind.</p>
<p>Erstens geht es nicht um Leistungskontrolle einzelner Personen, sondern um die Frage, welcher Kunde wie viel Kapazität bindet. Zweitens reicht eine grobe Erfassung. Kunde und Tätigkeitsart in Viertelstundenschritten genügen vollkommen. Wer minutengenau erfassen lässt, bekommt schlechtere Daten, weil niemand mitmacht.</p>
<p>Nach zwei Monaten liegt ein belastbares Bild vor. Das ist der Zeitpunkt, an dem sich Verhandlungen führen lassen.</p>

<h2>Was mit unrentablen Kunden geschieht</h2>
<p>Drei Wege, in dieser Reihenfolge zu prüfen.</p>
<p><strong>Leistung an den Preis anpassen.</strong> Oft ist der Preis in Ordnung und der Leistungsumfang gewachsen. Ein sauber definierter Katalog, was im Retainer enthalten ist und was extra abgerechnet wird, löst das ohne Preisdiskussion.</p>
<p><strong>Preis an die Leistung anpassen.</strong> Bei Kunde A wären rund 5.300 Euro nötig, um den Zielsatz zu erreichen. Das ist eine große Erhöhung, lässt sich aber begründen, wenn man den gewachsenen Umfang gegenüberstellt. Zwei Stufen über zwölf Monate sind realistischer als ein Sprung.</p>
<p><strong>Trennen.</strong> Wenn beides scheitert, ist die Trennung die wirtschaftlich richtige Entscheidung. Die frei werdenden 61 Stunden im Monat entsprechen bei 87 Euro einem Gegenwert von gut 5.300 Euro. Diese Kapazität in Neukundengewinnung oder in bestehende rentable Kunden zu stecken, bringt mehr als der Umsatz, den man verliert.</p>

<h2>Die Falle mit dem Mediabudget</h2>
<p>Ein Punkt, der speziell Performance-orientierte Agenturen betrifft und in keiner BWA auffällt: das Werbebudget der Kunden, das über das eigene Konto läuft.</p>
<p>Die Plattformen ziehen das Geld sofort ein, meist über eine hinterlegte Kreditkarte. Der Kunde zahlt seine Rechnung 30 Tage später. Bei 60.000 Euro monatlichem Mediabudget finanziert eine Agentur mit vielleicht 50.000 Euro eigenem Monatsumsatz dauerhaft einen sechsstelligen Betrag vor, der ihr wirtschaftlich nicht gehört.</p>
<p>Zwei Risiken stecken darin. Das erste ist Liquidität: Die Kreditkartenlinie ist dauerhaft ausgereizt, und für eigene Investitionen bleibt nichts. Das zweite ist ein Ausfallrisiko in einer Größenordnung, die den Betrieb gefährden kann. Wird ein Kunde zahlungsunfähig, bleibt die Agentur auf dem verauslagten Werbebudget sitzen, ohne selbst eine Gegenleistung erhalten zu haben.</p>
<p>Sauber ist es, wenn Kunden ihre Werbekonten selbst führen und die Agentur nur Zugriff bekommt. Ist das nicht durchsetzbar, gehören Vorkasse für das Mediabudget oder eine Kreditversicherung dazu. Eine Regelung ohne Sicherheit sollte es ab einer gewissen Größenordnung nicht geben.</p>

<h2>Womit Sie anfangen</h2>
<ol>
  <li>Zielstundensatz einmal sauber ausrechnen, mit realistischen abrechenbaren Stunden.</li>
  <li>Zwei Monate grob Zeit erfassen, nach Kunde und Tätigkeitsart.</li>
  <li>Effektiven Stundensatz je Kunde ermitteln und gegen den Zielsatz stellen.</li>
  <li>Die zwei schwächsten Kunden angehen, entweder über den Leistungsumfang oder über den Preis.</li>
  <li>Prüfen, wie viel fremdes Mediabudget dauerhaft über das eigene Konto läuft.</li>
</ol>
<p>Diese fünf Schritte kosten wenige Stunden im Monat und verändern erfahrungsgemäß mehr am Ergebnis als jeder neue Kunde.</p>
'''
},
]

# ============================ HILFSFUNKTIONEN ============================
from datetime import datetime, timezone, timedelta

def de_datum(iso):
    """2026-08-30 -> 30. August 2026"""
    monate = ["Januar","Februar","März","April","Mai","Juni",
              "Juli","August","September","Oktober","November","Dezember"]
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d.day}. {monate[d.month-1]} {d.year}"

def rfc822(iso):
    """2026-08-30 -> Sun, 30 Aug 2026 09:00:00 +0200 (Format, das RSS verlangt)"""
    tage = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    mon  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    d = datetime.strptime(iso, "%Y-%m-%d").replace(
        hour=9, tzinfo=timezone(timedelta(hours=2)))
    return (f"{tage[d.weekday()]}, {d.day:02d} {mon[d.month-1]} {d.year} "
            f"09:00:00 +0200")

# ============================ TEMPLATES ============================
def artikel_seite(a):
    url = f"https://valtixfm.de/ratgeber/{a['slug']}.html"
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a["titel"],
        "description": a["beschreibung"],
        "author": {"@type": "Organization", "name": "Valtix Financial Management"},
        "publisher": {
            "@type": "Organization",
            "name": "Valtix Financial Management",
            "sameAs": ["https://www.linkedin.com/company/valtixfm"],
            "logo": {"@type": "ImageObject", "url": "https://valtixfm.de/assets/valtix-logo.png"},
        },
        "datePublished": a["datum"],
        "dateModified": a["datum"],
        "mainEntityOfPage": url,
        "inLanguage": "de-DE",
    }
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(a.get("seo_titel") or a["titel"])} | Valtix</title>
<meta name="description" content="{html.escape(a["beschreibung"])}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#FBF8F2">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:locale" content="de_DE">
<meta property="og:title" content="{html.escape(a["titel"])}">
<meta property="og:description" content="{html.escape(a["beschreibung"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://valtixfm.de/assets/valtix-logo.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="application/rss+xml" title="Valtix Ratgeber" href="/feed.xml">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
<style>{SHARED_CSS}
  main{{max-width:720px;margin-inline:auto;padding:48px 24px 24px}}
  .crumb{{font-size:.86rem;color:var(--ink-soft);margin-bottom:26px}}
  .crumb a{{text-decoration:none}}
  .crumb a:hover{{text-decoration:underline;text-underline-offset:3px}}
  .tag{{display:inline-block;font-size:.74rem;font-weight:700;letter-spacing:.1em;
        text-transform:uppercase;color:var(--gold-deep);background:rgba(166,129,63,.13);
        padding:5px 13px;border-radius:var(--r-pill);margin-bottom:18px}}
  article h1{{font-size:clamp(2rem,4.6vw,2.9rem);line-height:1.08;margin-bottom:14px}}
  .byline{{font-size:.88rem;color:var(--ink-soft);display:flex;gap:16px;flex-wrap:wrap;
           padding-bottom:26px;border-bottom:1px solid var(--hairline);margin-bottom:32px}}
  article .lede{{font-size:1.12rem;color:var(--ink-soft);margin-bottom:26px}}
  article h2{{font-size:1.5rem;margin:42px 0 12px}}
  article p{{margin-bottom:16px}}
  article ul,article ol{{margin:0 0 18px 22px}}
  article li{{margin-bottom:9px}}
  /* Tabellen scrollen in ihrem eigenen Kasten, damit die Seite nie quer laeuft */
  .tbl-wrap{{overflow-x:auto;margin:22px 0;-webkit-overflow-scrolling:touch}}
  article table{{border-collapse:collapse;width:100%;min-width:420px;font-size:.92rem}}
  article th,article td{{padding:10px 14px;text-align:left;white-space:nowrap;
    border-bottom:1px solid var(--hairline)}}
  article th{{font-weight:600;font-size:.78rem;text-transform:uppercase;
    letter-spacing:.06em;color:var(--ink-soft)}}
  article th.num,article td.num{{text-align:right}}
  article tbody tr:last-child td{{border-bottom:none;font-weight:600}}
  .tbl-hint{{font-size:.82rem;color:var(--ink-soft);margin:-12px 0 20px}}
  @media(min-width:700px){{.tbl-hint{{display:none}}}}
  article strong{{font-weight:600}}
  .cta-box{{margin:44px 0 0;padding:32px 30px;border-radius:var(--r-lg);color:#fff;
            background:linear-gradient(152deg,#2E3552 0%,#1A1F33 100%);
            box-shadow:0 24px 60px rgba(23,27,44,.28)}}
  .cta-box h2{{font-size:1.4rem;margin:0 0 10px;color:#fff}}
  .cta-box p{{color:rgba(255,255,255,.78);font-size:.97rem;margin-bottom:22px}}
  .more{{margin:52px 0 0;padding-top:26px;border-top:1px solid var(--hairline)}}
  .more h2{{font-size:1.15rem;margin:0 0 14px}}
  .more ul{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}}
  .more a{{text-decoration:none;font-weight:600;font-size:.97rem}}
  .more a:hover{{color:var(--gold-deep)}}
  .more span{{display:block;font-weight:400;font-size:.88rem;color:var(--ink-soft)}}
{NL_CSS}
</style>
</head>
<body>
{HEADER}

<main id="main">
  <p class="crumb"><a href="/">Start</a> › <a href="/ratgeber.html">Ratgeber</a> › {html.escape(a["branche"])}</p>
  <article>
    <span class="tag">{html.escape(a["branche"])}</span>
    <h1>{html.escape(a["titel"])}</h1>
    <p class="byline"><span>Valtix Financial Management</span><span><time datetime="{a["datum"]}">{de_datum(a["datum"])}</time></span><span>Lesezeit {a["lesezeit"]}</span></p>
    {a["inhalt"].strip()}

    <div class="cta-box">
      <h2>Wie steht Ihr Betrieb da?</h2>
      <p>Im Financial Health Check prüfen wir Ihre Kennzahlen und zeigen Ihnen, wo Liquidität gebunden ist. Das Erstgespräch ist kostenlos und unverbindlich.</p>
      <a class="btn btn-cream btn-lg" href="/#kontakt">Erstgespräch vereinbaren
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
      </a>
    </div>

{newsletter(a["slug"])}

    <nav class="more" aria-label="Weitere Beiträge">
      <h2>Weitere Beiträge</h2>
      <ul>
{{MORE}}
      </ul>
    </nav>
  </article>
</main>

{FOOTER}
</body>
</html>
'''

def uebersicht():
    url = "https://valtixfm.de/ratgeber.html"
    ld_uebersicht = json.dumps({"@context":"https://schema.org","@graph":[
        {"@type":"Blog","@id":url,"name":"Valtix Ratgeber","url":url,
         "description":"Beiträge zu Liquidität, Kennzahlen und Ertrag im Mittelstand.",
         "inLanguage":"de-DE",
         "publisher":{"@type":"Organization","name":"Valtix Financial Management",
                      "url":"https://valtixfm.de/",
                      "sameAs":["https://www.linkedin.com/company/valtixfm"],
                      "logo":{"@type":"ImageObject",
                              "url":"https://valtixfm.de/assets/valtix-logo.png"}},
         "blogPost":[{"@type":"BlogPosting",
                      "headline":a["titel"],
                      "description":a["beschreibung"],
                      "datePublished":a["datum"],
                      "url":f"https://valtixfm.de/ratgeber/{a['slug']}.html"}
                     for a in sorted(ARTIKEL, key=lambda x: x["datum"], reverse=True)]},
        {"@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Start","item":"https://valtixfm.de/"},
            {"@type":"ListItem","position":2,"name":"Ratgeber","item":url}]},
    ]}, ensure_ascii=False, indent=2)
    karten = []
    for a in ARTIKEL:
        karten.append(f'''        <article class="post glass">
          <span class="tag">{html.escape(a["branche"])}</span>
          <h2><a href="/ratgeber/{a["slug"]}.html">{html.escape(a["titel"])}</a></h2>
          <p>{html.escape(a["anriss"])}</p>
          <p class="read">Lesezeit {a["lesezeit"]}</p>
        </article>''')
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ratgeber für Unternehmer | Valtix Financial Management</title>
<meta name="description" content="Praxisnahe Beiträge zu Liquidität, Kennzahlen und Ertrag: für Handwerk, Gastronomie, Agenturen und den Mittelstand aus Leipzig.">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#FBF8F2">
<link rel="canonical" href="https://valtixfm.de/ratgeber.html">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:title" content="Ratgeber für Unternehmer | Valtix Financial Management">
<meta property="og:description" content="Praxisnahe Beiträge zu Liquidität, Kennzahlen und Ertrag für den Mittelstand.">
<meta property="og:url" content="https://valtixfm.de/ratgeber.html">
<meta property="og:image" content="https://valtixfm.de/assets/valtix-logo.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="application/rss+xml" title="Valtix Ratgeber" href="/feed.xml">
<script type="application/ld+json">
{ld_uebersicht}
</script>
<style>{SHARED_CSS}
  main{{max-width:1180px;margin-inline:auto;padding:56px 24px 20px;width:calc(100% - 48px)}}
  @media(max-width:767px){{main{{width:calc(100% - 32px);padding:40px 0 12px}}}}
  .head{{max-width:640px;margin-bottom:46px}}
  .head h1{{font-size:clamp(2.2rem,5.4vw,3.4rem);margin-bottom:14px}}
  .head p{{color:var(--ink-soft);font-size:1.1rem}}
  .posts{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}
  @media(max-width:820px){{.posts{{grid-template-columns:1fr}}}}
  .post{{border-radius:var(--r-lg);padding:28px 26px;display:flex;flex-direction:column;
         transition:transform .26s ease,box-shadow .26s ease}}
  .post:hover{{transform:translateY(-4px);box-shadow:0 26px 60px rgba(35,41,65,.16), inset 0 1px 0 rgba(255,255,255,.9)}}
  .tag{{display:inline-block;align-self:flex-start;font-size:.72rem;font-weight:700;letter-spacing:.1em;
        text-transform:uppercase;color:var(--gold-deep);background:rgba(166,129,63,.13);
        padding:5px 12px;border-radius:var(--r-pill);margin-bottom:15px}}
  .post h2{{font-size:1.28rem;line-height:1.22;margin-bottom:10px}}
  .post h2 a{{text-decoration:none}}
  .post h2 a:hover{{color:var(--gold-deep)}}
  .post p{{color:var(--ink-soft);font-size:.95rem;margin-bottom:14px}}
  .post .read{{margin-top:auto;margin-bottom:0;font-size:.84rem;color:var(--ink-soft);opacity:.85}}
  .note{{margin:40px 0 0;padding:20px 24px;border-radius:16px;font-size:.9rem;color:var(--gold-deep);
         background:rgba(166,129,63,.1);border:1px dashed rgba(166,129,63,.5)}}
</style>
</head>
<body>
{HEADER}

<main id="main">
  <div class="head">
    <h1>Ratgeber</h1>
    <p>Was wir in Beratungsgesprächen immer wieder erklären, hier zum Nachlesen. Praxisnah, nach Branchen sortiert und ohne Fachchinesisch.</p>
  </div>

  <div class="posts">
{chr(10).join(karten)}
  </div>

  <p class="note">Der Ratgeber wird laufend erweitert. Sie vermissen ein Thema? Schreiben Sie uns, wir greifen Fragen aus der Praxis gerne auf.</p>
</main>

{FOOTER}
</body>
</html>
'''

# ============================ SCHREIBEN ============================
for a in ARTIKEL:
    others = [x for x in ARTIKEL if x["slug"] != a["slug"]][:3]
    more = "\n".join(
        f'        <li><a href="/ratgeber/{o["slug"]}.html">{html.escape(o["titel"])}'
        f'<span>{html.escape(o["branche"])}</span></a></li>' for o in others)
    page = artikel_seite(a).replace("{MORE}", more)
    with open(os.path.join(ROOT, 'ratgeber', a["slug"] + '.html'), 'w') as f:
        f.write(page)
    print('Artikel:', a["slug"])

with open(os.path.join(ROOT, 'ratgeber.html'), 'w') as f:
    f.write(uebersicht())
print('Uebersicht: ratgeber.html')

# ============================ RSS-FEED ============================
# Reihenfolge: neueste Beitraege zuerst
feed_artikel = sorted(ARTIKEL, key=lambda a: a["datum"], reverse=True)
items = "\n".join(f"""  <item>
    <title>{html.escape(a["titel"])}</title>
    <link>https://valtixfm.de/ratgeber/{a["slug"]}.html</link>
    <guid isPermaLink="true">https://valtixfm.de/ratgeber/{a["slug"]}.html</guid>
    <pubDate>{rfc822(a["datum"])}</pubDate>
    <category>{html.escape(a["branche"])}</category>
    <description>{html.escape(a["beschreibung"])}</description>
  </item>""" for a in feed_artikel)

with open(os.path.join(ROOT, 'feed.xml'), 'w') as f:
    f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Valtix Ratgeber</title>
  <link>https://valtixfm.de/ratgeber.html</link>
  <atom:link href="https://valtixfm.de/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Beiträge zu Kennzahlen, Liquidität und Ertrag im Mittelstand von Valtix Financial Management, Leipzig.</description>
  <language>de-DE</language>
  <lastBuildDate>{rfc822(feed_artikel[0]["datum"])}</lastBuildDate>
{items}
</channel>
</rss>
""")
print('Feed:    ', len(feed_artikel), 'Beitraege')

# Sitemap neu aufbauen
urls = ['https://valtixfm.de/', 'https://valtixfm.de/ratgeber.html'] + \
       [f'https://valtixfm.de/ratgeber/{a["slug"]}.html' for a in ARTIKEL]
entries = "\n".join(
    f'  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-08-20</lastmod>\n'
    f'    <changefreq>monthly</changefreq>\n    <priority>{"1.0" if u.endswith("de/") else "0.8"}</priority>\n  </url>'
    for u in urls)
with open(os.path.join(ROOT, 'sitemap.xml'), 'w') as f:
    f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n')
print('Sitemap: ', len(urls), 'Eintraege')
