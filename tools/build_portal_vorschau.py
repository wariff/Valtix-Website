# -*- coding: utf-8 -*-
"""Baut die statische Portalvorschau.

Reine Attrappe zur Ansicht: kein Server, keine Datenbank, keine Speicherung.
Die Zahlen stammen aus der Beispieldatei, die Firma ist erfunden.

Der Aufbau folgt dem, was Auswertungswerkzeuge wie finban vormachen:
Seitenleiste links, Werkzeugleiste oben, darunter Kennzahlen, ein Verlauf
ueber alle Monate und ein aufklappbares Raster mit den Monaten als Spalten.
Die Farben sind die von Valtix, nicht die des Vorbilds.
"""
import math
import os
import re
import sys

_HIER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_HIER)
sys.path.insert(0, os.path.join(_HIER, 'bericht'))
from matrix import Matrix                                    # noqa: E402

QUELLE = os.environ.get('VALTIX_DEMO', '/tmp/demo.xlsx')
BERICHT = 'portal-vorschau-bericht.html'

M = Matrix(QUELLE)
KURZ = {'Januar': 'Jan', 'Februar': 'Feb', 'März': 'Mär', 'April': 'Apr',
        'Mai': 'Mai', 'Juni': 'Jun', 'Juli': 'Jul', 'August': 'Aug',
        'September': 'Sep', 'Oktober': 'Okt', 'November': 'Nov',
        'Dezember': 'Dez'}


# ------------------------------------------------------------------- Formate
def geld(w, nachkomma=0):
    if w is None:
        return '–'
    s = f'{w:,.{nachkomma}f}'.replace(',', '@').replace('.', ',').replace('@', '.')
    return s + ' €'


def prozent(w):
    return '–' if w is None else f'{w:,.1f}'.replace('.', ',') + ' %'


def zahl(w):
    if w is None:
        return '–'
    nk = 0 if abs(w - round(w)) < 0.005 else 1
    return f'{w:,.{nk}f}'.replace(',', '@').replace('.', ',').replace('@', '.')


def tage(w):
    return '–' if w is None else f'{w:,.0f}'.replace(',', '.') + ' Tage'


def formatiere(art, w):
    return {'geld': geld, 'prozent': prozent, 'zahl': zahl, 'tage': tage}[art](w)


# ---------------------------------------------------------------- Diagramme
def sparkline(werte, breite=46, hoehe=18):
    """Winziger Verlauf am Zeilenanfang, wie im Vorbild."""
    echte = [w for w in werte if w is not None]
    if len(echte) < 2:
        return f'<svg width="{breite}" height="{hoehe}" aria-hidden="true"></svg>'
    tief, hoch = min(echte), max(echte)
    spanne = (hoch - tief) or 1
    schritt = breite / (len(werte) - 1)
    punkte = []
    for i, w in enumerate(werte):
        if w is None:
            continue
        y = hoehe - 2 - (w - tief) / spanne * (hoehe - 4)
        punkte.append(f'{i * schritt:.1f},{y:.1f}')
    letzte = punkte[-1].split(',')
    return (f'<svg width="{breite}" height="{hoehe}" viewBox="0 0 {breite} {hoehe}" '
            f'aria-hidden="true" class="funke">'
            f'<polyline points="{" ".join(punkte)}" fill="none" stroke="currentColor" '
            f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{letzte[0]}" cy="{letzte[1]}" r="1.9" fill="currentColor"/></svg>')


def _runde_obergrenze(wert, stufen=4):
    """Achsen sollen bei glatten Betraegen enden, nicht bei 411.492 Euro."""
    grob = wert / stufen
    zehner = 10 ** math.floor(math.log10(grob))
    for faktor in (1, 2, 2.5, 5, 10):
        if faktor * zehner >= grob:
            return faktor * zehner * stufen
    return grob * stufen


def verlaufsbild():
    """Saeulen je Monat fuer Gesamtleistung und Gesamtkosten, dazu die
    liquiden Mittel als Linie. Der Berichtsmonat ist hinterlegt."""
    gesamt = M.zeile('gesamtleistung').werte
    kosten = [M.zeile('variabel').werte[i] + M.zeile('fix').werte[i]
              + (M.zeile('afa').werte[i] if M.zeile('afa') else 0)
              for i in range(len(M.monate))]
    liq_zeile = M.zeile('liquide')
    liquide = liq_zeile.werte if liq_zeile else []

    B, H = 1000, 250
    links, rechts, oben, unten = 74, 18, 18, 34
    flaeche_b = B - links - rechts
    flaeche_h = H - oben - unten
    roh = max(gesamt + kosten + [w for w in liquide if w is not None] + [1]) * 1.08
    hoch = _runde_obergrenze(roh)
    spalte = flaeche_b / len(M.monate)
    balken = min(26, spalte * 0.3)

    teile = [f'<svg viewBox="0 0 {B} {H}" role="img" class="verlauf" '
             f'aria-label="Gesamtleistung, Gesamtkosten und liquide Mittel je Monat">']
    # Gitter
    for k in range(5):
        y = oben + flaeche_h - flaeche_h * k / 4
        wert = hoch * k / 4
        teile.append(f'<line x1="{links}" y1="{y:.1f}" x2="{B - rechts}" y2="{y:.1f}" '
                     f'stroke="rgba(35,41,65,.09)" stroke-width="1"/>')
        teile.append(f'<text x="{links - 10}" y="{y + 4:.1f}" text-anchor="end" '
                     f'font-size="11" fill="#8A8FA3">{geld(wert)}</text>')
    # Berichtsmonat hinterlegen
    mx = links + spalte * M.aktiv
    teile.append(f'<rect x="{mx:.1f}" y="{oben - 8}" width="{spalte:.1f}" '
                 f'height="{flaeche_h + 8}" fill="rgba(35,41,65,.045)"/>')
    # Saeulen
    for i, monat in enumerate(M.monate):
        mitte = links + spalte * (i + .5)
        for wert, farbe, versatz in ((gesamt[i], '#404D97', -balken - 2),
                                     (kosten[i], '#B0842A', 2)):
            h = flaeche_h * (wert / hoch)
            teile.append(
                f'<rect x="{mitte + versatz:.1f}" y="{oben + flaeche_h - h:.1f}" '
                f'width="{balken:.1f}" height="{h:.1f}" rx="3" fill="{farbe}">'
                f'<title>{monat}: {geld(wert)}</title></rect>')
        teile.append(f'<text x="{mitte:.1f}" y="{H - 12}" text-anchor="middle" '
                     f'font-size="11.5" fill="#565D73">{KURZ[monat]}</text>')
    # Liquiditaetslinie
    if any(w is not None for w in liquide):
        punkte = [f'{links + spalte * (i + .5):.1f},'
                  f'{oben + flaeche_h - flaeche_h * (w / hoch):.1f}'
                  for i, w in enumerate(liquide) if w is not None]
        teile.append(f'<polyline points="{" ".join(punkte)}" fill="none" '
                     f'stroke="#232941" stroke-width="1.8" stroke-dasharray="4 4" '
                     f'stroke-linecap="round"/>')
        x, y = punkte[-1].split(',')
        teile.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#232941" '
                     f'stroke="#FBF8F2" stroke-width="2"/>')
    teile.append('</svg>')
    return ''.join(teile)


