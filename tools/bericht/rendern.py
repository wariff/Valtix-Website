#!/usr/bin/env python3
"""Erzeugt den Monatsbericht als HTML im Valtix-Design.

    python3 tools/bericht/rendern.py <eingabe.xlsx> [ausgabe.html]
"""
import os, sys
from html import escape
from datetime import date

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from modell import Bericht                      # noqa: E402
import diagramme as dg                          # noqa: E402

CSS = '''
:root{
  --ink:#232941; --ink-soft:#565D73; --muted:#8A8FA3;
  --gold-deep:#7A6238; --cream:#F5EBD0; --bg:#FBF8F2;
  --serie-a:#404D97; --serie-b:#B0842A;
  --gruen:#0CA30C; --gelb:#FAB219; --rot:#D03B3B;
  --hairline:rgba(35,41,65,.12);
  --karte:#fff; --schatten:0 10px 30px rgba(35,41,65,.08);
  --r:16px;
  --font:"Inter Tight",system-ui,-apple-system,"Segoe UI",sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);background:var(--bg);color:var(--ink);
     font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}
.blatt{max-width:960px;margin:0 auto;padding:40px 28px 72px}
@media(max-width:640px){.blatt{padding:24px 16px 48px}}
h1,h2,h3{font-weight:800;letter-spacing:-.03em;line-height:1.12}
h1{font-size:clamp(1.7rem,4vw,2.3rem);margin-bottom:6px}
h2{font-size:1.32rem;margin:44px 0 6px}
h3{font-size:1.02rem;margin:22px 0 8px;letter-spacing:-.02em}
p{margin-bottom:12px}
.kopf{border-bottom:1px solid var(--hairline);padding-bottom:22px;margin-bottom:8px}
.vertraulich{font-size:.72rem;font-weight:700;letter-spacing:.14em;
             text-transform:uppercase;color:var(--gold-deep);margin-bottom:14px}
.kopf .meta{color:var(--ink-soft);font-size:.95rem}
.karte{background:var(--karte);border:1px solid var(--hairline);border-radius:var(--r);
       padding:22px 24px;box-shadow:var(--schatten);margin-top:14px}
.kacheln{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-top:20px}
@media(max-width:860px){.kacheln{grid-template-columns:repeat(2,1fr)}}
@media(max-width:420px){.kacheln{grid-template-columns:1fr}}
.kachel{background:var(--karte);border:1px solid var(--hairline);border-radius:var(--r);
        padding:16px 18px;box-shadow:var(--schatten)}
.kachel b{display:block;font-size:1.28rem;font-weight:800;letter-spacing:-.035em;line-height:1.15}
.kachel span{display:block;font-size:.8rem;color:var(--ink-soft);margin-top:4px}
.kachel .delta{font-size:.78rem;font-weight:600;margin-top:6px}
.hoch{color:var(--gruen)} .runter{color:var(--rot)}
svg{display:block;width:100%;height:auto;overflow:visible}
.diagramm{overflow-x:auto;-webkit-overflow-scrolling:touch}
@media(max-width:760px){
  /* Beschriftungen bleiben lesbar, das Diagramm scrollt stattdessen */
  .diagramm svg{min-width:640px}
  .diagramm-hinweis{display:block}
}
.diagramm-hinweis{display:none;font-size:.8rem;color:var(--ink-soft);margin-top:8px}
.tabelle-rahmen{overflow-x:auto;margin:14px 0 0}
table{border-collapse:collapse;width:100%;min-width:460px;font-size:.9rem}
th,td{padding:8px 12px;text-align:left;border-bottom:1px solid var(--hairline);white-space:nowrap}
th{font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;
   color:var(--ink-soft);font-weight:600}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
tr.summe td{font-weight:700;background:rgba(35,41,65,.035)}
tr:last-child td{border-bottom:none}
.punkt{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;
       vertical-align:baseline}
.legende{display:flex;gap:18px;flex-wrap:wrap;font-size:.82rem;color:var(--ink-soft);margin-top:10px}
.legende i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:6px}
.hinweis{font-size:.82rem;color:var(--ink-soft);margin-top:10px}
.fuss{margin-top:52px;padding-top:20px;border-top:1px solid var(--hairline);
      font-size:.82rem;color:var(--ink-soft)}
@media print{
  body{background:#fff}
  .karte,.kachel{box-shadow:none}
  h2{break-after:avoid} .karte{break-inside:avoid}
}
'''