# -------------------------------------------------------------------- Raster
def ampelmarke(zl, i):
    a = M.ampel(zl, i)
    if not a:
        return ''
    farbe, erfuellung = a
    ziel = ('≥ ' if zl.richtung == 'hoeher' else '≤ ') + formatiere(zl.art, zl.ziel)
    return (f'<span class="marke {farbe}" title="Zielerreichung, Ziel {ziel}">'
            f'{erfuellung * 100:,.0f}'.replace(',', '.') + ' %</span>')


def raster():
    kopf = ''.join(
        f'<th class="num{" jetzt" if i == M.aktiv else ""}">{KURZ[m]} '
        f'{str(M.jahr)[-2:]}</th>' for i, m in enumerate(M.monate))
    bloecke = []
    for kennung, titel, zeilen in M.bloecke:
        koerper = []
        for zl in zeilen:
            klassen = ['zeile', f'ebene{zl.ebene}']
            attribute = ''
            if zl.gruppe:
                klassen.append('kind')
                klassen.append(f'zu-{zl.gruppe}')
                attribute = ' hidden'
            hat_kinder = any(k.gruppe == zl.schluessel for k in zeilen)
            knopf = (f'<button type="button" class="klapp" data-gruppe="{zl.schluessel}" '
                     f'aria-expanded="false"><span aria-hidden="true">›</span>'
                     f'<span class="nurlesen">Positionen anzeigen</span></button>'
                     if hat_kinder else '<span class="klapp leer"></span>')
            zellen = []
            for i, w in enumerate(zl.werte):
                text = formatiere(zl.art, w)
                if zl.vorzeichen < 0 and w:
                    text = '−' + text
                marke = ampelmarke(zl, i) if i == M.aktiv else ''
                zellen.append(
                    f'<td class="num{" jetzt" if i == M.aktiv else ""}'
                    f'{" minus" if zl.vorzeichen < 0 else ""}">{marke}{text}</td>')
            ziel = ('–' if zl.ziel is None else
                    ('≥ ' if zl.richtung == 'hoeher' else '≤ ')
                    + formatiere(zl.art, zl.ziel))
            koerper.append(
                f'<tr class="{" ".join(klassen)}"{attribute}>'
                f'<th scope="row" class="pos">{knopf}<span class="titel">{zl.titel}</span></th>'
                f'<td class="funkezelle">{sparkline(zl.werte)}</td>'
                f'{"".join(zellen)}'
                f'<td class="num ziel">{ziel}</td></tr>')
        bloecke.append(
            f'<tbody><tr class="blockkopf"><th scope="rowgroup" class="pos">{titel}</th>'
            f'<td colspan="{len(M.monate) + 2}"></td></tr>{"".join(koerper)}</tbody>')
    return (f'<div class="rasterrahmen"><table class="raster">'
            f'<thead><tr><th class="pos">Position</th><th class="funkezelle">Verlauf</th>'
            f'{kopf}<th class="num ziel">Ziel</th></tr></thead>'
            f'{"".join(bloecke)}</table></div>')


# ------------------------------------------------------------------ Kacheln
def kacheln():
    def delta(schluessel):
        w = M.zeile(schluessel).werte
        if M.aktiv == 0 or w[M.aktiv - 1] in (None, 0) or w[M.aktiv] is None:
            return ''
        v = (w[M.aktiv] - w[M.aktiv - 1]) / abs(w[M.aktiv - 1]) * 100
        pfeil = '▲' if v >= 0 else '▼'
        return (f'<span class="delta {"hoch" if v >= 0 else "runter"}">{pfeil} '
                + f'{abs(v):,.1f}'.replace('.', ',') + ' % zum Vormonat</span>')

    posten = [('umsatz', 'Umsatzerlöse', True), ('ebt', 'Ergebnis vor Steuern', True),
              ('db_quote', 'Deckungsbeitragsquote', False),
              ('liquide', 'Liquide Mittel', True), ('auslastung', 'Auslastung', False)]
    raus = []
    for schluessel, titel, mit_delta in posten:
        zl = M.zeile(schluessel)
        if zl is None:
            continue
        wert = zl.werte[M.aktiv]
        raus.append(
            f'<div class="kachel"><span class="kachel-titel">{titel}</span>'
            f'<b>{formatiere(zl.art, wert)}</b>'
            f'{ampelmarke(zl, M.aktiv)}{delta(schluessel) if mit_delta else ""}</div>')
    return f'<div class="kacheln">{"".join(raus)}</div>'


# ------------------------------------------------------------------- Huelle
def initialen(name):
    teile = [t for t in re.split(r'\s+', name) if t]
    return (teile[0][0] + (teile[1][0] if len(teile) > 1 else '')).upper()


NAV_MANDANT = [('auswertung', 'Auswertung', 'M8 3v10M4 7v6M12 6v7'),
               ('berichte', 'Berichte', 'M4 3h8v10H4z M6 6h4M6 9h4')]
NAV_ADMIN = [('mandanten', 'Mandanten', 'M3 13v-1a3 3 0 013-3h4a3 3 0 013 3v1M8 3a2.5 2.5 0 110 5 2.5 2.5 0 010-5'),
             ('zugaenge', 'Zugänge', 'M6 7V5a2 2 0 114 0v2M4 7h8v6H4z'),
             ('protokoll', 'Protokoll', 'M4 3h8v10H4z M6 6h4M6 9h3')]


def icon(pfad):
    return (f'<svg viewBox="0 0 16 16" aria-hidden="true" fill="none" '
            f'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
            f'stroke-linejoin="round"><path d="{pfad}"/></svg>')


def seitenleiste(rolle, aktiv):
    liq = M.zeile('liquide')
    wechsler = (
        f'<button type="button" class="wechsler" aria-haspopup="listbox">'
        f'<span class="signet">{initialen(M.firma)}</span>'
        f'<span class="wechsler-text"><b>{M.firma}</b>'
        f'<span>{M.berichtsmonat} {M.jahr}</span></span>'
        f'<span class="chevron" aria-hidden="true">⌄</span></button>')
    kennzahl = (f'<div class="seiten-kennzahl"><span>Liquide Mittel</span>'
                f'<b>{geld(liq.werte[M.aktiv])}</b></div>') if liq else ''

    punkte = []
    for kennung, titel, pfad in NAV_MANDANT:
        an = ' aria-current="page"' if kennung == aktiv else ''
        punkte.append(f'<a href="#" data-ziel="{rolle}-{kennung}"{an}>{icon(pfad)}{titel}</a>')
    admin = ''
    if rolle == 'admin':
        eintraege = []
        for kennung, titel, pfad in NAV_ADMIN:
            an = ' aria-current="page"' if kennung == aktiv else ''
            eintraege.append(
                f'<a href="#" data-ziel="admin-{kennung}"{an}>{icon(pfad)}{titel}</a>')
        admin = (f'<p class="nav-titel">Verwaltung</p><nav class="seiten-nav">'
                 f'{"".join(eintraege)}</nav>')

    person = ('Administrator', 'admin@vorschau.valtix') if rolle == 'admin' \
        else ('Ansprechpartner Muster', 'mandant@vorschau.valtix')
    return f'''<aside class="seitenleiste">
      <div class="seiten-marke">Valtix<span>Mandantenportal</span></div>
      {wechsler}{kennzahl}
      <p class="nav-titel">Auswertung</p>
      <nav class="seiten-nav">{"".join(punkte)}</nav>
      {admin}
      <div class="seiten-fuss">
        <div class="person"><span class="signet klein">{initialen(person[0])}</span>
          <span><b>{person[0]}</b><span>{person[1]}</span></span></div>
        <button type="button" class="knopf stumm schmal" data-ziel="anmelden">Abmelden</button>
      </div>
    </aside>'''


def werkzeugleiste(untertitel):
    monate = ''.join(
        f'<button type="button" class="monat{" an" if i == M.aktiv else ""}"'
        f'{"" if i == M.aktiv else " disabled"}>{KURZ[m]}</button>'
        for i, m in enumerate(M.monate))
    return f'''<div class="werkzeugleiste">
      <div class="wz-links">
        <span class="wz-titel">{untertitel}</span>
        <span class="wz-zeitraum">{KURZ[M.monate[0]]} {M.jahr} bis
          {KURZ[M.monate[-1]]} {M.jahr}</span>
      </div>
      <div class="monatsleiste" role="group" aria-label="Berichtsmonat">{monate}</div>
      <span class="wz-stand">Stand {M.berichtsmonat} {M.jahr}</span>
    </div>'''


def auswertung(rolle):
    return f'''{seitenleiste(rolle, 'auswertung')}
      <main class="flaeche">
        {werkzeugleiste('Auswertung')}
        <div class="inhalt">
          {kacheln()}
          <section class="karte">
            <div class="karten-kopf">
              <h2>Gesamtleistung, Kosten und Liquidität</h2>
              <div class="legende">
                <span><i style="background:#404D97"></i>Gesamtleistung</span>
                <span><i style="background:#B0842A"></i>Gesamtkosten</span>
                <span><i class="strich"></i>Liquide Mittel</span>
              </div>
            </div>
            <div class="bildrahmen">{verlaufsbild()}</div>
            <p class="hinweis">Auf schmalen Bildschirmen lässt sich das Diagramm
              seitlich schieben.</p>
          </section>
          <section class="karte flach">
            <div class="karten-kopf">
              <h2>Alle Positionen je Monat</h2>
              <p class="hinweis">Zeilen mit Pfeil lassen sich aufklappen. Die Prozentmarke
                im Berichtsmonat zeigt die Zielerreichung.</p>
            </div>
            {raster()}
          </section>
          <p class="quelle">Grundlage ist die ausgefüllte Eingabevorlage. Der vollständige
            Bericht als Dokument liegt unter
            <a href="{BERICHT}">Berichte</a>.</p>
        </div>
      </main>'''