def kachel(wert, label, delta=None):
    d = ''
    if delta is not None:
        klasse = 'hoch' if delta >= 0 else 'runter'
        d = f'<span class="delta {klasse}">{"+" if delta>=0 else "−"}{dg.proz(abs(delta))} zum Vormonat</span>'
    return f'<div class="kachel"><b>{wert}</b><span>{escape(label)}</span>{d}</div>'


def zeile(name, wert, num=True, summe=False):
    k = ' class="summe"' if summe else ''
    return f'<tr{k}><td>{escape(name)}</td><td class="num">{wert}</td></tr>'


def bauen(pfad_in, pfad_out=None):
    b = Bericht(pfad_in)
    m, vm = b.m, b.vormonat
    s = b.stamm
    einheit_pl = s['einheit_plural']
    be = b.break_even()
    t = []

    def d(neu, alt):
        return (neu - alt) / abs(alt) * 100 if alt else None

    # ---------- Kopf ----------
    t.append(f'''<div class="kopf">
      <p class="vertraulich">Vertraulich</p>
      <h1>Finanzielle Kennzahlenanalyse</h1>
      <p class="meta">{escape(s['firma'])} · {escape(str(b.aktuell))} {escape(str(s['jahr']))}
      {' · ' + escape(s['branche']) if s['branche'] else ''}</p>
    </div>''')

    # ---------- 1 Cockpit ----------
    t.append('<h2>1 &nbsp;Cockpit</h2>')
    t.append('<div class="kacheln">')
    t.append(kachel(dg.eur(m['umsatz'], 2), 'Umsatzerlöse', d(m['umsatz'], vm['umsatz']) if vm else None))
    t.append(kachel(dg.eur(m['ebt'], 2), f"EBT · Marge {dg.proz(m['ebt_marge'])}",
                    d(m['ebt'], vm['ebt']) if vm and vm['ebt'] else None))
    t.append(kachel(dg.eur(m['db'], 2), f"Deckungsbeitrag · {dg.proz(m['db_quote'])}"))
    if m['auslastung'] is not None:
        t.append(kachel(dg.proz(m['auslastung']), b.op_titel.get('menge', 'Auslastung')
                                and 'Auslastung'))
    if m['op'].get('auftragsbestand'):
        t.append(kachel(dg.eur(m['op']['auftragsbestand']), 'Auftragsbestand'))
    t.append('</div>')

    # Ergebnisbrücke
    schritte = [('Umsatzerlöse', m['umsatz'], 'start')]
    if m['sonstige']:
        schritte.append(('Sonstige Erträge', m['sonstige'], 'auf'))
    schritte += [('Variable Kosten', -m['var_summe'], 'ab'),
                 ('Fixkosten', -m['fix_summe'], 'ab'),
                 ('Abschreibungen', -m['afa'], 'ab')]
    if m['zins']:
        schritte.append(('Zinsergebnis', -m['zins'], 'ab'))
    schritte.append(('EBT', m['ebt'], 'ende'))
    t.append('<h3>Ergebnisbrücke: von den Umsatzerlösen zum EBT</h3>')
    t.append('<div class="karte"><div class="diagramm">' + dg.ergebnisbruecke(schritte) + '</div>' +
             '<p class="diagramm-hinweis">Das Diagramm lässt sich seitlich scrollen.</p>' +
             '<div class="legende">'
             f'<span><i style="background:{dg.SERIE_A}"></i>Zwischen- und Endgrößen</span>'
             f'<span><i style="background:{dg.SERIE_B}"></i>Zu- und Abgänge</span></div></div>')

    # Kostenstruktur
    posten = list(m['variabel'].items()) + list(m['fix'].items()) + [('Abschreibungen', m['afa'])]
    gesamt = m['var_summe'] + m['fix_summe'] + m['afa']
    t.append('<h3>Kostenstruktur</h3>')
    t.append('<div class="karte"><div class="diagramm">' + dg.kostenstruktur(posten, gesamt) + '</div>' +
             '<p class="diagramm-hinweis">Das Diagramm lässt sich seitlich scrollen.</p>' +
             f'<p class="hinweis">Gesamtkosten {dg.eur(gesamt, 2)}, '
             f'Anteile bezogen auf diese Summe.</p></div>')

    # GuV-Detail
    t.append('<h3>Gewinn- und Verlustrechnung im Detail</h3>')
    r = ['<div class="tabelle-rahmen"><table><thead><tr><th>Position</th>'
         f'<th class="num">{escape(str(b.aktuell))} {escape(str(s["jahr"]))}</th></tr></thead><tbody>']
    for name, wert in m['erloese'].items():
        if wert: r.append(zeile(name, dg.eur(wert, 2)))
    r.append(zeile('Umsatzerlöse', dg.eur(m['umsatz'], 2), summe=True))
    if m['sonstige']:
        r.append(zeile('Sonstige betriebliche Erträge', dg.eur(m['sonstige'], 2)))
        r.append(zeile('Gesamtleistung', dg.eur(m['gesamtleistung'], 2), summe=True))
    for name, wert in m['variabel'].items():
        if wert: r.append(zeile('− ' + name, dg.eur(wert, 2)))
    r.append(zeile(f"Deckungsbeitrag  ·  Quote {dg.proz(m['db_quote'])}", dg.eur(m['db'], 2), summe=True))
    for name, wert in m['fix'].items():
        if wert: r.append(zeile('− ' + name, dg.eur(wert, 2)))
    r.append(zeile('EBITDA', dg.eur(m['ebitda'], 2), summe=True))
    if m['afa']: r.append(zeile('− Abschreibungen', dg.eur(m['afa'], 2)))
    r.append(zeile('EBIT', dg.eur(m['ebit'], 2), summe=True))
    if m['zins']: r.append(zeile('− Zinsergebnis', dg.eur(m['zins'], 2)))
    r.append(zeile(f"EBT  ·  Marge {dg.proz(m['ebt_marge'])}", dg.eur(m['ebt'], 2), summe=True))
    r.append('</tbody></table></div>')
    t.append(''.join(r))

    # ---------- 2 Verlauf ----------
    if len(b.monate) >= 2:
        namen = [x['monat'] for x in b.monate]
        t.append('<h2>2 &nbsp;Verlauf im Berichtsjahr</h2>')
        t.append('<h3>Umsatzerlöse je Monat</h3>')
        t.append('<div class="karte"><div class="diagramm">'
                 + dg.verlauf(namen, [x['umsatz'] for x in b.monate],
                              'Umsatzerlöse je Monat', lambda v: dg.eur(v))
                 + '</div><p class="diagramm-hinweis">Das Diagramm lässt sich seitlich scrollen.</p></div>')
        t.append('<h3>Ergebnis vor Steuern je Monat</h3>')
        t.append('<div class="karte"><div class="diagramm">'
                 + dg.verlauf(namen, [x['ebt'] for x in b.monate],
                              'EBT je Monat', lambda v: dg.eur(v), negativ_ok=True)
                 + '</div><p class="hinweis">Balken unterhalb der Nulllinie kennzeichnen ein '
                   'negatives Monatsergebnis. Auf schmalen Bildschirmen lässt sich das Diagramm '
                   'seitlich scrollen.</p></div>')
        kopf = ''.join(f'<th class="num">{x[:3]}</th>' for x in namen)
        rr = [f'<div class="tabelle-rahmen"><table><thead><tr><th>Kennzahl</th>{kopf}</tr></thead><tbody>']
        for label, hol, fmt in [
                ('Umsatzerlöse', lambda x: x['umsatz'], lambda v: dg.eur(v)),
                ('Deckungsbeitrag', lambda x: x['db'], lambda v: dg.eur(v)),
                ('DB-Quote', lambda x: x['db_quote'], lambda v: dg.proz(v)),
                ('Fixkosten inkl. AfA', lambda x: x['fix_inkl_afa'], lambda v: dg.eur(v)),
                ('EBT', lambda x: x['ebt'], lambda v: dg.eur(v)),
                ('EBT-Marge', lambda x: x['ebt_marge'], lambda v: dg.proz(v))]:
            zellen = ''.join(f'<td class="num">{fmt(hol(x))}</td>' for x in b.monate)
            rr.append(f'<tr><td>{label}</td>{zellen}</tr>')
        rr.append('</tbody></table></div>')
        t.append(''.join(rr))

    # ---------- 3 Vormonatsvergleich ----------
    if vm:
        t.append('<h2>3 &nbsp;Vormonatsvergleich</h2>')
        rr = ['<div class="tabelle-rahmen"><table><thead><tr><th>Kennzahl</th>'
              f'<th class="num">{vm["monat"][:3]}</th><th class="num">{m["monat"][:3]}</th>'
              '<th class="num">Δ absolut</th><th class="num">Δ in %</th></tr></thead><tbody>']
        for label, sch, fmt, ist_proz in [
                ('Umsatzerlöse', 'umsatz', lambda v: dg.eur(v, 2), False),
                ('Deckungsbeitrag', 'db', lambda v: dg.eur(v, 2), False),
                ('Fixkosten inkl. AfA', 'fix_inkl_afa', lambda v: dg.eur(v, 2), False),
                ('EBITDA', 'ebitda', lambda v: dg.eur(v, 2), False),
                ('EBT', 'ebt', lambda v: dg.eur(v, 2), False),
                ('Auslastung', 'auslastung', lambda v: dg.proz(v), True)]:
            a, n = vm[sch], m[sch]
            if a is None or n is None or (not a and not n): continue
            diff = n - a
            dtxt = (f'{"+" if diff>=0 else "−"}{dg.zahl(abs(diff),1)} %-Pkte.' if ist_proz
                    else f'{"+" if diff>=0 else "−"}{dg.eur(abs(diff), 2)}')
            ptxt = f'{"+" if diff>=0 else "−"}{dg.proz(abs(diff/a*100))}' if a else 'n. a.'
            rr.append(f'<tr><td>{label}</td><td class="num">{fmt(a)}</td>'
                      f'<td class="num">{fmt(n)}</td><td class="num">{dtxt}</td>'
                      f'<td class="num">{ptxt}</td></tr>')
        rr.append('</tbody></table></div>')
        t.append(''.join(rr))

    # ---------- 4 Ampel ----------
    if b.ziele:
        t.append('<h2>4 &nbsp;Kennzahlen im Ampelprinzip</h2>')
        t.append('<p>Grün bedeutet Ziel erreicht, Gelb bis zehn Prozent verfehlt, '
                 'Rot mehr als zehn Prozent verfehlt.</p>')
        rr = ['<div class="tabelle-rahmen"><table><thead><tr><th>Kennzahl</th>'
              f'<th class="num">Ist {m["monat"][:3]}</th><th class="num">Ziel</th>'
              '<th>Bewertung</th></tr></thead><tbody>']
        wort = {'gruen': 'Grün', 'gelb': 'Gelb', 'rot': 'Rot', 'grau': 'ohne Ziel'}
        fehlend = []
        for z in b.ziele:
            ist = b.ist_wert(z['quelle'])
            if ist is None:
                fehlend.append(f"{z['name']} (Blatt 5, Zeile {z['zeile']})")
                continue
            fmt = {'eur': lambda v: dg.eur(v, 2), 'proz': lambda v: dg.proz(v),
                   'tage': lambda v: dg.zahl(v, 0, 'Tage'), 'zahl': lambda v: dg.zahl(v, 0)}[z['einheit']]
            a = b.ampel(ist, z['ziel'], z['richtung'])
            pfeil = '≥' if z['richtung'] == 'hoch' else '≤'
            rr.append(f'<tr><td>{escape(z["name"])}</td><td class="num">{fmt(ist)}</td>'
                      f'<td class="num">{pfeil} {fmt(z["ziel"])}</td>'
                      f'<td><span class="punkt" style="background:{dg.STATUS[a]}"></span>{wort[a]}</td></tr>')
        rr.append('</tbody></table></div>')
        t.append(''.join(rr))
        if fehlend:
            t.append('<p class="hinweis">Für diese Zielwerte wurden keine Ausgangszahlen '
                     'übermittelt, sie bleiben daher unbewertet: '
                     + escape('; '.join(fehlend)) + '.</p>')

    # ---------- 5 Break-even ----------
    if be:
        eh = escape(s['einheit'])
        t.append('<h2>5 &nbsp;Gewinnschwelle</h2>')
        t.append(f'<p>Bezugsgröße ist die Leistungseinheit „{eh}". Der Deckungsbeitrag je '
                 f'Einheit wird ohne die sonstigen betrieblichen Erträge gerechnet, weil diese '
                 f'nicht an der Leistungsmenge hängen.</p>')
        t.append('<div class="karte"><div class="diagramm">'
                 + dg.break_even_bild(dict(be, fix_inkl_afa=m['fix_inkl_afa']), eh) + '</div>' +
                 '<p class="diagramm-hinweis">Das Diagramm lässt sich seitlich scrollen.</p>' +
                 f'<div class="legende">'
                 f'<span><i style="background:{dg.SERIE_A}"></i>Erlös</span>'
                 f'<span><i style="background:{dg.SERIE_B}"></i>Gesamtkosten</span></div></div>')
        rr = ['<div class="tabelle-rahmen"><table><thead><tr><th>Größe</th>'
              '<th class="num">Wert</th></tr></thead><tbody>']
        for label, wert in [
            (f'Umsatz je {eh}', dg.eur(be['umsatz_je_einheit'], 2)),
            (f'Deckungsbeitrag je {eh}', dg.eur(be['db_je_einheit'], 2)),
            ('Fixkosten inkl. Abschreibungen', dg.eur(m['fix_inkl_afa'], 2)),
            ('Gewinnschwelle', f"{dg.zahl(be['schwelle'],2,einheit_pl)} · {dg.eur(be['schwelle_umsatz'],2)}"),
            ('Cash-Gewinnschwelle ohne Abschreibungen',
             f"{dg.zahl(be['cash_schwelle'],2,einheit_pl)} · {dg.eur(be['cash_umsatz'],2)}"),
            (f'Ist im {m["monat"]}', dg.zahl(be['ist'], 2, einheit_pl)),
            ('Sicherheitsabstand', f"{dg.zahl(be['abstand'],2,einheit_pl)} · {dg.proz(be['abstand_proz'])}"),
            ('Umsatzpuffer bis zur Gewinnschwelle', dg.eur(be['puffer_umsatz'], 2)),
        ]:
            rr.append(zeile(label, wert))
        rr.append('</tbody></table></div>')
        t.append(''.join(rr))

    # ---------- Fuß ----------
    t.append(f'''<div class="fuss">
      <p>Erstellt am {date.today().strftime('%d.%m.%Y')} von Valtix Financial Management,
      Luca Sparhuber und Sharif Ibrahim GbR, Leipzig. Grundlage sind die von
      {escape(s['firma'])} übermittelten Zahlen; eine Prüfung dieser Angaben erfolgt nicht.</p>
      <p>Dieser Bericht ist eine betriebswirtschaftliche Auswertung. Er ersetzt weder
      Jahresabschluss noch Steuer- oder Rechtsberatung.</p>
    </div>''')

    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Kennzahlenanalyse {escape(s['firma'])} · {escape(str(b.aktuell))} {escape(str(s['jahr']))}</title>
<style>{CSS}</style>
</head>
<body><div class="blatt">{''.join(t)}</div></body>
</html>
'''
    ziel = pfad_out or os.path.splitext(pfad_in)[0] + '.html'
    with open(ziel, 'w') as f:
        f.write(html)
    return ziel, b


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Aufruf: rendern.py <eingabe.xlsx> [ausgabe.html]')
    ziel, b = bauen(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"{b.stamm['firma']} · {b.aktuell} · {len(b.monate)} Monate  ->  {ziel}")
    for h in getattr(b, 'hinweise', []):
        print('  Hinweis:', h)