def berichte(rolle):
    zeilen = ''.join(
        f'<tr><td>{z}</td><td>{d}</td><td class="num">'
        f'<a class="knopf stumm schmal" href="{BERICHT}">Ansehen</a></td></tr>'
        for z, d in [('Juli 2026', '06.08.2026'), ('Juni 2026', '07.07.2026'),
                     ('Mai 2026', '05.06.2026')])
    return f'''{seitenleiste(rolle, 'berichte')}
      <main class="flaeche">
        {werkzeugleiste('Berichte')}
        <div class="inhalt">
          <section class="karte flach">
            <div class="karten-kopf"><h2>Monatsberichte</h2>
              <p class="hinweis">Jeder Bericht bleibt in der Fassung erhalten, in der
                er eingestellt wurde.</p></div>
            <div class="rasterrahmen"><table class="liste"><thead><tr>
              <th>Zeitraum</th><th>Eingestellt</th><th class="num">&nbsp;</th>
            </tr></thead><tbody>{zeilen}</tbody></table></div>
          </section>
        </div>
      </main>'''


def admin_mandanten():
    zeilen = ''.join(
        f'<tr><td>{n}</td><td class="num">{b}</td><td>{s}</td>'
        f'<td class="num"><a class="knopf stumm schmal" href="#" '
        f'data-ziel="admin-auswertung">Öffnen</a></td></tr>'
        for n, b, s in [('Muster Lüftungstechnik GmbH', 3, 'Juli 2026'),
                        ('Beispiel Bau GmbH', 1, 'Juli 2026'),
                        ('Beispiel Handel e. K.', 2, 'Juli 2026')])
    return f'''{seitenleiste('admin', 'mandanten')}
      <main class="flaeche">
        {werkzeugleiste('Mandanten')}
        <div class="inhalt">
          <section class="karte flach">
            <div class="karten-kopf"><h2>Mandanten</h2></div>
            <div class="rasterrahmen"><table class="liste"><thead><tr>
              <th>Name</th><th class="num">Berichte</th><th>Letzter Bericht</th>
              <th class="num">&nbsp;</th></tr></thead><tbody>{zeilen}</tbody></table></div>
          </section>
          <section class="karte">
            <div class="karten-kopf"><h2>Bericht einstellen</h2></div>
            <form onsubmit="return false" class="formular">
              <label for="m">Mandant</label>
              <select id="m"><option>Muster Lüftungstechnik GmbH</option>
                <option>Beispiel Bau GmbH</option>
                <option>Beispiel Handel e. K.</option></select>
              <label for="d">Ausgefüllte Eingabevorlage (.xlsx)</label>
              <input id="d" type="file" accept=".xlsx" disabled>
              <button class="knopf" type="button" disabled>Hochladen und Bericht erzeugen</button>
              <p class="hinweis">In der Vorschau ohne Funktion. Es lässt sich nichts hochladen.</p>
            </form>
          </section>
        </div>
      </main>'''


def admin_zugaenge():
    zeilen = ''.join(
        f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td><span class="status {k}">{d}</span></td></tr>'
        for a, b, c, d, k in [
            ('Administrator', 'admin@vorschau.valtix', 'Administrator', 'aktiv', 'gut'),
            ('Ansprechpartner Muster', 'mandant@vorschau.valtix',
             'Muster Lüftungstechnik GmbH', 'aktiv', 'gut'),
            ('Ansprechpartner Beispiel Bau', 'bau@vorschau.valtix',
             'Beispiel Bau GmbH', 'Einladung offen', 'offen')])
    return f'''{seitenleiste('admin', 'zugaenge')}
      <main class="flaeche">
        {werkzeugleiste('Zugänge')}
        <div class="inhalt">
          <section class="karte flach">
            <div class="karten-kopf"><h2>Zugänge</h2></div>
            <div class="rasterrahmen"><table class="liste"><thead><tr>
              <th>Name</th><th>E-Mail</th><th>Zugehörigkeit</th><th>Status</th>
            </tr></thead><tbody>{zeilen}</tbody></table></div>
          </section>
          <section class="karte">
            <div class="karten-kopf"><h2>Zugang anlegen</h2></div>
            <form onsubmit="return false" class="formular">
              <label for="zn">Name</label><input id="zn" disabled>
              <label for="ze">E-Mail</label><input id="ze" type="email" disabled>
              <label for="zr">Rolle</label>
              <select id="zr" disabled><option>Mandant</option>
                <option>Administrator</option></select>
              <button class="knopf" type="button" disabled>Zugang anlegen</button>
              <p class="hinweis">Es wird kein Passwort vergeben. Die Person setzt es selbst
                über einen einmaligen Link.</p>
            </form>
          </section>
        </div>
      </main>'''


def admin_protokoll():
    zeilen = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>'
                     for a, b, c, d in [
        ('06.08.2026 09:14:02', 'anmeldung', 'mandant@vorschau.valtix', ''),
        ('06.08.2026 09:14:11', 'bericht_geoeffnet', 'mandant@vorschau.valtix', 'Juli 2026'),
        ('06.08.2026 08:52:40', 'bericht_eingestellt', 'admin@vorschau.valtix',
         'Muster Lüftungstechnik GmbH'),
        ('05.08.2026 17:30:19', 'zugang_angelegt', 'admin@vorschau.valtix',
         'bau@vorschau.valtix'),
        ('05.08.2026 17:29:03', 'anmeldung_fehlgeschlagen', '', 'unbekannte Kennung')])
    return f'''{seitenleiste('admin', 'protokoll')}
      <main class="flaeche">
        {werkzeugleiste('Protokoll')}
        <div class="inhalt">
          <section class="karte flach">
            <div class="karten-kopf"><h2>Letzte Ereignisse</h2>
              <p class="hinweis">Anmeldungen, Zugriffe auf Berichte und Änderungen an
                Zugängen werden festgehalten.</p></div>
            <div class="rasterrahmen"><table class="liste"><thead><tr>
              <th>Zeitpunkt</th><th>Ereignis</th><th>E-Mail</th><th>Detail</th>
            </tr></thead><tbody>{zeilen}</tbody></table></div>
          </section>
        </div>
      </main>'''


ANMELDEN = '''<div class="tuer">
  <div class="tuer-karte">
    <div class="seiten-marke gross">Valtix<span>Mandantenportal</span></div>
    <h1>Anmelden</h1>
    <p class="lead">Zugang erhalten Mandanten im Rahmen der monatlichen Betreuung.</p>
    <div class="zugang"><b>Zugangsdaten der Vorschau</b>
      <dl>
        <dt>Administrator</dt><dd><code>admin@vorschau.valtix</code></dd>
        <dt>Mandant</dt><dd><code>mandant@vorschau.valtix</code></dd>
        <dt>Passwort, beide</dt><dd><code>Vorschau2026</code></dd>
      </dl>
      <p>Geprüft wird nur im Browser. Es gibt keine Datenbank hinter dieser Seite
        und keinen Server, der etwas entgegennimmt.</p>
    </div>
    <div class="meldung fehler" id="fehler" hidden></div>
    <form id="form-anmelden" novalidate class="formular">
      <label for="e">E-Mail-Adresse</label>
      <input id="e" type="email" autocomplete="off" value="mandant@vorschau.valtix">
      <label for="p">Passwort</label>
      <input id="p" type="password" autocomplete="off" value="Vorschau2026">
      <button class="knopf" type="submit">Anmelden</button>
    </form>
  </div>
</div>'''

BILDSCHIRME = [
    ('anmelden', 'Anmeldung', ANMELDEN, False),
    ('mandant-auswertung', 'Mandantenansicht', auswertung('mandant'), True),
    ('mandant-berichte', 'Berichte', berichte('mandant'), True),
    ('admin-auswertung', 'Adminansicht', auswertung('admin'), True),
    ('admin-mandanten', 'Mandanten', admin_mandanten(), True),
    ('admin-zugaenge', 'Zugänge', admin_zugaenge(), True),
    ('admin-protokoll', 'Protokoll', admin_protokoll(), True),
]

BAND = '''<div class="band"><div class="band-innen">
  <b>Vorschau</b>
  <span>Attrappe zur Ansicht. Es wird nichts gespeichert und nichts übertragen.
    Firma und Zahlen sind erfunden.</span>
  <a href="index.html">Zurück zur Website</a>
</div></div>'''

SCHALTER = ('<div class="schalterband"><div class="band-innen">'
            '<span class="schalter-titel">Ansicht</span>'
            '<div class="schalter" role="group" aria-label="Ansicht wechseln">'
            + ''.join(f'<button type="button" data-ziel="{k}" aria-pressed="false">{t}</button>'
                      for k, t, _, _ in BILDSCHIRME)
            + '</div></div></div>')

CSS = '''
:root{
  --ink:#232941; --ink-soft:#565D73; --muted:#8A8FA3;
  --gold-deep:#7A6238; --cream:#F5EBD0; --bg:#FBF8F2; --flaeche:#F7F4EC;
  --serie-a:#404D97; --serie-b:#B0842A;
  --gruen:#0CA30C; --gelb:#FAB219; --rot:#D03B3B;
  --linie:rgba(35,41,65,.11); --linie-stark:rgba(35,41,65,.18);
  --r:14px; --schatten:0 8px 24px rgba(35,41,65,.07);
  --font:"Inter Tight",system-ui,-apple-system,"Segoe UI",sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);background:var(--bg);color:var(--ink);
     font-size:14px;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:var(--gold-deep)}
h1{font-size:1.55rem;font-weight:800;letter-spacing:-.03em;margin-bottom:4px}
h2{font-size:1.02rem;font-weight:700;letter-spacing:-.02em}
.nurlesen{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);
          white-space:nowrap}

/* Vorschauleisten, im echten Portal nicht vorhanden */
.band{background:var(--ink);color:#fff;font-size:.84rem;padding:11px 22px}
.band-innen{max-width:1420px;margin:0 auto;display:flex;gap:14px;
            align-items:baseline;flex-wrap:wrap}
.band b{font-weight:700}
.band span{color:rgba(255,255,255,.72)}
.band a{color:var(--cream)}
.schalterband{background:rgba(35,41,65,.05);border-bottom:1px solid var(--linie)}
.schalterband .band-innen{padding:9px 22px;align-items:center}
.schalter-titel{font-size:.68rem;text-transform:uppercase;letter-spacing:.11em;
                color:var(--ink-soft);font-weight:700}
.schalter{display:flex;gap:5px;flex-wrap:wrap}
.schalter button{font:inherit;font-size:.82rem;padding:6px 13px;border-radius:999px;
  border:1px solid var(--linie);background:#fff;color:var(--ink-soft);cursor:pointer}
.schalter button[aria-pressed=true]{background:var(--ink);color:#fff;border-color:var(--ink)}

/* Grundgeruest */
.bildschirm[hidden]{display:none}
.huelle{display:flex;min-height:calc(100vh - 96px);max-width:1460px;margin:0 auto;
        background:var(--bg)}

/* Seitenleiste */
.seitenleiste{width:236px;flex:0 0 236px;border-right:1px solid var(--linie);
  background:#fff;padding:18px 14px 16px;display:flex;flex-direction:column;gap:4px}
.seiten-marke{font-weight:800;letter-spacing:-.03em;font-size:1.02rem;padding:0 8px 14px}
.seiten-marke span{font-weight:500;color:var(--ink-soft);margin-left:7px;font-size:.86rem}
.wechsler{display:flex;align-items:center;gap:9px;width:100%;text-align:left;
  background:var(--flaeche);border:1px solid var(--linie);border-radius:12px;
  padding:9px 10px;font:inherit;cursor:pointer;color:inherit}
.signet{flex:0 0 30px;height:30px;border-radius:9px;background:var(--ink);color:#fff;
  display:grid;place-items:center;font-size:.74rem;font-weight:700;letter-spacing:.02em}
.signet.klein{flex-basis:26px;height:26px;font-size:.68rem;background:var(--gold-deep)}
.wechsler-text{min-width:0;flex:1}
.wechsler-text b{display:block;font-size:.82rem;font-weight:700;line-height:1.25;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.wechsler-text span{font-size:.74rem;color:var(--ink-soft)}
.chevron{color:var(--muted);font-size:.9rem}
.seiten-kennzahl{margin:10px 0 4px;padding:10px 12px;border-radius:12px;
  background:var(--cream);border:1px solid rgba(122,98,56,.24)}
.seiten-kennzahl span{display:block;font-size:.7rem;text-transform:uppercase;
  letter-spacing:.09em;color:var(--gold-deep);font-weight:700}
.seiten-kennzahl b{font-size:1.06rem;font-weight:800;letter-spacing:-.03em}
.nav-titel{font-size:.66rem;text-transform:uppercase;letter-spacing:.12em;
  color:var(--muted);font-weight:700;padding:14px 8px 6px}
.seiten-nav{display:flex;flex-direction:column;gap:1px}
.seiten-nav a{display:flex;align-items:center;gap:9px;padding:8px 10px;border-radius:10px;
  text-decoration:none;color:var(--ink-soft);font-size:.88rem}
.seiten-nav a svg{width:16px;height:16px;flex:0 0 16px;color:var(--muted)}
.seiten-nav a:hover{background:var(--flaeche);color:var(--ink)}
.seiten-nav a[aria-current]{background:var(--ink);color:#fff;font-weight:600}
.seiten-nav a[aria-current] svg{color:var(--cream)}
.seiten-fuss{margin-top:auto;padding-top:14px;border-top:1px solid var(--linie);
  display:flex;flex-direction:column;gap:9px}
.person{display:flex;align-items:center;gap:9px;min-width:0}
.person b{display:block;font-size:.79rem;font-weight:700;line-height:1.3}
.person span span{font-size:.72rem;color:var(--ink-soft);word-break:break-all}

/* Arbeitsflaeche */
.flaeche{flex:1;min-width:0;display:flex;flex-direction:column}
.werkzeugleiste{display:flex;align-items:center;gap:14px;flex-wrap:wrap;
  padding:12px 22px;border-bottom:1px solid var(--linie);background:rgba(255,255,255,.6)}
.wz-links{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.wz-titel{font-weight:700;letter-spacing:-.02em}
.wz-zeitraum{font-size:.8rem;color:var(--ink-soft)}
.monatsleiste{display:flex;gap:2px;margin-left:auto;background:var(--flaeche);
  border:1px solid var(--linie);border-radius:999px;padding:3px}
.monat{font:inherit;font-size:.78rem;padding:4px 11px;border-radius:999px;border:0;
  background:none;color:var(--muted);cursor:default}
.monat.an{background:#fff;color:var(--ink);font-weight:700;
  box-shadow:0 1px 3px rgba(35,41,65,.16)}
.wz-stand{font-size:.76rem;color:var(--ink-soft);white-space:nowrap}
.inhalt{padding:20px 22px 44px;display:flex;flex-direction:column;gap:16px}

/* Kacheln */
.kacheln{display:grid;grid-template-columns:repeat(5,1fr);gap:11px}
@media(max-width:1180px){.kacheln{grid-template-columns:repeat(3,1fr)}}
@media(max-width:720px){.kacheln{grid-template-columns:repeat(2,1fr)}}
@media(max-width:420px){.kacheln{grid-template-columns:1fr}}
.kachel{background:#fff;border:1px solid var(--linie);border-radius:var(--r);
  padding:13px 15px;box-shadow:var(--schatten)}
.kachel-titel{display:block;font-size:.74rem;color:var(--ink-soft);margin-bottom:3px}
.kachel b{display:block;font-size:1.24rem;font-weight:800;letter-spacing:-.035em;
  line-height:1.18}
.kachel .marke{margin:6px 6px 0 0}
.delta{display:inline-block;font-size:.74rem;font-weight:600;margin-top:5px}
.hoch{color:var(--gruen)} .runter{color:var(--rot)}

/* Karten */
.karte{background:#fff;border:1px solid var(--linie);border-radius:var(--r);
  padding:16px 18px;box-shadow:var(--schatten)}
.karte.flach{padding:16px 0 0}
.karte.flach .karten-kopf,.karte.flach .formular{padding:0 18px}
.karten-kopf{display:flex;justify-content:space-between;align-items:baseline;
  gap:14px;flex-wrap:wrap;margin-bottom:10px}
.hinweis{font-size:.78rem;color:var(--ink-soft)}
.quelle{font-size:.78rem;color:var(--ink-soft)}
.legende{display:flex;gap:14px;flex-wrap:wrap;font-size:.78rem;color:var(--ink-soft)}
.legende i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px}
.legende i.strich{width:16px;height:0;border-top:2px dashed var(--ink);border-radius:0;
  transform:translateY(-3px)}
.bildrahmen{overflow-x:auto;-webkit-overflow-scrolling:touch}
.verlauf{display:block;width:100%;height:auto;min-width:660px}

/* Raster */
.rasterrahmen{overflow-x:auto;-webkit-overflow-scrolling:touch;border-top:1px solid var(--linie)}
table{border-collapse:separate;border-spacing:0;width:100%;font-size:.83rem}
.raster{min-width:940px}
.liste{min-width:520px}
th,td{padding:7px 8px;text-align:left;border-bottom:1px solid var(--linie);
  white-space:nowrap;font-weight:400}
thead th{font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;
  color:var(--ink-soft);font-weight:700;background:var(--flaeche);
  position:sticky;top:0;z-index:3}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.pos{position:sticky;left:0;background:#fff;z-index:2;
  min-width:240px;max-width:284px;border-right:1px solid var(--linie)}
/* Lange Positionsbezeichnungen duerfen umbrechen, sonst schiebt eine einzige
   Zeile den Berichtsmonat aus dem Bild. */
.pos .titel{white-space:normal;display:inline-block;vertical-align:top;
  max-width:230px}
thead .pos{background:var(--flaeche);z-index:4}
.blockkopf th{font-size:.68rem;text-transform:uppercase;letter-spacing:.11em;
  color:var(--gold-deep);font-weight:700;background:var(--flaeche);padding-top:11px;
  padding-bottom:5px}
.blockkopf td{background:var(--flaeche)}
.zeile:hover td,.zeile:hover .pos{background:#FCFAF5}
.ebene0 .pos .titel,.ebene0 td{font-weight:700}
.ebene0 td{background:rgba(35,41,65,.028)}
.ebene0 .pos{background:rgba(252,250,245,1)}
.ebene2 .titel{color:var(--ink-soft);padding-left:16px}
.klapp{border:0;background:none;font:inherit;color:var(--muted);cursor:pointer;
  padding:0 6px 0 0;line-height:1}
.klapp span[aria-hidden]{display:inline-block;transition:transform .12s ease}
.klapp[aria-expanded=true] span[aria-hidden]{transform:rotate(90deg)}
.klapp.leer{display:inline-block;width:13px}
.funkezelle{width:54px;color:var(--muted);padding-right:0}
.funke{display:block}
td.minus{color:var(--gold-deep)}
td.jetzt,th.jetzt{background:rgba(35,41,65,.05)}
.ebene0 td.jetzt{background:rgba(35,41,65,.075)}
thead th.jetzt{color:var(--ink);border-bottom:2px solid var(--ink)}
td.ziel{color:var(--ink-soft)}
.marke{display:inline-block;font-size:.68rem;font-weight:700;padding:1px 6px;
  border-radius:999px;margin-right:7px;vertical-align:1px}
.marke.gruen{background:rgba(12,163,12,.12);color:#0A7A0A}
.marke.gelb{background:rgba(250,178,25,.18);color:#8A6100}
.marke.rot{background:rgba(208,59,59,.12);color:#A32C2C}
.status{font-size:.74rem;font-weight:600}
.status.gut{color:#0A7A0A} .status.offen{color:var(--gold-deep)}

/* Formulare und Knoepfe */
.formular{max-width:460px}
label{display:block;font-size:.8rem;font-weight:600;margin:12px 0 4px}
input,select{width:100%;font:inherit;font-size:.92rem;color:var(--ink);background:#fff;
  border:1px solid var(--linie-stark);border-radius:10px;padding:9px 12px;min-height:42px}
input:focus,select:focus{outline:none;border-color:var(--ink);
  box-shadow:0 0 0 3px rgba(35,41,65,.13)}
input:disabled,select:disabled{background:var(--flaeche);color:var(--muted)}
.knopf{display:inline-flex;align-items:center;justify-content:center;min-height:42px;
  padding:0 20px;border-radius:999px;border:0;font:inherit;font-weight:600;cursor:pointer;
  background:linear-gradient(180deg,#232941,#171B2C);color:#fff;text-decoration:none;
  box-shadow:0 6px 16px rgba(35,41,65,.24);margin-top:16px}
.knopf:disabled{opacity:.5;box-shadow:none;cursor:not-allowed}
.knopf.stumm{background:#fff;color:var(--ink);border:1px solid var(--linie);
  box-shadow:none}
.knopf.schmal{min-height:32px;padding:0 13px;font-size:.8rem;margin:0}
.meldung{padding:10px 14px;border-radius:10px;font-size:.86rem;margin-bottom:12px}
.fehler{background:#FDECEC;color:#8B1F1F}

/* Anmeldung */
.tuer{padding:6vh 22px 60px;min-height:60vh}
.tuer-karte{width:100%;max-width:430px;margin:0 auto;background:#fff;border:1px solid var(--linie);
  border-radius:var(--r);padding:26px;box-shadow:var(--schatten)}
.tuer-karte .seiten-marke{padding:0 0 16px}
.lead{color:var(--ink-soft);margin-bottom:16px}
.zugang{background:var(--cream);border:1px solid rgba(122,98,56,.26);border-radius:11px;
  padding:13px 15px;margin-bottom:14px;font-size:.85rem}
.zugang b{display:block;font-size:.68rem;text-transform:uppercase;letter-spacing:.11em;
  color:var(--gold-deep);margin-bottom:7px}
.zugang dl{display:grid;grid-template-columns:auto 1fr;gap:3px 12px;align-items:baseline}
.zugang dt{color:var(--ink-soft)}
.zugang dd{min-width:0;overflow-wrap:anywhere}
.zugang p{margin-top:8px;color:var(--ink-soft);font-size:.79rem}
code{background:rgba(35,41,65,.08);padding:1px 5px;border-radius:5px;font-size:.83rem}
.fuss{max-width:1420px;margin:0 auto;padding:14px 22px 34px;font-size:.76rem;
      color:var(--ink-soft)}

@media(max-width:900px){
  .huelle{flex-direction:column}
  .seitenleiste{width:auto;flex:none;border-right:0;border-bottom:1px solid var(--linie);
    padding:14px}
  .seiten-nav{flex-direction:row;flex-wrap:wrap}
  .seiten-fuss{flex-direction:row;align-items:center;justify-content:space-between}
  .werkzeugleiste{padding:11px 14px}
  .monatsleiste{margin-left:0;overflow-x:auto}
  .inhalt{padding:14px 14px 36px}
  .karte.flach .karten-kopf,.karte.flach .formular{padding:0 14px}
  .pos{min-width:200px}
  .tuer{padding:4vh 14px 44px}
  .tuer-karte{padding:20px}
}
'''

JS = '''
(function(){
  var zeigen = function(id){
    document.querySelectorAll('.bildschirm').forEach(function(s){
      s.hidden = (s.id !== 'bs-' + id);
    });
    document.querySelectorAll('.schalter button').forEach(function(b){
      b.setAttribute('aria-pressed', String(b.dataset.ziel === id));
    });
    window.scrollTo(0,0);
    // Das Raster oeffnet beim Berichtsmonat, nicht beim Januar. Sonst muesste
    // man auf schmalen Bildschirmen erst nach rechts schieben.
    document.querySelectorAll('#bs-' + id + ' .rasterrahmen').forEach(function(r){
      var jetzt = r.querySelector('thead th.jetzt');
      if (!jetzt) return;
      var ziel = jetzt.offsetLeft + jetzt.offsetWidth - r.clientWidth + 110;
      r.scrollLeft = Math.max(0, ziel);
    });
    if (history.replaceState) history.replaceState(null, '', '#ansicht-' + id);
  };
  document.addEventListener('click', function(e){
    var klapp = e.target.closest('.klapp[data-gruppe]');
    if (klapp) {
      var auf = klapp.getAttribute('aria-expanded') !== 'true';
      klapp.setAttribute('aria-expanded', String(auf));
      klapp.closest('table').querySelectorAll('.zu-' + klapp.dataset.gruppe)
        .forEach(function(tr){ tr.hidden = !auf; });
      return;
    }
    var ziel = e.target.closest('[data-ziel]');
    if (!ziel) return;
    e.preventDefault();
    zeigen(ziel.dataset.ziel);
  });
  var f = document.getElementById('form-anmelden');
  f.addEventListener('submit', function(e){
    e.preventDefault();
    var mail = document.getElementById('e').value.trim().toLowerCase();
    var pw = document.getElementById('p').value;
    var box = document.getElementById('fehler');
    if (pw === 'Vorschau2026' && mail === 'admin@vorschau.valtix') {
      box.hidden = true; zeigen('admin-auswertung'); return;
    }
    if (pw === 'Vorschau2026' && mail === 'mandant@vorschau.valtix') {
      box.hidden = true; zeigen('mandant-auswertung'); return;
    }
    box.textContent = 'E-Mail-Adresse oder Passwort stimmen nicht. In der Vorschau '
      + 'gelten nur die oben genannten Zugangsdaten.';
    box.hidden = false;
  });
  var start = location.hash.replace('#ansicht-','').replace('#','');
  zeigen(document.getElementById('bs-' + start) ? start : 'anmelden');
})();
'''

abschnitte = ''.join(
    f'<section class="bildschirm" id="bs-{kennung}" hidden>'
    + (f'<div class="huelle">{inhalt}</div>' if huelle else inhalt)
    + '</section>'
    for kennung, _, inhalt, huelle in BILDSCHIRME)

html = f'''<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Vorschau Mandantenportal · Valtix Financial Management</title>
<link rel="icon" href="favicon.ico" sizes="any">
<style>{CSS}</style></head><body>
{BAND}
{SCHALTER}
{abschnitte}
<div class="fuss">Valtix Financial Management · Luca Sparhuber und Sharif Ibrahim GbR,
Leipzig · Diese Seite dient allein der Ansicht. Sie verarbeitet keine personenbezogenen
Daten, setzt keine Cookies und sendet nichts an einen Server.</div>
<script>{JS}</script>
</body></html>'''

ziel = os.path.join(ROOT, 'portal-vorschau.html')
open(ziel, 'w').write(html)
print('geschrieben:', ziel, len(html), 'Zeichen,', len(M.monate), 'Monate')
if M.ohne_zuordnung:
    print('Zielzeilen ohne passende Kennzahl:', M.ohne_zuordnung)
